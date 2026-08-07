var window = {};
var fs = Object.assign({}, {
  readFile: function(path) {
    var app = Application.currentApplication();
    app.includeStandardAdditions = true;
    return app.doShellScript("cat " + path);
  }
});

var foodVectorsCode = fs.readFile("food_vectors.js");
eval(foodVectorsCode);

var vectors = window.FOOD_VECTORS;
var uniVec = vectors["ウニ"] || vectors["UNI"];

if (!uniVec) {
  console.log("No UNI vector found in JS!");
} else {
  var results = [];
  for (var word in vectors) {
    var vec = vectors[word];
    var dot = 0;
    for (var i = 0; i < uniVec.length; i++) {
      dot += uniVec[i] * vec[i];
    }
    if (dot >= 0.55) {
      results.push(word + ": " + dot);
    }
  }
  console.log("Matches: " + results.join(", "));
}
