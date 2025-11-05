import os
import csv
import subprocess
from pathlib import Path
import pandas as pd
from thinkcerca_tool.config import DATA_DIR

# === PATH CONFIGURATION ===
BASE_DIR = Path(DATA_DIR).parent
DATA_DIR = BASE_DIR / "data"           # input sources
OUTPUT_DIR = BASE_DIR / "output"       # all generated outputs
JSX_DIR = BASE_DIR / "jsx"             # jsx scripts (generated + templates)
OUTPUT_DIR.mkdir(exist_ok=True)

# === FILE PATHS ===
INDD_FILE = DATA_DIR / "AI-1-grade-8-student-guide-volume-1.indd"
MAPPING_XLSX = OUTPUT_DIR / "Grade8_Unit1_Module2_Mapped_Standards_AI_Final.xlsx"
EXPORT_PDF = OUTPUT_DIR / "AI-1-grade-8-student-guide-volume-1-MAPPED.pdf"
JSX_FILE = JSX_DIR / "insert_from_python.jsx"

# ==============================================================
#  CSV EXPORT
# ==============================================================
def export_mapping_to_csv():
    """
    Export minimal CSV with Page + concatenated Standard codes.
    Ensures proper numeric pages are used.
    """
    if not MAPPING_XLSX.exists():
        raise FileNotFoundError(f"❌ Mapping Excel not found → {MAPPING_XLSX}")

    df = pd.read_excel(MAPPING_XLSX)

    if "Page" in df.columns and pd.api.types.is_numeric_dtype(df["Page"]):
        group_col = "Page"
    else:
        print("⚠️ 'Page' column missing or not numeric; falling back to 'Activity'")
        group_col = "Activity"

    df = df[df[group_col].notnull()]

    df_out = (
        df.groupby(group_col)["Standard Code"]
        .apply(lambda x: ", ".join(sorted(set(str(v).strip() for v in x if v))))
        .reset_index()
    )

    df_out.rename(columns={group_col: "Page"}, inplace=True)

    try:
        df_out["Page"] = df_out["Page"].astype(int)
        df_out = df_out.sort_values("Page")
    except Exception:
        pass

    csv_path = OUTPUT_DIR / "standards_for_indesign.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"✅ Mapping exported with numeric pages → {csv_path}")
    return csv_path


# ==============================================================
#  JSX GENERATION (your provided script, unchanged)
# ==============================================================
def build_jsx(csv_path: Path):
    jsx_code = f"""
#target "InDesign"
(function () {{
  alert("🚀 Inserting clean, smaller footer text visibly on ThinkCERCA document");

  var csvPath = "{csv_path.as_posix()}";
  var inddPath = "{INDD_FILE.as_posix()}";
  var docFile = File(inddPath);
  if (!docFile.exists) {{ alert("❌ InDesign file not found!"); return; }}

  var doc = app.open(docFile);

  // ✅ Same overlay layer logic as POC
  var overlayLayer;
  try {{
    overlayLayer = doc.layers.item("Automation Overlay");
    overlayLayer.name;
  }} catch (e) {{
    overlayLayer = doc.layers.add({{ name: "Automation Overlay" }});
  }}
  overlayLayer.visible = true;
  overlayLayer.locked = false;
  overlayLayer.printable = true;
  overlayLayer.move(LocationOptions.AT_BEGINNING);

  // === Helpers ===
  function trim(s) {{ return (s || "").replace(/^\\s+|\\s+$/g, ""); }}
  function safeSplit(line) {{
    var arr = [], cur = "", q = false;
    for (var i = 0; i < line.length; i++) {{
      var ch = line.charAt(i);
      if (ch === '"') q = !q;
      else if (ch === "," && !q) {{ arr.push(cur); cur = ""; }}
      else cur += ch;
    }}
    arr.push(cur);
    return arr;
  }}

  // === Read CSV ===
  var csvFile = File(csvPath);
  if (!csvFile.exists) {{ alert("❌ CSV not found!"); return; }}
  csvFile.open("r");
  var text = csvFile.read();
  csvFile.close();

  var lines = text.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").split("\\n");
  if (lines.length < 2) {{ alert("⚠️ CSV empty"); return; }}

  var header = safeSplit(lines[0]);
  var pageIdx = -1, codeIdx = -1;
  for (var i = 0; i < header.length; i++) {{
    var h = trim(header[i]);
    if (h === "Page") pageIdx = i;
    if (h === "Standard Code") codeIdx = i;
  }}
  if (pageIdx < 0) pageIdx = 0;
  if (codeIdx < 0) codeIdx = 1;

  // === Loop ===
  for (var r = 1; r < lines.length; r++) {{
    var line = trim(lines[r]);
    if (!line) continue;
    var parts = safeSplit(line);
    if (parts.length < 2) continue;

    var pageNum = parseInt(trim(parts[pageIdx]), 10);
    var code = trim(parts[codeIdx]);
    if (isNaN(pageNum) || !code) continue;

    var page = null;
    try {{ page = doc.pages.itemByName(pageNum.toString()); }} catch (e) {{}}
    if (!page || !page.isValid) {{
      try {{ page = doc.pages.item(pageNum - 1); }} catch (e2) {{}}
    }}
    if (!page || !page.isValid) continue;

    // === Keep absolute coordinates (safe) ===
    var tf = page.textFrames.add(overlayLayer);
    // a bit lower than original: from 2–4in to 8.7–9.1in zone
    tf.geometricBounds = ["8.7in", "1in", "9.1in", "5in"];
    tf.contents = code;  // only codes

    var t = tf.texts[0];
    t.pointSize = 10; // smaller
    t.justification = Justification.LEFT_ALIGN;

    var safeFonts = ["Helvetica", "Arial", "Times-Roman", "Courier"];
    for (var f = 0; f < safeFonts.length; f++) {{
      try {{ t.appliedFont = app.fonts.item(safeFonts[f]); break; }} catch (e) {{}}
    }}

    try {{ t.fillColor = doc.swatches.item("Black"); }} catch (e) {{}}
    // No rectangle, no background
    try {{ tf.strokeWeight = 0; }} catch (e) {{}}
    try {{ tf.fillColor = doc.swatches.item("None"); }} catch (e) {{}}

    tf.bringToFront();
    alert("✅ Inserted footer on page " + page.name + " → " + code);
  }}

  alert("🏁 Done inserting small clean codes near footer!");
}})();
"""
    JSX_FILE.write_text(jsx_code, encoding="utf-8")
    print(f"✅ JSX generated successfully → {JSX_FILE}")
    return JSX_FILE


# ==============================================================
#  INDESIGN LAUNCHER
# ==============================================================
def run_indesign(js_script: Path):
    js_path = js_script.as_posix()
    osa_script_path = JSX_DIR / "run_indesign_temp.applescript"

    osa_code = f'''
    tell application id "com.adobe.InDesign"
        activate
        do script (POSIX file "{js_path}") language javascript
    end tell
    '''
    osa_script_path.write_text(osa_code, encoding="utf-8")

    print(f"🚀 Launching InDesign automation via {osa_script_path}")
    subprocess.run(["osascript", str(osa_script_path)], check=True)
    osa_script_path.unlink(missing_ok=True)
    print("✅ InDesign finished processing.")


# ==============================================================
#  MAIN ENTRY
# ==============================================================
def run_full_pipeline():
    csv_path = export_mapping_to_csv()
    jsx_path = build_jsx(csv_path)
    run_indesign(jsx_path)

if __name__ == "__main__":
    run_full_pipeline()
