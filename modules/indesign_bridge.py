import os
import csv
import subprocess
from pathlib import Path
import pandas as pd

# === CONFIG ===
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INDD_FILE = DATA_DIR / "AI-1-grade-8-student-guide-volume-1.indd"
MAPPING_XLSX = DATA_DIR / "Grade8_Unit1_Module2_Mapped_Standards_AI_Final.xlsx"
JSX_FILE = Path(__file__).resolve().parents[1] / "jsx" / "insert_from_python.jsx"
EXPORT_PDF = DATA_DIR / "AI-1-grade-8-student-guide-volume-1-MAPPED.pdf"

def export_mapping_to_csv():
    """Export minimal CSV with Page + concatenated Standard codes."""
    df = pd.read_excel(MAPPING_XLSX)
    group_col = None
    for candidate in ["Page", "Activity", "Slide Summary / Extracted Text"]:
        if candidate in df.columns:
            group_col = candidate
            break

    if not group_col:
        raise ValueError(f"No suitable grouping column found in {MAPPING_XLSX}")

    df = df.groupby(group_col)["Standard Code"].apply(lambda x: ", ".join(sorted(set(str(v).strip() for v in x)))).reset_index()
    df.rename(columns={group_col: "Page"}, inplace=True)

    csv_path = DATA_DIR / "standards_for_indesign.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Mapping exported → {csv_path}")
    return csv_path

