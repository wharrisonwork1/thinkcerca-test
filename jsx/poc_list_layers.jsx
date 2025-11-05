#target "InDesign"
  (function () {
    alert("🚀 Listing all layers and their states");

    // Path to your real ThinkCERCA InDesign file
    var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
    var docFile = File(inddPath);

    if (!docFile.exists) {
      alert("❌ File not found: " + inddPath);
      return;
    }

    var doc = app.open(docFile);
    if (!doc || !doc.isValid) {
      alert("❌ Could not open document");
      return;
    }

    var msg = "📄 " + doc.name + " opened successfully\\n\\n";
    msg += "Total pages: " + doc.pages.length + "\\n\\n";
    msg += "Layers:\\n-------------------------------------\\n";

    for (var i = 0; i < doc.layers.length; i++) {
      var L = doc.layers[i];
      msg += (i + 1) + ". " + L.name +
        " | visible=" + L.visible +
        " | locked=" + L.locked +
        " | printable=" + L.printable + "\\n";
    }

    alert(msg);
  })();
