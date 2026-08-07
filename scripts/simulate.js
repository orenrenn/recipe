const fs = require('fs');

// Stub window object
global.window = {};

// Load the vectors
const vectorsCode = fs.readFileSync('food_vectors.js', 'utf-8');
eval(vectorsCode); // This will set window.FOOD_VECTORS and window.QUERY_VECTORS

// Load the functions from index.html
const htmlContent = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = htmlContent.match(/<script>([\s\S]*?)<\/script>/);
const scriptContent = scriptMatch[1];

// We need to evaluate the script in a way that gives us access to computeRecipeSemanticScore
// Let's just extract the relevant functions manually to avoid DOM dependencies
const functions = `
function normalizeJapaneseText(str) {
  if (!str) return '';
  let norm = str.normalize('NFKC');
  norm = norm.toLowerCase();
  norm = norm.replace(/[\\s\\u3000・,\\-_\\/\\\\\\(\\)\\u3001\\u3002\\u300C\\u300D\\u3010\\u3011「」【】]/g, '');
  return norm;
}

function toHiragana(str) {
  if (!str) return '';
  return String(str).replace(/[\\u30A1-\\u30F6\\u30F4]/g, match => String.fromCharCode(match.charCodeAt(0) - 0x60));
}

function computeSearchMatchScore(queryWord, targetText) {
  if (!queryWord || !targetText) return 0;
  const qNorm = normalizeJapaneseText(queryWord);
  const tNorm = normalizeJapaneseText(targetText);
  if (!qNorm || !tNorm) return 0;

  const allQueryWords = { ...(window.FOOD_VECTORS || {}), ...(window.QUERY_VECTORS || {}) };
  const qHira = toHiragana(qNorm);
  const isSemanticQuery = (qNorm in allQueryWords) || (qHira in allQueryWords);

  const isAllHiragana = /^[\\u3040-\\u309F]+$/.test(qNorm);
  if (!isSemanticQuery && isAllHiragana && qNorm.length <= 2) {
    return 0;
  }

  let maxScore = 0;
  let baseSubstringScore = isSemanticQuery ? 0.5 : 2.5;

  if (tNorm.includes(qNorm)) {
    maxScore = baseSubstringScore;
  } else {
    const tHira = toHiragana(tNorm);
    if (tHira.includes(qHira) && maxScore < baseSubstringScore - 0.1) {
      maxScore = baseSubstringScore - 0.1;
    }
  }

  if (window.FOOD_VECTORS) {
    let maxSemanticSim = 0;
    const matchedWords = [];
    for (const qWord in allQueryWords) {
      const qWordHira = toHiragana(qWord);
      let idx = -1;
      let matchLen = 0;
      if (qNorm === qWord || qHira === qWordHira) {
        idx = 0; matchLen = qNorm.length;
      } else if (qWord.length >= 2 && qNorm.includes(qWord)) {
        idx = qNorm.indexOf(qWord); matchLen = qWord.length;
      } else if (qWord.length >= 2 && qHira.includes(qWordHira)) {
        idx = qHira.indexOf(qWordHira); matchLen = qWordHira.length;
      }
      if (idx !== -1) {
        matchedWords.push({ word: qWord, start: idx, end: idx + matchLen });
      }
    }

    const queryWordsToUse = [];
    for (let i = 0; i < matchedWords.length; i++) {
      let isSubsumed = false;
      for (let j = 0; j < matchedWords.length; j++) {
        if (i === j) continue;
        if (matchedWords[i].start >= matchedWords[j].start && 
            matchedWords[i].end <= matchedWords[j].end && 
            (matchedWords[j].end - matchedWords[j].start) > (matchedWords[i].end - matchedWords[i].start)) {
          isSubsumed = true;
          break;
        }
      }
      if (!isSubsumed) {
        queryWordsToUse.push(matchedWords[i].word);
      }
    }

    const matchedTargetWords = [];
    for (const tWord in window.FOOD_VECTORS) {
      let searchIdx = 0;
      while (true) {
        searchIdx = tNorm.indexOf(tWord, searchIdx);
        if (searchIdx === -1) break;
        let isValid = true;
        const isKatakanaWord = /^[\\u30A0-\\u30FF]+$/.test(tWord);
        if (isKatakanaWord) {
          const prevChar = searchIdx > 0 ? tNorm[searchIdx - 1] : '';
          const nextChar = searchIdx + tWord.length < tNorm.length ? tNorm[searchIdx + tWord.length] : '';
          if (/[\\u30A0-\\u30FF]/.test(prevChar) || /[\\u30A0-\\u30FF]/.test(nextChar)) {
            isValid = false;
          }
        }
        if (isValid) {
          matchedTargetWords.push({ word: tWord, start: searchIdx, end: searchIdx + tWord.length });
        }
        searchIdx += 1;
      }
    }

    const validTargetWords = new Set();
    for (let i = 0; i < matchedTargetWords.length; i++) {
      let isSubsumed = false;
      for (let j = 0; j < matchedTargetWords.length; j++) {
        if (i === j) continue;
        const wi = matchedTargetWords[i];
        const wj = matchedTargetWords[j];
        if (wi.start >= wj.start && wi.end <= wj.end && (wj.end - wj.start) > (wi.end - wi.start)) {
          isSubsumed = true;
          break;
        }
      }
      if (!isSubsumed) {
        validTargetWords.add(matchedTargetWords[i].word);
      }
    }

    for (const qWord of queryWordsToUse) {
      const qVec = allQueryWords[qWord];
      for (const tWord of validTargetWords) {
        const tVec = window.FOOD_VECTORS[tWord];
        let dot = 0;
        for (let i = 0; i < qVec.length; i++) {
          dot += qVec[i] * tVec[i];
        }
        if (dot > 1.0) dot = 1.0;
        if (dot > maxSemanticSim) maxSemanticSim = dot;
      }
    }

    if (maxSemanticSim >= 0.55) {
      const semanticScore = (maxSemanticSim - 0.5) * 14.0;
      maxScore = Math.max(maxScore, semanticScore);
    }
  }

  return maxScore >= 1.8 ? maxScore : 0;
}

function computeRecipeSemanticScore(recipe, queryStr) {
  let normalizedQuery = queryStr.replace(/[\\u3000・,\\/、。｜\\|]/g, ' ');
  const rawKeywords = normalizedQuery.trim().split(/\\s+/).filter(k => k.length > 0);
  if (rawKeywords.length === 0) return 1.0;

  const keywords = [];
  const allQueryWords = { ...(window.FOOD_VECTORS || {}), ...(window.QUERY_VECTORS || {}) };
  for (const kw of rawKeywords) {
    const qNorm = normalizeJapaneseText(kw);
    const qHira = toHiragana(qNorm);
    const isSemantic = (qNorm in allQueryWords) || (qHira in allQueryWords);
    const isAllHira = /^[\\u3040-\\u309F]+$/.test(qNorm);
    if (!isSemantic && isAllHira && qNorm.length <= 2) continue;
    keywords.push(kw);
  }
  const finalKeywords = keywords.length > 0 ? keywords : rawKeywords;

  let totalScore = 0;
  for (const kw of finalKeywords) {
    let kwMaxScore = computeSearchMatchScore(kw, recipe.title) * 2.0;

    if (Array.isArray(recipe.ingredients)) {
      for (const ing of recipe.ingredients) {
        kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, ing) * 1.5);
      }
    }

    if (Array.isArray(recipe.steps)) {
      for (const st of recipe.steps) {
        const stText = typeof st === 'object' ? \`\${st.title || ''} \${st.text || st.desc || ''}\` : String(st);
        kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, stText) * 0.6);
      }
    }

    if (recipe.memo) {
      kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, recipe.memo) * 0.8);
    }

    if (kwMaxScore <= 0) return 0;
    totalScore += kwMaxScore;
  }
  return totalScore;
}
`;

eval(functions);

const recipe1 = {
  title: "玄米と麦と白米",
  ingredients: ["玄米：3合（60% - 不動のメイン）", "押し麦：1合（20% - プチプチ食感をしっかり味わえる）", "白米：1合（20% - 全体のまとまり役）"],
  steps: [],
  memo: ""
};

const recipe2 = {
  title: "豆スープリゾット",
  ingredients: [
    "生米：1合（洗わずに使います）",
    "余った豆スープ＋お湯：合計で600〜800ml",
    "お好みのキノコ（しめじ、マッシュルームなど）：1/2パック",
    "粉チーズ、粗挽き黒こしょう：お好みで",
    "フライパンにオリーブオイル（大さじ1）とみじん切りにしたニンニク（1片）を入れ、弱火で香りを出す"
  ],
  steps: [],
  memo: ""
};

console.log("ウニ vs Recipe 1:", computeRecipeSemanticScore(recipe1, "ウニ"));
console.log("ウニ vs Recipe 2:", computeRecipeSemanticScore(recipe2, "ウニ"));
