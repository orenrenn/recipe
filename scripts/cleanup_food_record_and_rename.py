with open('index.html', 'r') as f:
    text = f.read()

# 1. Title & Meta & Logo & Manifest
text = text.replace('<title>もぐもぐダイアリー 📓</title>', '<title>もぐもぐレシピ 🍳</title>')
text = text.replace('<meta name="apple-mobile-web-app-title" content="もぐダイアリー">', '<meta name="apple-mobile-web-app-title" content="もぐもぐレシピ">')
text = text.replace('<span>もぐもぐダイアリー</span>', '<span>もぐもぐレシピ</span>')
text = text.replace('"name": "もぐもぐダイアリー"', '"name": "もぐもぐレシピ"')
text = text.replace('"short_name": "もぐダイアリー"', '"short_name": "もぐもぐレシピ"')
text = text.replace('<span>📓✨</span>', '<span>🍳✨</span>')

# 2. Mode Switcher HTML (Remove mode-food-record)
old_switcher = '''  <div class="mode-switcher-container">
    <button id="mode-recipe" class="mode-btn active" onclick="switchAppMode('recipe')">
      <span class="mode-icon">🍳</span> レシピ
    </button>
    <button id="mode-food-record" class="mode-btn" onclick="switchAppMode('food_record')">
      <span class="mode-icon">🍽️</span> ごはんメモ
    </button>
    <button id="mode-fridge" class="mode-btn" onclick="switchAppMode('fridge')">
      <span class="mode-icon">🧺</span> 食材ストック
    </button>
  </div>'''

new_switcher = '''  <div class="mode-switcher-container">
    <button id="mode-recipe" class="mode-btn active" onclick="switchAppMode('recipe')">
      <span class="mode-icon">🍳</span> レシピ
    </button>
    <button id="mode-fridge" class="mode-btn" onclick="switchAppMode('fridge')">
      <span class="mode-icon">🧺</span> 食材ストック
    </button>
  </div>'''

if old_switcher in text:
    text = text.replace(old_switcher, new_switcher)
    print("Mode switcher HTML updated!")

# 3. switchAppMode JS
old_switch_js = '''    window.switchAppMode = function (mode) {
      currentAppMode = mode;

      // Update Tab UI
      document.getElementById('mode-recipe').classList.toggle('active', mode === 'recipe');
      document.getElementById('mode-food-record').classList.toggle('active', mode === 'food_record');
      document.getElementById('mode-fridge').classList.toggle('active', mode === 'fridge');

      const isFridge = mode === 'fridge';

      if (isFridge) {
        document.querySelector('nav').style.display = 'none';
        switchPage('fridge');
        if (window.renderFridgeUI) window.renderFridgeUI();
      } else {
        document.querySelector('nav').style.display = 'flex';
        if (document.getElementById('page-fridge').classList.contains('active')) {
          switchPage('list');
        } else {
          renderRecipeList();
          if (document.getElementById('page-add').classList.contains('active')) {
            updateFormModeUI();
          }
        }
      }

      if (!isFridge) {
        const isRecipe = mode === 'recipe';
        document.getElementById('nav-list-text').innerText = isRecipe ? 'レシピ一覧' : 'メモ一覧';
        document.getElementById('nav-add-text').innerText = isRecipe ? 'レシピ登録' : 'メモする';
        document.getElementById('form-header-title').innerText = isRecipe ? '📌 基本情報' : '🍽️ メモ情報';
      }
    };'''

new_switch_js = '''    window.switchAppMode = function (mode) {
      currentAppMode = mode;

      // Update Tab UI
      document.getElementById('mode-recipe').classList.toggle('active', mode === 'recipe');
      document.getElementById('mode-fridge').classList.toggle('active', mode === 'fridge');

      const isFridge = mode === 'fridge';

      if (isFridge) {
        document.querySelector('nav').style.display = 'none';
        switchPage('fridge');
        if (window.renderFridgeUI) window.renderFridgeUI();
      } else {
        document.querySelector('nav').style.display = 'flex';
        if (document.getElementById('page-fridge').classList.contains('active')) {
          switchPage('list');
        } else {
          renderRecipeList();
          if (document.getElementById('page-add').classList.contains('active')) {
            updateFormModeUI();
          }
        }
      }

      if (!isFridge) {
        document.getElementById('nav-list-text').innerText = 'レシピ一覧';
        document.getElementById('nav-add-text').innerText = 'レシピ登録';
        document.getElementById('form-header-title').innerText = '📌 基本情報';
      }
    };'''

