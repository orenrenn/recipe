const fs = require('fs');
let code = fs.readFileSync('index.html', 'utf8');

// extract normalizeJapaneseText and computeSearchMatchScore
let normMatch = code.match(/function normalizeJapaneseText[\s\S]*?return s;\n    }/);
let toHiraMatch = code.match(/function toHiragana[\s\S]*?return String.*?;\n    }/);
let compMatch = code.match(/function computeSearchMatchScore[\s\S]*?return maxScore >= 1\.8 \? maxScore : 0;\n    }/);
let dicts = code.match(/window\.FOOD_VECTORS\s*=\s*\{.*?\};/);
let dicts2 = code.match(/window\.QUERY_VECTORS\s*=\s*\{.*?\};/);

let script = `
const window = {};
${dicts ? dicts[0] : 'window.FOOD_VECTORS = {};'}
${dicts2 ? dicts2[0] : 'window.QUERY_VECTORS = {};'}
const COMMON_SYNONYMS = { "ニンニク": "にんにく", "オクラ": "おくら" }; // simplified
${normMatch[0]}
${toHiraMatch[0]}
${compMatch[0]}

console.log("にんにく vs ニンニク", computeSearchMatchScore("にんにく", "ニンニク"));
console.log("おくら&長芋 vs オクラ", computeSearchMatchScore("おくら&長芋", "オクラ"));
console.log("にんにく vs ニンニク(レシピ)", computeSearchMatchScore("にんにく", "ニンニク(レシピ)"));
`;
fs.writeFileSync('test_jsc.js', script);
