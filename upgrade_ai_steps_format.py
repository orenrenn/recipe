with open('index.html', 'r') as f:
    text = f.read()

# 1. Update AI Prompt JSON structure in doGenerateAI
old_prompt = '''    "steps": [
      "下ごしらえ: 豚肉は一口大に切り、玉ねぎは5mm幅の薄切りにする。",
      "炒める: フライパンに油小さじ1を熱し、中火で豚肉を2分ほど炒める。",
      "煮立てる・仕上げ: 玉ねぎと調味料を加え、弱火で蓋をして約5分煮込み、全体に味がなじんだら火を止める。"
    ]'''

new_prompt = '''    "steps": [
      { "title": "下ごしらえ", "text": "豚肉は一口大に切り、玉ねぎは5mm幅の薄切りにする。" },
      { "title": "炒める", "text": "フライパンに油小さじ1を熱し、中火で豚肉を2分ほど炒める。" },
      { "title": "煮立てる・仕上げ", "text": "玉ねぎと調味料を加え、弱火で蓋をして約5分煮込み、全体に味がなじんだら火を止める。" }
    ]'''

if old_prompt in text:
    text = text.replace(old_prompt, new_prompt)
    print("Updated AI prompt JSON schema for steps!")
else:
    print("Could not find old_prompt in text")

# 2. Update AI recipe step normalization in recipes.forEach
old_foreach = '''        recipes.forEach(r => {
          if (r.title) aiGeneratedTitles.push(r.title);
          r.isAiGenerated = true;'''

new_foreach = '''        recipes.forEach(r => {
          if (r.title) aiGeneratedTitles.push(r.title);
          r.isAiGenerated = true;
          if (Array.isArray(r.steps)) {
            r.steps = r.steps.map(step => {
              if (typeof step === 'object' && step !== null) return { title: step.title || '', text: step.text || step.desc || '' };
              let s = String(step).replace(/^[0-9０-９]+[\\\.．\\s]*/, '').trim();
              if (s.includes(':') || s.includes('：')) {
                const parts = s.split(/[:：]/);
                return { title: parts[0].trim(), text: parts.slice(1).join(':').trim() };
              }
              return { title: '', text: s };
            });
          }'''

if old_foreach in text:
    text = text.replace(old_foreach, new_foreach)
    print("Updated recipes.forEach for step normalization!")
else:
    print("Could not find old_foreach in text")

# 3. Update openRecipeDetail step rendering
old_detail_step = '''          if (typeof step === 'object' && step !== null) {
            stepTitle = step.title || '';
            stepText = step.text || step.desc || '';
          } else if (typeof step === 'string') {
            const lines = step.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length >= 2) {
              stepTitle = lines[0];
              stepText = lines.slice(1).join('\\n');
            } else {
              stepText = step;
            }
          }'''

new_detail_step = '''          if (typeof step === 'object' && step !== null) {
            stepTitle = step.title || '';
            stepText = step.text || step.desc || '';
          } else if (typeof step === 'string') {
            let s = step.replace(/^[0-9０-９]+[\\\.．\\s]*/, '').trim();
            if (s.includes('\\n')) {
              const lines = s.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
              stepTitle = lines[0];
              stepText = lines.slice(1).join('\\n');
            } else if (s.includes(':') || s.includes('：')) {
              const parts = s.split(/[:：]/);
              stepTitle = parts[0].trim();
              stepText = parts.slice(1).join(':').trim();
            } else {
              stepText = s;
            }
          }'''

if old_detail_step in text:
    text = text.replace(old_detail_step, new_detail_step)
    print("Updated openRecipeDetail step parsing!")
else:
    print("Could not find old_detail_step in text")

# 4. Update btn-save-ai-recipe step saving
old_save_steps = 'steps: currentDetailRecipe.steps || [],'
new_save_steps = '''steps: (currentDetailRecipe.steps || []).map(step => {
            if (typeof step === 'object' && step !== null) {
              return { title: step.title || '', text: step.text || step.desc || '' };
            }
            let s = String(step).replace(/^[0-9０-９]+[\\\.．\\s]*/, '').trim();
            if (s.includes(':') || s.includes('：')) {
              const parts = s.split(/[:：]/);
              return { title: parts[0].trim(), text: parts.slice(1).join(':').trim() };
            }
            return { title: '', text: s };
          }),'''

if old_save_steps in text:
    text = text.replace(old_save_steps, new_save_steps)
    print("Updated btn-save-ai-recipe step saving!")
else:
    print("Could not find old_save_steps in text")

with open('index.html', 'w') as f:
    f.write(text)

