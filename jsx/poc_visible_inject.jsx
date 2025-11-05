#target "InDesign"
  (function () {
    alert("🚀 Inserting test text visibly on ThinkCERCA document");

    var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
    var doc = app.open(File(inddPath));

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

    // ✅ Move it to top of layer stack
    overlayLayer.move(LocationOptions.AT_BEGINNING);

    // === Get first few pages and insert test text ===
    for (var i = 0; i < Math.min(3, doc.pages.length); i++) {
      var page = doc.pages[i];
      var tf = page.textFrames.add(overlayLayer);
      tf.geometricBounds = ["2in", "1in", "4in", "6in"];
      tf.contents = "🧩 TEST INSERT PAGE " + page.name;

      var t = tf.texts[0];
      t.pointSize = 48;
      t.justification = Justification.CENTER_ALIGN;

      // Font fallback
      var safeFonts = ["Helvetica", "Arial", "Times-Roman", "Courier"];
      for (var f = 0; f < safeFonts.length; f++) {
        try { t.appliedFont = app.fonts.item(safeFonts[f]); break; } catch (e) { }
      }

      // Style so it's visible
      try { t.fillColor = doc.swatches.item("Black"); } catch (e) { }
      try { tf.strokeWeight = 3; tf.strokeColor = doc.swatches.item("Red"); } catch (e) { }
      try { tf.fillColor = doc.swatches.item("Yellow"); } catch (e) { }

      tf.bringToFront();
      alert("✅ Inserted visible text on page " + page.name);
    }

    alert("🏁 Done inserting visible overlays. Check pages 1–3.");
  })();
