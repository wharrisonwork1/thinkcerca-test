"""
ThinkCERCA Automation Pipeline
==============================

This script unifies all major ThinkCERCA automation stages:

1. Load module-specific standards from the Core Scope & Sequence file
2. Load CCSS Grade 8 standard descriptions
3. Join and normalize both data sources
4. (Optional) Run AI mapping to align activities with standards
5. (Optional) Generate CSV + JSX and automate Adobe InDesign

Usage:
    python main.py                 → run everything end-to-end
    python main.py --ai            → include AI mapping
    python main.py --indesign-only → skip data prep and AI, just rerun InDesign

"""

import sys
import pandas as pd
from thinkcerca_tool.modules import (
    standards_loader,
    standards_descriptions,
    join_standards,
    ai_matcher,
    indesign_bridge,
)
from thinkcerca_tool.config import DATA_DIR


def run_data_pipeline() -> pd.DataFrame:
    """Run Steps 1–3: load + join standards."""
    print("\n📘 Loading reference standards...")
    sheets = standards_loader.load_reference_1()
    df_ref = standards_loader.extract_standards(sheets)
    print(f"✅ Extracted {len(df_ref)} rows from reference sheets")

    print("\n📗 Loading standard descriptions...")
    df_desc = standards_descriptions.load_standard_descriptions()
    print(f"✅ Loaded {len(df_desc)} descriptions")

    print("\n📙 Joining both datasets...")
    df_joined = join_standards.join_module_standards()
    print(f"✅ Joined dataset has {len(df_joined)} rows\n")

    out_path = DATA_DIR / "joined_standards_preview.csv"
    df_joined.to_csv(out_path, index=False)
    print(f"💾 Saved joined preview → {out_path}")
    return df_joined


def run_ai_mapping():
    """Step 4 — AI mapping via OpenAI."""
    print("\n🤖 Running AI mapping pipeline...")
    ai_matcher.run_ai_mapping_pipeline()
    print("✅ AI mapping completed.\n")


def run_indesign_pipeline():
    """Step 5 — export CSV, generate JSX, and automate InDesign."""
    print("\n🖋️ Running InDesign automation...")
    indesign_bridge.run_full_pipeline()
    print("✅ InDesign pipeline complete.\n")


def main():
    """Command-line entrypoint with optional flags."""
    run_ai = "--ai" in sys.argv
    indesign_only = "--indesign-only" in sys.argv

    print("🚀 Starting ThinkCERCA Automation\n")

    if indesign_only:
        run_indesign_pipeline()
    else:
        df_joined = run_data_pipeline()
        if run_ai:
            run_ai_mapping()
        run_indesign_pipeline()

    print("\n🎉 All steps finished successfully!")


if __name__ == "__main__":
    main()
