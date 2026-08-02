with open('index.html', 'r') as f:
    text = f.read()

# 1. Update HTML structure of suggest-section
old_html = '''      <!-- サジェストセクション -->
      <div id="suggest-section" style="margin-top: 16px;">
        <div
          style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 2px solid var(--primary-light); padding-bottom: 4px;">
          <h3 style="font-size: 1.05rem; color: #555; margin: 0;">📖 自分のレシピから作れるもの</h3>
          <select id="suggest-tag-select" class="form-input"
            style="width: auto; padding: 4px 8px; font-size: 0.8rem; border-color: var(--primary-light);"
            onchange="suggestLocalRecipes()">
            <option value="">すべてのタグ</option>
          </select>
        </div>
        <div id="suggest-local-grid" class="recipe-grid" style="margin-bottom: 24px;"></div>

        <h3
          style="font-size: 1.05rem; color: #555; margin-bottom: 12px; border-bottom: 2px solid var(--primary-light); padding-bottom: 4px;">
          ✨ AIに新しいレシピを提案してもらう</h3>'''

new_html = '''      <!-- サジェストセクション (タブ切り替え化) -->
      <div id="suggest-section" style="margin-top: 24px; border-top: 2px dashed var(--border); padding-top: 16px;">
        <!-- サブタブヘッダー -->
        <div style="display: flex; gap: 8px; margin-bottom: 16px; background: var(--border); padding: 4px; border-radius: 14px;">
          <button id="subtab-suggest-local" onclick="switchSuggestSubTab('local')"
            style="flex: 1; padding: 10px 12px; border-radius: 10px; font-weight: bold; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; border: none; background: var(--primary); color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📖 マイレシピから提案</button>
          <button id="subtab-suggest-ai" onclick="switchSuggestSubTab('ai')"
            style="flex: 1; padding: 10px 12px; border-radius: 10px; font-weight: bold; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; border: none; background: transparent; color: var(--text-muted);">✨ AI提案レシピ</button>
        </div>

        <!-- サブパネル 1: マイレシピから提案 -->
        <div id="subpanel-suggest-local">
          <div
            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 2px solid var(--primary-light); padding-bottom: 4px;">
            <h3 style="font-size: 1.05rem; color: #555; margin: 0;">📖 自分のレシピから作れるもの</h3>
            <select id="suggest-tag-select" class="form-input"
              style="width: auto; padding: 4px 8px; font-size: 0.8rem; border-color: var(--primary-light);"
              onchange="suggestLocalRecipes()">
              <option value="">すべてのタグ</option>
            </select>
          </div>
          <div id="suggest-local-grid" class="recipe-grid" style="margin-bottom: 24px;"></div>
        </div>

        <!-- サブパネル 2: AI提案レシピ -->
        <div id="subpanel-suggest-ai" style="display: none;">
          <h3
            style="font-size: 1.05rem; color: #555; margin-bottom: 12px; border-bottom: 2px solid var(--primary-light); padding-bottom: 4px;">
            ✨ AIに新しいレシピを提案してもらう</h3>'''

if old_html in text:
    text = text.replace(old_html, new_html)
    print("HTML subtabs added successfully!")
else:
    print("Could not find old_html in index.html")

# Close subpanel-suggest-ai at the end of suggest-section
old_end = '''          <div id="ai-loading-spinner-another" style="display: none; text-align: center; margin-top: 16px; color: var(--primary);">
            <div style="font-size: 1.5rem; animation: spin 1s infinite linear; display: inline-block;">🍳</div>
            <p style="font-size: 0.9rem; font-weight: bold; margin-top: 8px;">別のレシピを考えています...</p>
          </div>
        </div>
      </div>
    </div>'''

new_end = '''          <div id="ai-loading-spinner-another" style="display: none; text-align: center; margin-top: 16px; color: var(--primary);">
            <div style="font-size: 1.5rem; animation: spin 1s infinite linear; display: inline-block;">🍳</div>
            <p style="font-size: 0.9rem; font-weight: bold; margin-top: 8px;">別のレシピを考えています...</p>
          </div>
        </div>
        </div> <!-- End subpanel-suggest-ai -->
      </div>
    </div>'''

if old_end in text:
    text = text.replace(old_end, new_end)
    print("Subpanel close tag added successfully!")
else:
    print("Could not find old_end in index.html")

# Add JS switchSuggestSubTab function
js_target = '    window.suggestLocalRecipes = function suggestLocalRecipes() {'

js_addition = '''    window.switchSuggestSubTab = function (mode) {
      const btnLocal = document.getElementById('subtab-suggest-local');
      const btnAi = document.getElementById('subtab-suggest-ai');
      const panelLocal = document.getElementById('subpanel-suggest-local');
      const panelAi = document.getElementById('subpanel-suggest-ai');

      if (!btnLocal || !btnAi || !panelLocal || !panelAi) return;

      if (mode === 'local') {
        btnLocal.style.background = 'var(--primary)';
        btnLocal.style.color = 'white';
        btnLocal.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';

        btnAi.style.background = 'transparent';
        btnAi.style.color = 'var(--text-muted)';
        btnAi.style.boxShadow = 'none';

        panelLocal.style.display = 'block';
        panelAi.style.display = 'none';
      } else {
        btnAi.style.background = 'var(--primary)';
        btnAi.style.color = 'white';
        btnAi.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';

        btnLocal.style.background = 'transparent';
        btnLocal.style.color = 'var(--text-muted)';
        btnLocal.style.boxShadow = 'none';

        panelLocal.style.display = 'none';
        panelAi.style.display = 'block';
      }
    };

'''

if js_target in text:
    text = text.replace(js_target, js_addition + js_target)
    print("JS function switchSuggestSubTab added successfully!")
else:
    print("Could not find js_target in index.html")

with open('index.html', 'w') as f:
    f.write(text)