if old_switch_js in text:
    text = text.replace(old_switch_js, new_switch_js)
    print("switchAppMode JS updated!")

# 4. updateFormModeUI
old_form_ui = '''    function updateFormModeUI() {
      const isRecipe = currentAppMode === 'recipe';
      document.getElementById('form-group-servings').style.display = isRecipe ? 'block' : 'none';
      document.getElementById('form-card-ingredients').style.display = isRecipe ? 'block' : 'none';
      document.getElementById('form-card-steps').style.display = isRecipe ? 'block' : 'none';

      const isEdit = !!editingRecipeId;
      const typeStr = isRecipe ? 'レシピ' : 'メモ';
      document.getElementById('btn-save-content').innerHTML = `<span>💾</span> ${typeStr}を${isEdit ? '更新' : '保存'}する`;
      document.getElementById('form-section-title-memo').innerText = isRecipe ? '💡 コツ・メモ' : '✏️ 感想・メモ';

      // Clear optional fields if switching to record
      if (!isRecipe) {
        document.getElementById('recipe-servings').value = '';
        document.getElementById('recipe-ingredients').value = '';
        stepsFormContainer.innerHTML = '';
        recipeStepsRaw.value = '';
      }
    }'''

new_form_ui = '''    function updateFormModeUI() {
      document.getElementById('form-group-servings').style.display = 'block';
      document.getElementById('form-card-ingredients').style.display = 'block';
      document.getElementById('form-card-steps').style.display = 'block';

      const isEdit = !!editingRecipeId;
      document.getElementById('btn-save-content').innerHTML = `<span>💾</span> レシピを${isEdit ? '更新' : '保存'}する`;
      document.getElementById('form-section-title-memo').innerText = '💡 コツ・メモ';
    }'''

if old_form_ui in text:
    text = text.replace(old_form_ui, new_form_ui)
    print("updateFormModeUI updated!")

# 5. resetForm JS
old_reset = '''      const isRecipe = currentAppMode === 'recipe';
      document.getElementById('form-header-title').innerText = isRecipe ? '📌 基本情報' : '🍽️ メモ情報';
      document.getElementById('nav-add-icon').innerText = '➕';
      document.getElementById('nav-add-text').innerText = isRecipe ? 'レシピ登録' : 'メモする';
      document.getElementById('btn-save-content').innerHTML = `<span>💾</span> ${isRecipe ? 'レシピ' : 'メモ'}を保存する`;'''

new_reset = '''      document.getElementById('form-header-title').innerText = '📌 基本情報';
      document.getElementById('nav-add-icon').innerText = '➕';
      document.getElementById('nav-add-text').innerText = 'レシピ登録';
      document.getElementById('btn-save-content').innerHTML = `<span>💾</span> レシピを保存する`;'''

if old_reset in text:
    text = text.replace(old_reset, new_reset)
    print("resetForm updated!")

# 6. Save Alerts in btn-save-recipe
text = text.replace("recordType: currentAppMode", "recordType: 'recipe'")
text = text.replace("alert(currentAppMode === 'recipe' ? \"レシピを更新しました！\" : \"メモを更新しました！\");", 'alert("レシピを更新しました！");')
text = text.replace("alert(currentAppMode === 'recipe' ? \"レシピを保存しました！\" : \"メモを保存しました！\");", 'alert("レシピを保存しました！");')
text = text.replace("const typeStr = currentAppMode === 'recipe' ? 'レシピ' : 'メモ';", "const typeStr = 'レシピ';")

# 7. renderRecipeList
old_scored = '''      const scoredRecipes = recipesCache.map(item => {
        // Mode filtering
        const isFoodRecord = item.recordType === 'food_record';
        if (currentAppMode === 'recipe' && isFoodRecord) return { item, score: 0 };
        if (currentAppMode === 'food_record' && !isFoodRecord) return { item, score: 0 };
        if (currentFilter && (!item.tags || !item.tags.includes(currentFilter))) return { item, score: 0 };'''

new_scored = '''      const scoredRecipes = recipesCache.map(item => {
        if (currentFilter && (!item.tags || !item.tags.includes(currentFilter))) return { item, score: 0 };'''

if old_scored in text:
    text = text.replace(old_scored, new_scored)
    print("renderRecipeList mode filtering removed!")

