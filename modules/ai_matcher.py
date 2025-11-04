import os
import json
import pandas as pd
import fitz  # PyMuPDF
from tqdm import tqdm
from openai import OpenAI
from thinkcerca_tool.config import FILES, OUTPUT_FILE, MODEL_NAME, OPENAI_API_KEY
from thinkcerca_tool.modules.join_standards import join_module_standards

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from datetime import datetime

def extract_pdf_activities(pdf_path: str = FILES["STUDENT_GUIDE"]) -> list[dict]:
  """
  Extracts text chunks from the Student Guide PDF.
  Each top-level heading (MODULE sections or ALL-CAPS titles) is treated as an 'activity'.
  Returns a list of {page_num, heading, text}.
  """
  doc = fitz.open(pdf_path)
  activities = []

  for page_idx, page in enumerate(doc):
      text = page.get_text("text")
      # Very simple heuristic: treat double newlines or 'MODULE' markers as splits
      chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 60]
      for chunk in chunks:
          first_line = chunk.split("\n")[0][:80]
          activities.append(
              {"page": page_idx + 1, "heading": first_line, "text": chunk}
          )

  return activities


def match_standards_with_ai(
  activities: list[dict],
  standards_df: pd.DataFrame,
  model: str = MODEL_NAME,
  top_k: int = 2,
) -> pd.DataFrame:
  """
  Send each activity to GPT with candidate standards.
  Handles imperfect JSON by fallback parsing.
  """
  client = OpenAI(api_key=OPENAI_API_KEY)
  results = []

  # Prepare standards reference once
  standards_text = "\n".join(
      f"{row.Standard_Code}: {row.Description}" for _, row in standards_df.iterrows()
  )

  for act in tqdm(activities, desc="AI Matching"):
      prompt = f"""
        You are aligning student activities with educational standards.

        Activity:
        \"\"\"{act['text'][:2000]}\"\"\"

        Candidate Standards:
        {standards_text}

        Pick the {top_k} most relevant standard codes.
        Return valid JSON only:
        {{
          "activity": "{act['heading']}",
          "page": {act['page']},
          "matches": [
            {{"code": "<standard code>", "reason": "<why this matches>"}}
          ]
        }}
        """
      try:
          resp = client.chat.completions.create(
              model=model,
              messages=[{"role": "user", "content": prompt}],
              temperature=0.2,
          )
          content = resp.choices[0].message.content.strip()

          # --- Try parsing JSON directly ---
          try:
              data = json.loads(content)
          except json.JSONDecodeError:
              # --- Fallback: extract JSON substring if GPT wrapped in prose ---
              import re
              match = re.search(r"\{.*\}", content, re.DOTALL)
              if match:
                  data = json.loads(match.group(0))
              else:
                  print(f"⚠️ Could not parse GPT output on page {act['page']}: {content[:120]}")
                  continue

          for m in data.get("matches", []):
              results.append(
                  {
                      "Page": act["page"],
                      "Activity": act["heading"],
                      "Standard_Code": m.get("code", "").strip(),
                      "Reason": m.get("reason", "").strip(),
                  }
              )

      except Exception as e:
          print(f"⚠️ Error on page {act['page']}: {e}")

  return pd.DataFrame(results)


def run_ai_mapping_pipeline():
  """End-to-end pipeline that outputs a clean, sample-aligned Excel workbook with summary."""
  print("🔍 Loading module-specific standards...")
  standards_df = join_module_standards()

  print("📘 Extracting student-guide activities...")
  activities = extract_pdf_activities()

  print("🤖 Running OpenAI LLM matching...")
  matches_df = match_standards_with_ai(activities, standards_df)

  if matches_df.empty:
      print("⚠️ No matches returned — check AI output.")
      return

  # --- Build formatted final sheet ---
  print("🧾 Formatting final workbook...")

  # Static identifiers for this test module
  matches_df["Grade"] = 8
  matches_df["Unit"] = 1
  matches_df["Module"] = 2
  matches_df["Slide URL"] = ""

  # Rename Reason → Slide Summary and keep Activity column visible
  matches_df.rename(columns={
      "Reason": "Slide Summary / Extracted Text",
      "Standard_Code": "Standard Code",
      "Activity": "Activity"
  }, inplace=True)

  # Merge in descriptions
  merged = pd.merge(
      matches_df,
      standards_df[["Standard_Code", "Description"]],
      left_on="Standard Code",
      right_on="Standard_Code",
      how="left"
  )
  merged.drop(columns=["Standard_Code"], inplace=True)
  merged.rename(columns={"Description": "Standard Description"}, inplace=True)

  # Reorder columns to match sample
  merged = merged[[
      "Grade", "Unit", "Module", "Activity", "Slide URL",
      "Slide Summary / Extracted Text", "Standard Code", "Standard Description"
  ]]

  output_path = OUTPUT_FILE.replace(".xlsx", "_AI_Final.xlsx")

  # === Write data + summary ===
  with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
      merged.to_excel(writer, index=False, sheet_name="Mapped Standards")

      # Create summary data
      summary_data = {
          "Project": ["ThinkCERCA AI Standards Alignment"],
          "Grade": ["8"],
          "Unit": ["1"],
          "Module": ["2 – 'I Am the Greatest'"],
          "Date": [datetime.now().strftime("%Y-%m-%d")],
          "Total Unique Activities": [merged["Activity"].nunique()],
          "Total Unique Standards": [merged["Standard Code"].nunique()],
          "Total Activity–Standard Pairs": [len(merged)],
          "Model Used": [MODEL_NAME],
          "Notes": [
              "Each row represents one Activity → Standard mapping. Some activities appear multiple times because they align with 2 standards."
          ],
      }

      pd.DataFrame(summary_data).T.rename(columns={0: "Details"}).to_excel(
          writer, sheet_name="Summary"
      )

  # === Format workbook ===
  wb = load_workbook(output_path)
  ws = wb["Mapped Standards"]

  # Bold headers and center them
  header_font = Font(bold=True)
  for cell in ws[1]:
      cell.font = header_font
      cell.alignment = Alignment(horizontal="center", vertical="center")

  # Auto-adjust column widths
  for col in ws.columns:
      max_len = 0
      col_letter = get_column_letter(col[0].column)
      for cell in col:
          if cell.value:
              max_len = max(max_len, len(str(cell.value)))
      ws.column_dimensions[col_letter].width = min(max_len + 3, 60)

  ws.freeze_panes = "A2"
  wb.save(output_path)

  print(f"✅ Final Excel created with summary: {output_path}")