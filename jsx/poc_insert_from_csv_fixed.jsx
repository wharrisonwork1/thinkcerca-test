#target "InDesign"
(function () {
  alert("🚀 Inserting clean, smaller footer text visibly on ThinkCERCA document");

  var csvPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/output/standards_for_indesign.csv";
  var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
  var docFile = File(inddPath);
  if (!docFile.exists) { alert("❌ InDesign file not found!"); return; }

  var doc = app.open(docFile);

  // ✅ Same overlay layer logic as POC
  var overlayLayer;
  try {
    overlayLayer = doc.layers.item("Automation Overlay");
    overlayLayer.name;
  } catch (e) {
    overlayLayer = doc.layers.add({ name: "Automation Overlay" });
  }
  overlayLayer.visible = true;
  overlayLayer.locked = false;
  overlayLayer.printable = true;
  overlayLayer.move(LocationOptions.AT_BEGINNING);

  // === Helpers ===
  function trim(s) { return (s || "").replace(/^\s+|\s+$/g, ""); }
  function safeSplit(line) {
    var arr = [], cur = "", q = false;
    for (var i = 0; i < line.length; i++) {
      var ch = line.charAt(i);
      if (ch === '"') q = !q;
      else if (ch === "," && !q) { arr.push(cur); cur = ""; }
      else cur += ch;
    }
    arr.push(cur);
    return arr;
  }

  // === Read CSV ===
  var csvFile = File(csvPath);
  if (!csvFile.exists) { alert("❌ CSV not found!"); return; }
  csvFile.open("r");
  var text = csvFile.read();
  csvFile.close();

  var lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  if (lines.length < 2) { alert("⚠️ CSV empty"); return; }

  var header = safeSplit(lines[0]);
  var pageIdx = -1, codeIdx = -1;
  for (var i = 0; i < header.length; i++) {
    var h = trim(header[i]);
    if (h === "Page") pageIdx = i;
    if (h === "Standard Code") codeIdx = i;
  }
  if (pageIdx < 0) pageIdx = 0;
  if (codeIdx < 0) codeIdx = 1;

  // === Loop ===
  for (var r = 1; r < lines.length; r++) {
    var line = trim(lines[r]);
    if (!line) continue;
    var parts = safeSplit(line);
    if (parts.length < 2) continue;

    var pageNum = parseInt(trim(parts[pageIdx]), 10);
    var code = trim(parts[codeIdx]);
    if (isNaN(pageNum) || !code) continue;

    var page = null;
    try { page = doc.pages.itemByName(pageNum.toString()); } catch (e) {}
    if (!page || !page.isValid) {
      try { page = doc.pages.item(pageNum - 1); } catch (e2) {}
    }
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
    for (var f = 0; f < safeFonts.length; f++) {
      try { t.appliedFont = app.fonts.item(safeFonts[f]); break; } catch (e) {}
    }

    try { t.fillColor = doc.swatches.item("Black"); } catch (e) {}
    // No rectangle, no background
    try { tf.strokeWeight = 0; } catch (e) {}
    try { tf.fillColor = doc.swatches.item("None"); } catch (e) {}

    tf.bringToFront();
    alert("✅ Inserted footer on page " + page.name + " → " + code);
  }

  alert("🏁 Done inserting small clean codes near footer!");
})();
