import pandas as pd
import re
from thinkcerca_tool.config import FILES, TARGET_GRADE, TARGET_UNIT, TARGET_MODULE

def load_reference_1(path: str = FILES["REFERENCE_1"]) -> dict:
  """
  Load the Core National Scope and Sequence Excel file.
  Return a dictionary of {sheet_name: dataframe}.
  """
  xls = pd.ExcelFile(path)
  sheets = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
  return sheets


def extract_standards(sheets: dict) -> pd.DataFrame:
  """
  Search every worksheet for rows mentioning the target grade/unit/module.
  Returns a cleaned DataFrame with relevant text snippets.
  """
  results = []

  # Compile flexible patterns
  mod_pat = re.compile(fr"{TARGET_MODULE}\b", re.IGNORECASE)
  grade_pat = re.compile(fr"{TARGET_GRADE}\b", re.IGNORECASE)
  unit_pat = re.compile(fr"{TARGET_UNIT}\b", re.IGNORECASE)

  for sheet_name, df in sheets.items():
      df = df.fillna("").astype(str)

      for row_idx, row in df.iterrows():
          row_text = " | ".join(row.values)
          # check if our grade/unit/module appear anywhere in the row text
          if (
              mod_pat.search(row_text)
              and grade_pat.search(row_text)
              and unit_pat.search(row_text)
          ):
              prev_text = (
                  " | ".join(df.iloc[row_idx - 1].values)
                  if row_idx > 0
                  else ""
              )
              # quick cleanup of whitespace / separators
              context_above = re.sub(r"\s+", " ", prev_text.strip())
              context_row = re.sub(r"\s+", " ", row_text.strip())

              results.append(
                  {
                      "sheet": sheet_name,
                      "row": row_idx,
                      "context_above": context_above[:400],
                      "context_row": context_row[:400],
                  }
              )

  if not results:
      raise ValueError(
          f"No matches for {TARGET_GRADE} / {TARGET_UNIT} / {TARGET_MODULE}"
      )

  df_out = pd.DataFrame(results)
  df_out.drop_duplicates(subset=["context_row"], inplace=True)
  return df_out.reset_index(drop=True)