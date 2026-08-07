with open('index.html', 'r') as f:
    text = f.read()

import re
pattern = r"      document\.getElementById\('btn-generate-ai'\)\.disabled = true;.*?\]\`;"

replacement = '''      document.getElementById('btn-generate-ai').disabled = true;
      document.getElementById('btn-generate-ai-another').disabled = true;
      
      if (!isAnother) {
        document.getElementById('ai-loading-spinner').style.display = 'block';
        document.getElementById('suggest-ai-grid').innerHTML = '';
        document.getElementById('suggest-ai-controls').style.display = 'none';
      } else {
        document.getElementById('btn-generate-ai-another').style.display = 'none';
        document.getElementById('ai-loading-spinner-another').style.display = 'block';
      }

      try {
        const genAI = new GoogleGenerativeAI(geminiApiKey);
        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）をなるべく活用し、【${conditionStr}】という条件に沿った美味しい料理のレシピを${count}個の異なるバリエーションで提案してください。不足している一般的な調味料や多少の追加食材は使って構いません。
${excludeStr}出力は以下のJSON形式の配列のみを返してください。必ず有効なJSONにしてください。
[
  {
    "title": "料理名",
    "category": "主菜",
    "servings": 2,
    "ingredients": ["材料名1: 分量1", "材料名2: 分量2"], // ※使用するすべての材料・調味料（不足分も含む）を「食材名: 分量」の形式で記載してください。例：「豚肉: 200g」
    "missing_ingredients": ["買い足す必要がある材料名1", "材料名2"], // ※上記のうち、手元にない不足分の材料名のみ記載してください
    "steps": ["手順1", "手順2"]
  }
]\`;'''

if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    with open('index.html', 'w') as f:
        f.write(text)
    print("Fixed doGenerateAI UI and prompt!")
else:
    print("Could not find doGenerateAI block.")
