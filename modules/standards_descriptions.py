import pandas as pd
from thinkcerca_tool.config import FILES

def load_standard_descriptions(path: str = None) -> pd.DataFrame:
  """
  Load CCSS standards descriptions for Grade 8.
  Handles capitalization inconsistencies (e.g., 'CCSS Code', 'CCSS Standard').
  Returns a DataFrame with Standard_Code and Description.
  """
  if path is None:
      path = FILES["REFERENCE_1"].replace(
          "_new_ Core National Scope and Sequence",
          "[AI Lab] ThinkCERCA - ELA MOAC Standards (INTERNAL)"
      )

  xls = pd.ExcelFile(path)
  if "Grade 8" not in xls.sheet_names:
      raise ValueError("Grade 8 sheet not found in standards file.")

  df = xls.parse("Grade 8").fillna("")
  # Normalize columns to lowercase for easier matching
  col_map = {c.lower().strip(): c for c in df.columns}
  code_col = next((v for k, v in col_map.items() if "ccss" in k and "code" in k), None)
  desc_col = next((v for k, v in col_map.items() if "ccss" in k and "standard" in k), None)

  if not code_col or not desc_col:
      raise ValueError(f"Could not detect CCSS code or standard columns in Grade 8 sheet. Found: {list(df.columns)}")

  subset = df[[code_col, desc_col]].copy()
  subset.columns = ["Standard_Code", "Description"]
  subset = subset[subset["Standard_Code"].astype(str).str.strip() != ""]
  subset.drop_duplicates(subset=["Standard_Code"], inplace=True)

  subset["Standard_Code"] = subset["Standard_Code"].str.strip()
  subset["Description"] = subset["Description"].str.strip()

  return subset.reset_index(drop=True)
