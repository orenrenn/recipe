with open('index.html', 'r') as f:
    text = f.read()

# 1. Add input field to HTML form card
old_form_start = '''        <div class="form-card" style="background: linear-gradient(135deg, #FFF0F2 0%, #FFFDF9 100%); text-align: left;">
          <p style="font-size: 0.85rem; color: #666; margin-bottom: 14px; text-align: center;">※
            ストックの食材と好みの条件に合わせて、AIがオリジナルレシピを考えます。</p>

          <!-- Group 1: ジャンル -->'''

new_form_start = '''        <div class="form-card" style="background: linear-gradient(135deg, #FFF0F2 0%, #FFFDF9 100%); text-align: left;">
          <p style="font-size: 0.85rem; color: #666; margin-bottom: 14px; text-align: center;">※
            ストックの食材と好みの条件に合わせて、AIがオリジナルレシピを考えます。</p>

          <!-- 📌 使いたい食材・キーワード指定 -->
          <div style="margin-bottom: 16px; background: white; padding: 12px; border-radius: 12px; border: 1px solid var(--border);">
            <div style="font-size: 0.82rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
              <span>📌 使いたい食材・キーワード (任意)</span>
              <span style="font-size: 0.7rem; font-weight: normal; color: #888;">例: パスタ、アボカド、豆腐 など</span>
            </div>
            <input type="text" id="ai-required-ingredients" class="form-input" placeholder="指定したい食材やテーマを入力..." style="width: 100%; font-size: 0.9rem; padding: 8px 12px;">
            <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px;">
              <span style="font-size: 0.72rem; color: #888; align-self: center; margin-right: 4px;">ワンタップ追加:</span>
              <button type="button" class="pill" onclick="appendAiKeyword('パスタ')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">🍝 パスタ</button>
              <button type="button" class="pill" onclick="appendAiKeyword('うどん')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">🍜 うどん</button>
              <button type="button" class="pill" onclick="appendAiKeyword('食パン')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">🍞 食パン</button>
              <button type="button" class="pill" onclick="appendAiKeyword('豆腐')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">⬜ 豆腐</button>
              <button type="button" class="pill" onclick="appendAiKeyword('アボカド')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">🥑 アボカド</button>
              <button type="button" class="pill" onclick="appendAiKeyword('トマト缶')" style="font-size: 0.75rem; padding: 3px 8px; cursor: pointer; border: 1px solid #E2E8F0; background: #F8FAFC;">🥫 トマト缶</button>
            </div>
          </div>

          <!-- Group 1: ジャンル -->'''

if old_form_start in text:
    text = text.replace(old_form_start, new_form_start)
    print("Form HTML updated with required ingredient input!")
else:
    print("Could not find old_form_start in text")

# 2. Add appendAiKeyword to window
js_target = '    window.switchSuggestSubTab = function (mode) {'
js_addition = '''    window.appendAiKeyword = function (keyword) {
      const input = document.getElementById('ai-required-ingredients');
      if (!input) return;
      const current = input.value.trim();
      if (!current) {
        input.value = keyword;
      } else if (!current.includes(keyword)) {
        input.value = current + '、' + keyword;
      }
    };

'''

if js_target in text:
    text = text.replace(js_target, js_addition + js_target)
    print("JS appendAiKeyword function added successfully!")
else:
    print("Could not find js_target in text")

# 3. Update doGenerateAI logic
old_js_cond = '''      const genreEl = document.querySelector('input[name="aiGenre"]:checked');
      const moodEl = document.querySelector('input[name="aiMood"]:checked');
      const styleEl = document.querySelector('input[name="aiStyle"]:checked');
      const strictnessEl = document.querySelector('input[name="aiStrictness"]:checked');
      const servingsEl = document.querySelector('input[name="aiServings"]:checked');
      const countEl = document.querySelector('input[name="aiCount"]:checked');

      const genre = genreEl ? genreEl.value : "おまかせ";
      const mood = moodEl ? moodEl.value : "指定なし";
      const style = styleEl ? styleEl.value : "指定なし";
      const strictness = strictnessEl ? strictnessEl.value : "ストック優先";
      const servings = servingsEl ? servingsEl.value : "2人分";
      const count = countEl ? countEl.value : "5";

      let conditions = [];
      if (genre !== 'おまかせ') conditions.push(`ジャンル: ${genre}`);
      if (mood !== '指定なし') conditions.push(`気分・目的: ${mood}`);
      if (style !== '指定なし') conditions.push(`調理スタイル: ${style}`);
      conditions.push(`食材の買い足し方針: ${strictness}`);
      conditions.push(`分量: ${servings}`);'''

new_js_cond = '''      const requiredIngEl = document.getElementById('ai-required-ingredients');
      const requiredIng = requiredIngEl ? requiredIngEl.value.trim() : '';

      const genreEl = document.querySelector('input[name="aiGenre"]:checked');
      const moodEl = document.querySelector('input[name="aiMood"]:checked');
      const styleEl = document.querySelector('input[name="aiStyle"]:checked');
      const strictnessEl = document.querySelector('input[name="aiStrictness"]:checked');
      const servingsEl = document.querySelector('input[name="aiServings"]:checked');
      const countEl = document.querySelector('input[name="aiCount"]:checked');

      const genre = genreEl ? genreEl.value : "おまかせ";
      const mood = moodEl ? moodEl.value : "指定なし";
      const style = styleEl ? styleEl.value : "指定なし";
      const strictness = strictnessEl ? strictnessEl.value : "ストック優先";
      const servings = servingsEl ? servingsEl.value : "2人分";
      const count = countEl ? countEl.value : "5";

      let conditions = [];
      if (requiredIng) conditions.push(`【使いたい必須食材・テーマ】: ${requiredIng}`);
      if (genre !== 'おまかせ') conditions.push(`ジャンル: ${genre}`);
      if (mood !== '指定なし') conditions.push(`気分・目的: ${mood}`);
      if (style !== '指定なし') conditions.push(`調理スタイル: ${style}`);
      conditions.push(`食材の買い足し方針: ${strictness}`);
      conditions.push(`分量: ${servings}`);'''

if old_js_cond in text:
    text = text.replace(old_js_cond, new_js_cond)
    print("JS condition extraction updated with requiredIng!")
else:
    print("Could not find old_js_cond in text")

# 4. Update prompt with requiredInstruction
old_prompt_start = '        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）を優先的に活用し、【${conditionStr}】という条件に沿った美味しく実用的な料理レシピを${count}個の異なるバリエーションで提案してください。'
new_prompt_start = '''        const requiredInstruction = requiredIng ? `・【最優先・必須食材】: 指定された食材「${requiredIng}」を必ず使用したレシピを提案してください。\\n` : '';
        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）を優先的に活用し、【${conditionStr}】という条件に沿った美味しく実用的な料理レシピを${count}個の異なるバリエーションで提案してください。
${requiredInstruction}'''

if old_prompt_start in text:
    text = text.replace(old_prompt_start, new_prompt_start)
    print("Prompt updated with requiredInstruction!")
else:
    print("Could not find old_prompt_start in text")

with open('index.html', 'w') as f:
    f.write(text)