def build_jsx(csv_path: Path):
    """JSX with detailed logging for debugging undefined object (21) errors."""
    jsx_code = f"""
#target "InDesign"
(function() {{
    var csvPath = "{csv_path.as_posix()}";
    var inddPath = "{INDD_FILE.as_posix()}";
    var exportPDF = "{EXPORT_PDF.as_posix()}";

    var _replace = ("").replace;
    var _trim = ("").trim;
    var _split = ("").split;

    function log(msg) {{
        try {{
            var f = File("~/Desktop/indesign_debug.log");
            f.open("a");
            f.writeln(new Date().toISOString() + " :: " + msg);
            f.close();
        }} catch(e) {{}}
    }}

    function realString(v) {{
        try {{
            return v === undefined || v === null ? "" : ("" + v);
        }} catch(e) {{
            return "" + v;
        }}
    }}

    log("🚀 Script started");

    var csvFile = File(csvPath);
    if (!csvFile.exists) {{
        alert("❌ CSV not found: " + csvPath);
        return;
    }}
    csvFile.encoding = "BINARY";
    csvFile.open("r");
    var csvText = realString(csvFile.read());
    csvFile.close();

    csvText = _replace.call(csvText, /\\r\\n/g, "\\n");
    csvText = _replace.call(csvText, /\\r/g, "\\n");
    var lines = _split.call(csvText, "\\n");
    log("📊 Lines read: " + lines.length);

    if (!lines || lines.length === 0) {{
        alert("❌ Empty CSV.");
        return;
    }}

    var headerLine = realString(lines[0]);
    headerLine = _replace.call(headerLine, /^\\uFEFF/, "");
    headerLine = _replace.call(headerLine, /\\r/g, "");
    headerLine = _replace.call(headerLine, /\\n/g, "");
    headerLine = _trim.call(headerLine);

    var delimiter = ",";
    if (headerLine.indexOf(";") !== -1) delimiter = ";";
    else if (headerLine.indexOf("\\t") !== -1) delimiter = "\\t";

    var headerArr = _split.call(headerLine, delimiter);
    for (var i = 0; i < headerArr.length; i++)
        headerArr[i] = _trim.call(realString(headerArr[i]));

    log("🧭 headerArr: " + headerArr.join(" | "));

    var pageIdx = headerArr.indexOf("Page");
    var codesIdx = headerArr.indexOf("Standard Code");
    if (pageIdx < 0) pageIdx = 0;
    if (codesIdx < 0) codesIdx = 1;
    log("🔍 pageIdx=" + pageIdx + " codesIdx=" + codesIdx);

    if (!File(inddPath).exists) {{
        alert("❌ InDesign file not found: " + inddPath);
        return;
    }}
    var doc = app.open(File(inddPath));
    log("📘 Opened document: " + doc.name);

    // === Iterate rows with detailed logs ===
    for (var r = 1; r < lines.length; r++) {{
        try {{
            var line = realString(lines[r]);
            if (!line || _trim.call(line).length === 0) continue;
            log("---- ROW " + r + " ----");
            log("raw line=" + line);

            var parts = _split.call(line, delimiter);
            log("parts.length=" + parts.length);

            var pageNum = parseInt(parts[pageIdx], 10);
            var codes = realString(parts[codesIdx]);
            log("pageNum=" + pageNum + " codes=" + codes);

            if (isNaN(pageNum)) {{
                log("⚠️ Invalid pageNum string=" + parts[pageIdx]);
                continue;
            }}

            var page;
            try {{
                page = doc.pages.itemByName(pageNum.toString());
                log("page object typeof=" + (typeof page));
            }} catch(e) {{
                log("❌ itemByName threw: " + e);
                continue;
            }}

            if (!page || !page.isValid) {{
                log("⚠️ Page invalid: " + pageNum);
                continue;
            }}

            try {{
                log("page.bounds typeof=" + (typeof page.bounds));
                log("page.bounds value=" + page.bounds);
            }} catch(e) {{
                log("⚠️ Cannot access page.bounds: " + e);
                continue;
            }}

            var tf;
            try {{
                tf = page.textFrames.add();
                log("textFrame created, typeof=" + (typeof tf));
            }} catch(e) {{
                log("❌ textFrames.add() failed: " + e);
                continue;
            }}

            if (!tf || !tf.isValid) {{
                log("⚠️ textFrame invalid");
                continue;
            }}

            var y = page.bounds[2] - 60;
            var x = page.bounds[1] + 30;
            log("computed y=" + y + " x=" + x);

            try {{
                tf.geometricBounds = [y - 30, x, y, x + 250];
                tf.contents = codes;
            }} catch(e) {{
                log("❌ Setting text frame bounds/contents failed: " + e);
                continue;
            }}

            if (tf.texts && tf.texts.length > 0) {{
                try {{
                    var t = tf.texts[0];
                    log("text object valid=" + (t ? "yes" : "no"));
                    if (t) {{
                        t.pointSize = 9;
                        try {{ t.appliedFont = app.fonts.item("Minion Pro"); }} catch(e) {{}}
                        try {{ t.fillColor = doc.swatches.item("Black"); }} catch(e) {{}}
                    }}
                }} catch(e) {{
                    log("❌ Editing text failed: " + e);
                }}
            }}

            log("✅ Inserted on page " + pageNum);
        }} catch(e) {{
            log("❌ Outer loop error row " + r + ": " + e);
        }}
    }}

    try {{
        var preset = app.pdfExportPresets.firstItem();
        doc.exportFile(ExportFormat.PDF_TYPE, File(exportPDF), false, preset);
        log("📤 Exported PDF → " + exportPDF);
    }} catch(e) {{
        log("⚠️ PDF export failed: " + e);
    }}

    doc.close(SaveOptions.NO);
    alert("✅ Finished — check Desktop log");
    log("🏁 Done.");
}})();
"""
    JSX_FILE.write_text(jsx_code, encoding="utf-8")
    print(f"✅ JSX generated → {JSX_FILE}")
    return JSX_FILE


def run_indesign(js_script: Path):
    js_path = js_script.as_posix()
    osa_script_path = js_script.parent / "run_indesign_temp.applescript"

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


def run_full_pipeline():
    csv_path = export_mapping_to_csv()
    jsx_path = build_jsx(csv_path)
    run_indesign(jsx_path)

if __name__ == "__main__":
    run_full_pipeline()
