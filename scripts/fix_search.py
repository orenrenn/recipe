import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The start of the block to delete
start_str = "    const KANJI_READINGS = {"
start_idx = content.find(start_str)

# The end of the block (end of computeRecipeSemanticScore)
end_str = "    // Filter & Render List with Multi-Criteria Sorting"
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    new_search_logic = """
    function computeSearchMatchScore(queryWord, targetText) {
      if (!queryWord || !targetText) return 0;

      const qNorm = normalizeJapaneseText(queryWord);
      const tNorm = normalizeJapaneseText(targetText);
      if (!qNorm || !tNorm) return 0;

      let maxScore = 0;

      // --- Layer 0: Direct normalized substring match ---
      if (tNorm.includes(qNorm)) maxScore = 10.0;

      // --- Layer 1: Hiragana-unified substring match ---
      const qHira = toHiragana(qNorm);
      const tHira = toHiragana(tNorm);
      if (tHira.includes(qHira) && maxScore < 9.0) maxScore = 9.0;

      // --- Layer 2: Offline Category Semantic Search ---
      if (window.FOOD_VECTORS) {
        let maxSemanticSim = 0;
        for (const qWord in window.FOOD_VECTORS) {
          // Check if query contains dict word, OR dict word contains query (e.g. "あいびき" matches "あいびき肉")
          if (qNorm.includes(qWord) || qHira.includes(toHiragana(qWord)) || qWord.includes(qNorm) || toHiragana(qWord).includes(qHira)) {
            const qVec = window.FOOD_VECTORS[qWord];
            for (const tWord in window.FOOD_VECTORS) {
              if (tNorm.includes(tWord) || tHira.includes(toHiragana(tWord))) {
                const tVec = window.FOOD_VECTORS[tWord];
                let dot = 0;
                for (let i = 0; i < qVec.length; i++) {
                  dot += qVec[i] * tVec[i];
                }
                if (dot > maxSemanticSim) maxSemanticSim = dot;
              }
            }
          }
        }
        
        // Exact category match (dot == 1.0) gives semanticScore = 7.0
        if (maxSemanticSim >= 0.55) {
          const semanticScore = (maxSemanticSim - 0.5) * 14.0;
          maxScore = Math.max(maxScore, semanticScore);
        }
      }

      return maxScore >= 1.8 ? maxScore : 0;
    }

    function computeRecipeSemanticScore(recipe, queryStr) {
      const keywords = queryStr.trim().split(/\s+/).filter(k => k.length > 0);
      if (keywords.length === 0) return 1.0;
      let totalScore = 0;

      for (const kw of keywords) {
        let kwMaxScore = computeSearchMatchScore(kw, recipe.title) * 2.0;

        if (Array.isArray(recipe.ingredients)) {
          for (const ing of recipe.ingredients) {
            kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, ing) * 1.5);
          }
        }

        if (Array.isArray(recipe.steps)) {
          for (const st of recipe.steps) {
            const stText = typeof st === 'object' ? `${st.title || ''} ${st.text || st.desc || ''}` : String(st);
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

"""
    
    new_content = content[:start_idx] + new_search_logic + content[end_idx:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced search logic!")
else:
    print("Could not find start or end markers.")
