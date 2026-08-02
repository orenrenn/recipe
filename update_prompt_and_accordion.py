with open('index.html', 'r') as f:
    text = f.read()

# 1. Remove 'open' attribute from fridge master accordion
old_acc = '<details id="fridge-master-accordion" open style="margin-bottom: 16px;">'
new_acc = '<details id="fridge-master-accordion" style="margin-bottom: 16px;">'

if old_acc in text:
    text = text.replace(old_acc, new_acc)
    print("Accordion set to collapsed by default!")
else:
    print("Could not find old_acc in text")

# 2. Update prompt for detailed step-by-step instructions
old_prompt = '''        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）をなるべく活用し、【${conditionStr}】という条件に沿った美味しい料理のレシピを${count}個の異なるバリエーションで提案してください。不足している一般的な調味料や多少の追加食材は使って構いません。
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
]`;'''

new_prompt = '''        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）を優先的に活用し、【${conditionStr}】という条件に沿った美味しく実用的な料理レシピを${count}個の異なるバリエーションで提案してください。

【作り方（steps）に関する重要指示】
・手順は大雑把にまとめず、初心者でもスムーズに調理できるよう「下ごしらえ」「火加減（弱火・中火・強火など）」「具体的な調理時間（例: 〇分ほど炒める）」「仕上がり目安（例: きつね色になるまで）」を明記して、丁寧かつ具体的にステップ分けして書いてください。

${excludeStr}出力は以下のJSON形式の配列のみを返してください。必ず有効なJSONにしてください。
[
  {
    "title": "料理名",
    "category": "主菜",
    "servings": 2,
    "ingredients": ["材料名1: 分量1", "材料名2: 分量2"], // ※使用するすべての材料・調味料（不足分も含む）を「食材名: 分量」の形式で記載してください。例：「豚肉: 200g」
    "missing_ingredients": ["買い足す必要がある材料名1", "材料名2"], // ※上記のうち、手元にない不足分の材料のみ記載してください
    "steps": [
      "下ごしらえ: 豚肉は一口大に切り、玉ねぎは5mm幅の薄切りにする。",
      "炒める: フライパンに油小さじ1を熱し、中火で豚肉を2分ほど炒める。",
      "煮立てる・仕上げ: 玉ねぎと調味料を加え、弱火で蓋をして約5分煮込み、全体に味がなじんだら火を止める。"
    ]
  }
]`;'''

if old_prompt in text:
    text = text.replace(old_prompt, new_prompt)
    print("AI prompt updated with detailed instruction steps!")
else:
    print("Could not find old_prompt in text")

with open('index.html', 'w') as f:
    f.write(text)

