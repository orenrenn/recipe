with open('index.html', 'r') as f:
    text = f.read()

import re

# Find the corrupted block
corrupted_pattern = r'if \(r\.ingredients\) \{\s*r\.ingredients\.forEach\(ing => \{\s*if \(isTriviallyAvailab.*?\}\s*\]`;cored\.sort'

replacement = '''if (r.ingredients) {
          r.ingredients.forEach(ing => {
            if (isTriviallyAvailable(ing)) return;
            const isSeasoning = isSeasoningIngredient(ing);
            if (!isSeasoning) totalMainCount++;

            const isMatch = isIngredientInStock(ing, refrigeratorIngredients, normFCache);

            if (isMatch) {
              if (!isSeasoning) mainMatchCount++;
            } else {
              missingAllList.push(ing);
              if (isSeasoning) seasoningCount++;
            }
          });
        }
        return { item: r, matchCount: mainMatchCount, totalMainCount: totalMainCount, missing: missingAllList, seasoningCount: seasoningCount };
      }).filter(res => {
        if (res.totalMainCount > 0 && res.matchCount === 0) return false;
        const missingMainCount = res.missing.length - res.seasoningCount;
        if (res.totalMainCount > 0) {
          if (missingMainCount > 0) return false;
        }
        return true;
      });

      scored.sort'''

if re.search(corrupted_pattern, text, re.DOTALL):
    text = re.sub(corrupted_pattern, replacement, text, flags=re.DOTALL)
    print("Fixed corrupted suggestLocalRecipes block!")
else:
    print("Could not find corrupted block.")

with open('index.html', 'w') as f:
    f.write(text)

