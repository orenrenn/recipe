with open('index.html', 'r') as f:
    lines = f.readlines()

correct_lines = """            if (isTriviallyAvailable(ing)) return;
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

      s"""

# Replace lines 3825 to 3851 (index 3825 to 3851)
new_lines = lines[:3825] + [correct_lines + "\n"] + lines[3851:]

with open('index.html', 'w') as f:
    f.write("".join(new_lines))

print("Fixed!")
