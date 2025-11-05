"""
ThinkCERCA Automation Pipeline
==============================

Unified automation for aligning ThinkCERCA Student Guides with standards.

Pipeline stages:
1. Load and extract module-specific standards from Reference 1
2. Load Grade 8 standard descriptions
3. Join both into a single dataset
4. (Optional) AI matching with OpenAI → aligned standards per activity
5. (Optional) Export to InDesign via JSX automation

Usage:
    python main.py                 → run all, reuse cached results
    python main.py --ai            → include AI mapping
    python main.py --fresh         → force rerun all steps
    python main.py --indesign-only → skip data & AI, run InDesign only
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pathlib import Path

from thinkcerca_tool.modules import (
    standards_loader,
    standards_descriptions,
    join_standards,
    ai_matcher,
    indesign_bridge,
)
from thinkcerca_tool.config import DATA_DIR


# --- Define central output directory ---
OUTPUT_DIR = Path(DATA_DIR).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------
# Helpers
# ---------------------------
def file_exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0

def load_or_run_csv(path: Path, generator_fn, label: str) -> pd.DataFrame:
    """Generic helper to reuse or regenerate a DataFrame CSV."""
    if not file_exists(path):
        print(f"🧩 {label} not found — generating fresh...")
        df = generator_fn()
        df.to_csv(path, index=False)
        print(f"✅ {label} saved → {path}")
    else:
        print(f"♻️  Using cached {label} → {path}")
        df = pd.read_csv(path)
    return df

# ---------------------------
# Pipeline stages
# ---------------------------
def run_data_pipeline(force=False) -> pd.DataFrame:
    """Run Steps 1–3: load + join standards."""
    out_path = OUTPUT_DIR / "joined_standards.csv"
    if force or not file_exists(out_path):
        print("\n📘 Loading reference standards...")
        sheets = standards_loader.load_reference_1()
        df_ref = standards_loader.extract_standards(sheets)
        print(f"✅ Extracted {len(df_ref)} rows")

        print("\n📗 Loading standard descriptions...")
        df_desc = standards_descriptions.load_standard_descriptions()
        print(f"✅ Loaded {len(df_desc)} descriptions")

        print("\n📙 Joining both datasets...")
        df_joined = join_standards.join_module_standards()
        df_joined.to_csv(out_path, index=False)
        print(f"✅ Joined dataset saved → {out_path}")
    else:
        df_joined = pd.read_csv(out_path)
        print(f"♻️  Using cached joined data from {out_path}")

    return df_joined


def run_ai_mapping(force=False):
    """Step 4 — AI mapping pipeline."""
    ai_out = OUTPUT_DIR / "Grade8_Unit1_Module2_Mapped_Standards_AI_Final.xlsx"
    if force or not file_exists(ai_out):
        print("\n🤖 Running AI mapping pipeline...")
        ai_matcher.run_ai_mapping_pipeline()
        print(f"✅ AI mapping completed → {ai_out}")
    else:
        print(f"♻️  Using cached AI mapping results → {ai_out}")


def run_indesign_pipeline(force=False):
    """Step 5 — InDesign automation."""
    jsx_path = indesign_bridge.JSX_FILE
    if force or not file_exists(jsx_path):
        print("\n🖋️ Running InDesign full pipeline...")
        indesign_bridge.run_full_pipeline()
    else:
        print(f"♻️  JSX already exists at {jsx_path} — launching InDesign only...")
        indesign_bridge.run_full_pipeline()


# ---------------------------
# Entrypoint
# ---------------------------
def main():
    args = sys.argv
    run_ai = "--ai" in args
    force_fresh = "--fresh" in args
    indesign_only = "--indesign-only" in args

    print("\n🚀 Starting ThinkCERCA Automation\n")

    if indesign_only:
        run_indesign_pipeline(force_fresh)
    else:
        df_joined = run_data_pipeline(force_fresh)
        if run_ai:
            run_ai_mapping(force_fresh)
        run_indesign_pipeline(force_fresh)

    print("\n🎉 All steps finished successfully!\n")


if __name__ == "__main__":
    main()
