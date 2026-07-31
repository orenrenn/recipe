const fs = require('fs');
const code = fs.readFileSync('index.html', 'utf-8');

function normalizeJapaneseText(str) {
  if (!str) return '';
  let norm = str.normalize('NFKC');
  norm = norm.toLowerCase();
  norm = norm.replace(/[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】]/g, '');
  return norm;
}

function toHiragana(str) {
  if (!str) return '';
  return String(str).replace(/[\u30A1-\u30F6\u30F4]/g, match => String.fromCharCode(match.charCodeAt(0) - 0x60));
}

let text1 = "玄米：3合（60% - 不動のメイン） ・押し麦：1合（20% - プチプチ食感をしっかり味わえる） ・白米：1合（20% - 全体のまとまり役）";
let text2 = "生米：1合（洗わずに使います）・余った豆スープ＋お湯：合計で600〜800ml・お好みのキノコ（しめじ、マッシュルームなど）：1/2パック・粉チーズ、粗挽き黒こしょう：お好みで・フライパンにオリーブオイル（大さじ1）とみじん切りにしたニンニク（1片）を入れ、弱火で香りを出す";

let norm1 = normalizeJapaneseText(text1);
let norm2 = normalizeJapaneseText(text2);
let hira1 = toHiragana(norm1);
let hira2 = toHiragana(norm2);

console.log("hira1:", hira1);
console.log("hira2:", hira2);
console.log("hira1 contains うに?", hira1.includes("うに"));
console.log("hira2 contains うに?", hira2.includes("うに"));
