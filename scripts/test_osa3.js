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

var indexHtml = fs.readFile("index.html");
var scriptContent = indexHtml.match(/<script>([\s\S]*?)<\/script>/)[1];

var functionsCode = scriptContent
  .replace(/document\.getElementById.*?;/g, '')
  .replace(/window\.addEventListener.*?;/g, '')
  .replace(/renderRecipeList\(\)/g, '')
  .replace(/updatePagination\(\)/g, '');

eval(functionsCode);

var recipe1 = {
  title: "玄米と麦と白米",
  category: "主食",
  ingredients: ["玄米：3合（60% - 不動のメイン）", "押し麦：1合（20% - プチプチ食感をしっかり味わえる）", "白米：1合（20% - 全体のまとまり役）"],
  steps: [
    { title: "お米を研ぐ", text: "玄米（3合）と白米（1合）を一緒にボウルで研ぎ、炊飯器に入れます。" },
    { title: "ベースの水を計る", text: "炊飯器の「玄米」の4合目盛りまで水を入れます。（※玄米モードの目盛りがない場合は、白米の4合目盛りより少し多めに入れます）" },
    { title: "押し麦と追加の水を加える", text: "洗わずにそのままの押し麦（1合）と、押し麦が吸う分の追加の水として「200ml（1カップ）」を加えます。" },
    { title: "軽く混ぜて、しっかり浸水", text: "押し麦は上に浮きやすいので、炊きムラを防ぐために全体をサッと混ぜ合わせます。その後、最低でも2時間（できれば一晩）しっかり水に浸けてください。" },
    { title: "塩を加えて炊飯", text: "炊く直前に塩をひとつまみ入れてから、炊飯ボタンを押します（玄米モードがあれば玄米モードを使用してください）。" }
  ],
  memo: "水は白米の4合線くらいまで\n押し麦は比重が軽く、炊き上がるとお釜の上部に固まりやすい性質があります。炊き上がったら、なるべく早めに底から大きくすくい上げるように「天地返し（全体を混ぜる）」をしてあげると、麦とお米が均等に散らばり、冷めても美味しく召し上がれます。"
};

var score1 = computeRecipeSemanticScore(recipe1, "ウニ");
console.log("Score for recipe1 with 'ウニ': " + score1);
