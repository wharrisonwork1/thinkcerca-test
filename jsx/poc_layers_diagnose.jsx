#target "InDesign"
  (function () {
    alert("🔍 Running Layer Diagnostic");

    var inddPath = "/Users/saqib.ejaz/thinkcerca/thinkcerca_tool/data/AI-1-grade-8-student-guide-volume-1.indd";
    var docFile = File(inddPath);
    if (!docFile.exists) { alert("❌ File not found!"); return; }

    var doc = app.open(docFile);

    var log = "📘 Document: " + doc.name + "\\n";
    log += "Total Pages: " + doc.pages.length + "\\n";
    log += "\\n=== Layers Overview ===\\n";

    for (var i = 0; i < doc.layers.length; i++) {
      var L = doc.layers[i];
      log += (i + 1) + ". " + L.name + " | visible=" + L.visible + " | locked=" + L.locked + " | printable=" + L.printable + "\\n";
    }

    log += "\\n=== Master Spreads ===\\n";
    for (var m = 0; m < doc.masterSpreads.length; m++) {
      log += (m + 1) + ". " + doc.masterSpreads[m].name + " (pages=" + doc.masterSpreads[m].pages.length + ")\\n";
    }

    log += "\\n=== First Page Info ===\\n";
    var first = doc.pages[0];
    log += "Name: " + first.name + " | Parent: " + (first.appliedMaster ? first.appliedMaster.name : "none") + "\\n";
    log += "Items on page: " + first.allPageItems.length + "\\n";
    for (var j = 0; j < Math.min(10, first.allPageItems.length); j++) {
      var it = first.allPageItems[j];
      log += "  • " + it.constructor.name + " (" + it.name + ") layer=" + it.itemLayer.name + "\\n";
    }

    alert(log);
  })();
