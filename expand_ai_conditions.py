with open('index.html', 'r') as f:
    text = f.read()

import re

# 1. Replace the HTML form card inside subpanel-suggest-ai
old_form = '''          <!-- Group 1: ジャンル -->
          <div style="margin-bottom: 12px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🍱 ジャンル
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="おまかせ" checked> 🎲
                おまかせ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="和食"> 🍱 和食</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="洋食"> 🍝 洋食</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="中華"> 🥟 中華</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="エスニック"> 🌮 エスニック</label>
            </div>
          </div>

          <!-- Group 2: 気分・テーマ (既存項目保持) -->
          <div style="margin-bottom: 12px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">✨ 気分・テーマ
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="指定なし" checked> 🎲 指定なし</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="おつまみ"> 🥂 おつまみ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="時短・ズボラ"> ⏱️ 時短・ズボラ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="がっつり"> 🍖 がっつり</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="さっぱり・ヘルシー"> 🥗 さっぱり</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="辛いもの"> 🌶️ 辛いもの</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="子供が喜ぶ"> 👶 子供向け</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="スイーツ・おやつ"> 🍰 スイーツ</label>
            </div>
          </div>

          <!-- Group 3: 調理スタイル -->
          <div style="margin-bottom: 12px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🍳 調理スタイル
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="指定なし" checked> 🎲
                指定なし</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="フライパン1つ"> 🍳 ワンパン</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="電子レンジのみ"> ⚡ レンジのみ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="じっくり煮込み・本格"> 🍲 本格調理</label>
            </div>
          </div>

          <!-- Group 4: 提案数 -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🔢 提案数
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="3"> 3個 (高速)</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="5"> 5個</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="10" checked> 10個 (詳細)</label>
            </div>
          </div>

          <!-- Group 5: AIモデル -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🤖 AIモデル
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="auto" checked> 🎲
                自動最適化</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="flash"> ⚡ Flash
                (高速)</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="pro"> 🧠 Pro
                (高品質)</label>
            </div>
          </div>'''

new_form = '''          <!-- Group 1: ジャンル -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🍱 料理ジャンル</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="おまかせ" checked> 🎲 おまかせ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="和食"> 🍱 和食</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="洋食"> 🍝 洋食</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="中華"> 🥟 中華</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="エスニック・アジアン"> 🌮 エスニック</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="イタリアン"> 🇮🇹 イタリアン</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiGenre" value="韓国料理"> 🇰🇷 韓国料理</label>
            </div>
          </div>

          <!-- Group 2: 気分・目的 -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">✨ 気分・目的</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="指定なし" checked> 🎲 指定なし</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="時短・ズボラ (10分以内)"> ⏱️ 時短・ズボラ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="おつまみ・家飲み"> 🥂 おつまみ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="がっつりスタミナ"> 🍖 スタミナ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="さっぱり・ヘルシー"> 🥗 ヘルシー</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="旨辛・スパイス"> 🌶️ 旨辛</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="子供が喜ぶ味付け"> 👶 子供向け</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="節約・コスパ"> 💰 節約・コスパ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="お弁当のおかず"> 🍱 お弁当</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiMood" value="スイーツ・おやつ"> 🍰 スイーツ</label>
            </div>
          </div>

          <!-- Group 3: 調理スタイル -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🍳 調理スタイル・道具</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="指定なし" checked> 🎲 指定なし</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="フライパン1つ (ワンパン)"> 🍳 ワンパン</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="電子レンジのみ"> ⚡ レンジのみ</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="包丁・火いらず"> 🫕 包丁・火いらず</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="火を使わない (和えるだけ)"> 🥗 火を使わない</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStyle" value="じっくり煮込み・本格調理"> 🍲 本格煮込み</label>
            </div>
          </div>

          <!-- Group 4: 食材の買い足し方針 -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🛒 食材の買い足し方針</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiStrictness" value="ストック優先 (不足食材最小限)" checked> 🟢 ストック重視</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStrictness" value="定番調味料・野菜の買い足しOK"> 🟡 定番品の買い足しOK</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiStrictness" value="自由に追加食材OK"> 🔴 買い足し自由</label>
            </div>
          </div>

          <!-- Group 5: 人数 -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">👥 人数</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiServings" value="1人分"> 👤 1人分</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiServings" value="2人分" checked> 👥 2人分</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiServings" value="3〜4人分"> 👨‍👩‍👧 3〜4人分</label>
            </div>
          </div>

          <!-- Group 6: 提案数 -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🔢 提案数</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="3"> ⚡ 3個 (高速)</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="5" checked> 🍱 5個 (標準)</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiCount" value="10"> 📚 10個 (たっぷり)</label>
            </div>
          </div>

          <!-- Group 7: AIモデル -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 0.8rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px;">🤖 AIモデル</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" class="ai-group-chips">
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="auto" checked> 🎲 自動最適化</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="flash"> ⚡ Flash (高速)</label>
              <label class="pill ai-theme-label"><input type="radio" name="aiModelSelect" value="pro"> 🧠 Pro (高品質)</label>
            </div>
          </div>'''

if old_form in text:
    text = text.replace(old_form, new_form)
    print("Form HTML updated successfully!")
else:
    print("Could not find old_form in text")

# 2. Update JS doGenerateAI condition extraction
old_js = '''      const genreEl = document.querySelector('input[name="aiGenre"]:checked');
      const moodEl = document.querySelector('input[name="aiMood"]:checked');
      const styleEl = document.querySelector('input[name="aiStyle"]:checked');
      const countEl = document.querySelector('input[name="aiCount"]:checked');

      const genre = genreEl ? genreEl.value : "おまかせ";
      const mood = moodEl ? moodEl.value : "指定なし";
      const style = styleEl ? styleEl.value : "指定なし";
      const count = countEl ? countEl.value : "10";

      let conditions = [];
      if (genre !== 'おまかせ') conditions.push(`ジャンル: ${genre}`);
      if (mood !== '指定なし') conditions.push(`気分・テーマ: ${mood}`);
      if (style !== '指定なし') conditions.push(`調理スタイル: ${style}`);'''

new_js = '''      const genreEl = document.querySelector('input[name="aiGenre"]:checked');
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

if old_js in text:
    text = text.replace(old_js, new_js)
    print("JS condition extraction updated successfully!")
else:
    print("Could not find old_js in text")

with open('index.html', 'w') as f:
    f.write(text)

