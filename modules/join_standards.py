import re
import pandas as pd
from thinkcerca_tool.modules.standards_loader import extract_standards, load_reference_1
from thinkcerca_tool.modules.standards_descriptions import load_standard_descriptions

def join_module_standards() -> pd.DataFrame:
  """
  Combine module-specific standards (Reference 1)
  with Grade 8 CCSS descriptions (Reference 2).

  Returns:
      DataFrame with columns:
      ['sheet', 'context_row', 'Standard_Code', 'Description']
  """

  # --- Load both data sources ---
  sheets = load_reference_1()
  module_df = extract_standards(sheets)
  desc_df = load_standard_descriptions()

  # --- Detect standard codes like CCSS.L.8.6 or L.8.6.B ---
  code_pattern = re.compile(r"(?:CCSS\.)?([A-Z]{1,3}\.\d{1,2}\.\d+[A-Z]?)", re.IGNORECASE)

  matches = []
  for _, row in module_df.iterrows():
      found = code_pattern.findall(row["context_row"])
      if not found:
          continue
      for code in found:
          # Normalize code format
          code = code.upper().replace("CCSS.", "")
          full_code = f"CCSS.{code}"
          matches.append({
              "sheet": row["sheet"],
              "context_row": row["context_row"][:300],
              "Standard_Code": full_code
          })

  # --- If no matches found, fallback to provide context only ---
  if not matches:
      print("⚠️ No explicit CCSS codes found in Module 2 text; using full Grade 8 CCSS set.")
      merged = module_df.assign(Standard_Code=None)
  else:
      merged = pd.DataFrame(matches)

  # --- Merge with descriptions ---
  df_out = pd.merge(merged, desc_df, on="Standard_Code", how="left")

  # Replace missing descriptions safely (avoid chained assignment warnings)
  df_out["Description"] = df_out["Description"].fillna("(No description found)")

  # Deduplicate by code + sheet
  df_out.drop_duplicates(subset=["Standard_Code", "sheet"], inplace=True)
  df_out.reset_index(drop=True, inplace=True)

  return df_out
