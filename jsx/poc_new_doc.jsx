#target "InDesign"
  (function () {
    alert("🚀 Starting POC: new document → text → PDF export");

    try {
      // === 1. Create a new document ===
      var doc = app.documents.add();
      doc.documentPreferences.pageWidth = "8.5in";
      doc.documentPreferences.pageHeight = "11in";
      doc.documentPreferences.pagesPerDocument = 1;

      var page = doc.pages[0];

      // === 2. Add a giant visible text frame ===
      var tf = page.textFrames.add();
      tf.geometricBounds = ["2in", "1in", "9in", "7.5in"];
      tf.contents = "🧩 HELLO THINKCERCA AUTOMATION 🧩";

      var t = tf.texts[0];
      t.pointSize = 72;
      t.justification = Justification.CENTER_ALIGN;

      // === 3. Safe font fallback chain ===
      var safeFonts = ["Helvetica", "Arial", "Times-Roman", "Courier"];
      var applied = false;
      for (var f = 0; f < safeFonts.length; f++) {
        try {
          t.appliedFont = app.fonts.item(safeFonts[f]);
          applied = true;
          break;
        } catch (e) { }
      }
      if (!applied) alert("⚠️ No safe font found, using default.");

      // === 4. Apply bright styling ===
      try { t.fillColor = doc.swatches.item("Black"); } catch (e) { }
      try { tf.strokeColor = doc.swatches.item("Black"); tf.strokeWeight = 2; } catch (e) { }
      try { tf.fillColor = doc.swatches.item("Yellow"); } catch (e) { }
      tf.bringToFront();

      // === 5. Export as PDF to Desktop ===
      var pdfPath = Folder.desktop + "/thinkcerca_poc_output.pdf";
      var pdfFile = File(pdfPath);
      var preset = app.pdfExportPresets.firstItem();
      doc.exportFile(ExportFormat.PDF_TYPE, pdfFile, false, preset);

      alert("✅ Done! Exported PDF → " + pdfPath);

      // === 6. Save INDD too (optional) ===
      var inddPath = Folder.desktop + "/thinkcerca_poc.indd";
      doc.save(File(inddPath));

      // === 7. Close document ===
      doc.close(SaveOptions.NO);
    } catch (e) {
      alert("❌ Error: " + e);
    }
  })();
