#target "InDesign"
  (function () {
    alert("🚀 Inserting test text visibly on ThinkCERCA document (CSV-driven)");

    var csvPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/output/standards_for_indesign.csv";
    var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
    var docFile = File(inddPath);
    if (!docFile.exists) {
      alert("❌ InDesign file not found: " + inddPath);
      return;
    }

    var doc = app.open(docFile);

    // ✅ Create or get overlay layer
    var overlayLayer;
    try {
      overlayLayer = doc.layers.item("Automation Overlay");
      overlayLayer.name; // trigger error if doesn't exist
    } catch (e) {
      overlayLayer = doc.layers.add({ name: "Automation Overlay" });
    }
    overlayLayer.visible = true;
    overlayLayer.locked = false;
    overlayLayer.printable = true;
    overlayLayer.move(LocationOptions.AT_BEGINNING);

    // === Helpers ===
    function trim(s) {
      if (!s) return "";
      return s.replace(/^\s+|\s+$/g, "");
    }

    function safeSplit(line) {
      if (!line) return [];
      var result = [];
      var current = "";
      var inQuotes = false;
      var i, ch;
      for (i = 0; i < line.length; i++) {
        ch = line.charAt(i);
        if (ch === '"') {
          inQuotes = !inQuotes;
        } else if (ch === "," && !inQuotes) {
          result.push(current);
          current = "";
        } else {
          current += ch;
        }
      }
      result.push(current);
      return result;
    }

    // === Read CSV ===
    var csvFile = File(csvPath);
    if (!csvFile.exists) {
      alert("❌ CSV not found: " + csvPath);
      return;
    }
    csvFile.open("r");
    var csvText = csvFile.read();
    csvFile.close();

    var lines = csvText.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
    if (lines.length < 2) {
      alert("⚠️ CSV appears empty or invalid");
      return;
    }

    var header = safeSplit(lines[0]);
    var pageIdx = -1;
    var codeIdx = -1;
    var i;
    for (i = 0; i < header.length; i++) {
      var h = trim(header[i]);
      if (h === "Page") pageIdx = i;
      if (h === "Standard Code") codeIdx = i;
    }
    if (pageIdx < 0) pageIdx = 0;
    if (codeIdx < 0) codeIdx = 1;

    // === Loop through CSV ===
    var r;
    for (r = 1; r < lines.length; r++) {
      var line = trim(lines[r]);
      if (!line) continue;
      var parts = safeSplit(line);
      if (parts.length < 2) continue;

      var pageNum = parseInt(trim(parts[pageIdx]), 10);
      var code = trim(parts[codeIdx]);
      if (isNaN(pageNum) || !code) continue;

      var page = null;
      try {
        page = doc.pages.itemByName(pageNum.toString());
        if (!page.isValid) throw "invalid";
      } catch (e) {
        if (pageNum - 1 < doc.pages.length && pageNum > 0) {
          try {
            page = doc.pages.item(pageNum - 1);
          } catch (e2) { }
        }
      }

      if (!page || !page.isValid) {
        $.writeln("⚠️ Page not found for " + pageNum);
        continue;
      }

      // === Insert visible text (same POC logic) ===
      var tf = page.textFrames.add(overlayLayer);
      tf.geometricBounds = ["2in", "1in", "4in", "6in"];
      tf.contents = "🧩 " + code + " (Page " + page.name + ")";

      var t = tf.texts[0];
      t.pointSize = 48;
      t.justification = Justification.CENTER_ALIGN;

      // Font fallback
      var safeFonts = ["Helvetica", "Arial", "Times-Roman", "Courier"];
      var f;
      for (f = 0; f < safeFonts.length; f++) {
        try {
          t.appliedFont = app.fonts.item(safeFonts[f]);
          break;
        } catch (e) { }
      }

      // Style it visibly
      try { t.fillColor = doc.swatches.item("Black"); } catch (e) { }
      try { tf.strokeWeight = 3; tf.strokeColor = doc.swatches.item("Red"); } catch (e) { }
      try { tf.fillColor = doc.swatches.item("Yellow"); } catch (e) { }

      tf.bringToFront();
      alert("✅ Inserted visible text on page " + page.name + " → " + code);
    }

    alert("🏁 Done inserting visible overlays. Check affected pages!");
  })();