old_empty_msg = '''      if (filtered.length === 0) {
        const isRecipe = currentAppMode === 'recipe';
        const typeStr = isRecipe ? 'レシピ' : 'メモ';
        let msg = `該当する${typeStr}が見つかりません。`;

        if (activeCategory === 'fav') {
          msg = currentUser
            ? `お気に入りに登録された${typeStr}がありません。カードの ⭐ ボタンで追加できます。`
            : 'データ同期設定（⚙️）からGoogleログインするとお気に入り機能が利用できます。';
        }

        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">${isRecipe ? '🍳✨' : '🍽️✨'}</div>
            <p>${msg}</p>
          </div>`;
        return;
      }'''

new_empty_msg = '''      if (filtered.length === 0) {
        let msg = '該当するレシピが見つかりません。';

        if (activeCategory === 'fav') {
          msg = currentUser
            ? 'お気に入りに登録されたレシピがありません。カードの ⭐ ボタンで追加できます。'
            : 'データ同期設定（⚙️）からGoogleログインするとお気に入り機能が利用できます。';
        }

        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">🍳✨</div>
            <p>${msg}</p>
          </div>`;
        return;
      }'''

if old_empty_msg in text:
    text = text.replace(old_empty_msg, new_empty_msg)
    print("renderRecipeList empty msg updated!")

text = text.replace("const cookedBadgeHtml = (item.recordType === 'food_record') ? '' : `<span class=\"cooked-badge\">🍳 作った: ${item.cookedCount || 0}回</span>`;", "const cookedBadgeHtml = `<span class=\"cooked-badge\">🍳 作った: ${item.cookedCount || 0}回</span>`;")

# 8. openRecipeDetail Modal
old_detail_record = '''      // Handle Record Type Sections
      const isRecord = recipe.recordType === 'food_record';
      document.getElementById('section-ingredients').style.display = isRecord ? 'none' : 'block';
      document.getElementById('section-steps').style.display = isRecord ? 'none' : 'block';
      document.getElementById('detail-cooked-counter').style.display = isRecord ? 'none' : 'flex';
      document.getElementById('detail-section-title-memo').innerText = isRecord ? '✏️ 感想・メモ' : '💡 コツ・メモ';

      const btnDeleteRecipe = document.getElementById('btn-delete-recipe');
      btnDeleteRecipe.innerHTML = `<span>🗑️</span> ${isRecord ? 'メモ' : 'レシピ'}を削除`;'''

new_detail_record = '''      document.getElementById('section-ingredients').style.display = 'block';
      document.getElementById('section-steps').style.display = 'block';
      document.getElementById('detail-cooked-counter').style.display = 'flex';
      document.getElementById('detail-section-title-memo').innerText = '💡 コツ・メモ';

      const btnDeleteRecipe = document.getElementById('btn-delete-recipe');
      btnDeleteRecipe.innerHTML = `<span>🗑️</span> レシピを削除`;'''

if old_detail_record in text:
    text = text.replace(old_detail_record, new_detail_record)
    print("openRecipeDetail record handling simplified!")

text = text.replace("switchAppMode(currentDetailRecipe.recordType || 'recipe');", "switchAppMode('recipe');")

old_delete_btn = '''      const isRecord = currentDetailRecipe.recordType === 'food_record';
      const typeStr = isRecord ? 'メモ' : 'レシピ';

      if (!confirm(`本当にこの${typeStr}を削除しますか？\\n削除すると元に戻せません。`)) {
        return;
      }

      const btnDelete = document.getElementById('btn-delete-recipe');
      btnDelete.innerText = "削除中...";
      btnDelete.disabled = true;

      try {
        await deleteDoc(doc(db, "recipes", currentDetailRecipe.id));
        modalDetail.classList.remove('active');
        currentDetailRecipe = null;
        alert(`${typeStr}を削除しました。`);'''

new_delete_btn = '''      if (!confirm("本当にこのレシピを削除しますか？\\n削除すると元に戻せません。")) {
        return;
      }

      const btnDelete = document.getElementById('btn-delete-recipe');
      btnDelete.innerText = "削除中...";
      btnDelete.disabled = true;

      try {
        await deleteDoc(doc(db, "recipes", currentDetailRecipe.id));
        modalDetail.classList.remove('active');
        currentDetailRecipe = null;
        alert("レシピを削除しました。");'''

if old_delete_btn in text:
    text = text.replace(old_delete_btn, new_delete_end if 'new_delete_end' in locals() else new_delete_btn)
    print("Delete recipe button handler simplified!")

text = text.replace("if (r.recordType === 'food_record') return false;\n", "")
text = text.replace("if (currentAppMode === 'recipe' || currentAppMode === 'food_record') renderRecipeList();", "if (currentAppMode === 'recipe') renderRecipeList();")

with open('index.html', 'w') as f:
    f.write(text)

