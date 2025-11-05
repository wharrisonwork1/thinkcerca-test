#target "InDesign"
  (function () {
    alert("🚀 Running safe label POC");

    var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
    var docFile = File(inddPath);
    if (!docFile.exists) { alert("❌ File not found!"); return; }

    var doc = app.open(docFile);
    var page = doc.pages[0];

    // === Small label in bottom-right corner ===
    var b = page.bounds; // [y1, x1, y2, x2]
    var labelHeight = 50;
    var labelWidth = 300;
    var yBottom = b[2] - 72; // 1 inch up
    var xRight = b[3] - 72 - labelWidth;

    var tf = page.textFrames.add();
    tf.geometricBounds = [yBottom - labelHeight, xRight, yBottom, xRight + labelWidth];
    tf.contents = "🧩 THINKCERCA DEBUG LABEL";

    var t = tf.texts[0];
    t.pointSize = 24;
    t.justification = Justification.CENTER_ALIGN;

    // Use safe font
    var safeFonts = ["Helvetica", "Arial", "Times-Roman", "Courier"];
    for (var f = 0; f < safeFonts.length; f++) {
      try { t.appliedFont = app.fonts.item(safeFonts[f]); break; } catch (e) { }
    }

    // visible color (red text, transparent background)
    try { t.fillColor = doc.swatches.item("Black"); } catch (e) { }

    tf.fillColor = doc.swatches.item("None"); // transparent frame
    tf.strokeColor = doc.swatches.item("Black");
    tf.strokeWeight = 1;
    tf.bringToFront();

    alert("✅ Label added to bottom-right corner!");
  })();
