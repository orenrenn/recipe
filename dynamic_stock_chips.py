with open('index.html', 'r') as f:
    text = f.read()

# 1. Update HTML container for AI stock chips
old_html = '''          <!-- 📌 使いたい食材・キーワード指定 -->
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
          </div>'''

new_html = '''          <!-- 📌 使いたい食材・キーワード指定 -->
          <div style="margin-bottom: 16px; background: white; padding: 12px; border-radius: 12px; border: 1px solid var(--border);">
            <div style="font-size: 0.82rem; font-weight: bold; color: var(--primary-dark); margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
              <span>📌 使いたい食材・キーワード (任意)</span>
              <span style="font-size: 0.7rem; font-weight: normal; color: #888;">タップでオン/オフ選択できます</span>
            </div>
            <input type="text" id="ai-required-ingredients" class="form-input" placeholder="指定したい食材やテーマを入力..." style="width: 100%; font-size: 0.9rem; padding: 8px 12px;" oninput="renderAiStockChips()">
            <div style="margin-top: 8px;">
              <div style="font-size: 0.72rem; color: #888; margin-bottom: 4px;">ストック食材からワンタップ選択:</div>
              <div id="ai-stock-chips-container" style="display: flex; flex-wrap: wrap; gap: 6px;"></div>
            </div>
          </div>'''

if old_html in text:
    text = text.replace(old_html, new_html)
    print("HTML updated for dynamic AI stock chips!")
else:
    print("Could not find old_html in text")

# 2. Update JS functions (renderAiStockChips & toggleAiKeyword)
old_js = '''    window.appendAiKeyword = function (keyword) {
      const input = document.getElementById('ai-required-ingredients');
      if (!input) return;
      const current = input.value.trim();
      if (!current) {
        input.value = keyword;
      } else if (!current.includes(keyword)) {
        input.value = current + '、' + keyword;
      }
    };'''

new_js = '''    window.renderAiStockChips = function () {
      const container = document.getElementById('ai-stock-chips-container');
      if (!container) return;

      const input = document.getElementById('ai-required-ingredients');
      const currentVal = input ? input.value : '';
      const currentItems = currentVal.split(/[、,]/).map(s => s.trim()).filter(Boolean);

      container.innerHTML = '';

      if (!refrigeratorIngredients || refrigeratorIngredients.length === 0) {
        container.innerHTML = '<span style="font-size: 0.75rem; color: #aaa;">ストックに食材が登録されていません</span>';
        return;
      }

      refrigeratorIngredients.forEach(ingName => {
        const isSelected = currentItems.includes(ingName);
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pill';
        btn.style.fontSize = '0.75rem';
        btn.style.padding = '4px 10px';
        btn.style.cursor = 'pointer';
        btn.style.transition = 'all 0.2s';

        if (isSelected) {
          btn.style.background = 'var(--primary)';
          btn.style.color = 'white';
          btn.style.border = 'none';
          btn.style.fontWeight = 'bold';
          btn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.15)';
          btn.textContent = `✓ ${ingName}`;
        } else {
          btn.style.background = '#F8FAFC';
          btn.style.color = '#475569';
          btn.style.border = '1px solid #E2E8F0';
          btn.textContent = `＋ ${ingName}`;
        }

        btn.onclick = () => {
          toggleAiKeyword(ingName);
        };

        container.appendChild(btn);
      });
    };

    window.toggleAiKeyword = function (keyword) {
      const input = document.getElementById('ai-required-ingredients');
      if (!input) return;

      let items = input.value.split(/[、,]/).map(s => s.trim()).filter(Boolean);

      if (items.includes(keyword)) {
        items = items.filter(i => i !== keyword);
      } else {
        items.push(keyword);
      }

      input.value = items.join('、');
      renderAiStockChips();
    };'''

if old_js in text:
    text = text.replace(old_js, new_js)
    print("JS renderAiStockChips and toggleAiKeyword added!")
else:
    print("Could not find old_js in text")

# 3. Call renderAiStockChips in switchSuggestSubTab when mode === 'ai'
old_tab_switch = '''        panelLocal.style.display = 'none';
        panelAi.style.display = 'block';
      }
    };'''

new_tab_switch = '''        panelLocal.style.display = 'none';
        panelAi.style.display = 'block';
        renderAiStockChips();
      }
    };'''

if old_tab_switch in text:
    text = text.replace(old_tab_switch, new_tab_switch)
    print("switchSuggestSubTab updated with renderAiStockChips call!")
else:
    print("Could not find old_tab_switch in text")

# 4. Call renderAiStockChips at end of renderFridgeUI
old_fridge_end = '''      suggestLocalRecipes();
    };'''

new_fridge_end = '''      suggestLocalRecipes();
      renderAiStockChips();
    };'''

if old_fridge_end in text:
    text = text.replace(old_fridge_end, new_fridge_end)
    print("renderFridgeUI updated with renderAiStockChips call!")
else:
    print("Could not find old_fridge_end in text")

with open('index.html', 'w') as f:
    f.write(text)

