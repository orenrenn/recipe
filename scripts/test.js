
    import { GoogleGenerativeAI } from "https://esm.sh/@google/generative-ai";
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
    import { 
      getAuth, 
      signInWithPopup, 
      GoogleAuthProvider, 
      onAuthStateChanged, 
      signOut 
    } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";
    import { 
      getFirestore, 
      collection, 
      addDoc, 
      getDocs, 
      deleteDoc, 
      doc, 
      setDoc,
      getDoc,
      updateDoc, 
      arrayUnion,
      arrayRemove,
      increment,
      orderBy, 
      query, 
      onSnapshot,
      serverTimestamp 
    } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-firestore.js";

    // --- State Variables ---
    let app = null;
    let db = null;
    let auth = null;
    let currentUser = null;
    let userFavorites = [];
    let recipesCache = [];
    let activeCategory = 'all';
    let searchQuery = '';
    let sortBy = 'newest';
    let selectedImagesBase64 = [];
    let currentDetailRecipe = null;
    let currentGalleryIndex = 0;
    let editingRecipeId = null;

    let currentAppMode = 'recipe';
    let refrigeratorIngredients = [];
    let geminiApiKey = localStorage.getItem('geminiApiKey') || '';

    const googleAuthProvider = new GoogleAuthProvider();

    // Date formatter helper
    function formatDateString(ts) {
      if (!ts) return '';
      const date = ts.toDate ? ts.toDate() : new Date(ts);
      if (isNaN(date.getTime())) return '';
      return `${date.getFullYear()}/${String(date.getMonth()+1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
    }

    // --- Mode Switcher Logic ---
    window.switchAppMode = function(mode) {
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
    };

    function updateFormModeUI() {
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
    }

    // --- Dynamic Smart Steps Builder Logic ---
    const stepsFormContainer = document.getElementById('steps-form-container');
    const btnAddStepItem = document.getElementById('btn-add-step-item');
    const recipeStepsRaw = document.getElementById('recipe-steps-raw');

    function addStepInputRow(title = '', text = '') {
      const rowIdx = stepsFormContainer.children.length + 1;
      const row = document.createElement('div');
      row.className = 'step-form-row';
      row.innerHTML = `
        <div class="step-form-header">
          <span class="step-form-num">ステップ ${rowIdx}</span>
          <button type="button" class="btn-remove-step" title="削除">✕</button>
        </div>
        <div>
          <input type="text" class="step-title-input" placeholder="見出し (例: 予熱とパン粉の準備)" value="${escapeHtml(title)}">
        </div>
        <div>
          <textarea class="step-text-input" rows="2" placeholder="詳細 (例: オーブンを200℃〜220℃に予熱しておきます...)">${escapeHtml(text)}</textarea>
        </div>
      `;

      row.querySelector('.btn-remove-step').addEventListener('click', () => {
        row.remove();
        updateStepRowNumbers();
      });

      stepsFormContainer.appendChild(row);
    }

    function updateStepRowNumbers() {
      const rows = stepsFormContainer.querySelectorAll('.step-form-row');
      rows.forEach((r, idx) => {
        r.querySelector('.step-form-num').innerText = `ステップ ${idx + 1}`;
      });
    }

    btnAddStepItem.addEventListener('click', () => {
      addStepInputRow();
    });

    // --- Smart Auto-Parsing for Copied Raw Text ---
    function parsePastedStepsText(rawText) {
      if (!rawText || !rawText.trim()) return [];

      const blocks = rawText
        .split(/\n\s*\n+/)
        .map(b => b.trim())
        .filter(b => b.length > 0);

      const parsed = [];
      blocks.forEach(block => {
        const lines = block.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        if (lines.length >= 2) {
          const cleanTitle = lines[0].replace(/^[\d\.\s【】■◆①-⑨・\-]+/, '').trim() || lines[0];
          const text = lines.slice(1).join('\n');
          parsed.push({ title: cleanTitle, text });
        } else if (lines.length === 1) {
          const line = lines[0];
          const match = line.match(/^(.+?)[：:](.+)$/);
          if (match) {
            parsed.push({ title: match[1].trim(), text: match[2].trim() });
          } else {
            parsed.push({ title: '', text: line });
          }
        }
      });
      return parsed;
    }

    recipeStepsRaw.addEventListener('input', (e) => {
      const rawText = e.target.value;
      const parsedSteps = parsePastedStepsText(rawText);

      stepsFormContainer.innerHTML = '';
      if (parsedSteps.length > 0) {
        parsedSteps.forEach(st => addStepInputRow(st.title, st.text));
      } else {
        addStepInputRow();
      }
    });

    // --- Cloud Firebase Personal Favorites Logic ---
    async function loadUserFavorites() {
      if (!currentUser || !db) {
        userFavorites = [];
        renderRecipeList();
        return;
      }
      try {
        const userDocRef = doc(db, "users", currentUser.uid);
        const snap = await getDoc(userDocRef);
        if (snap.exists()) {
          userFavorites = snap.data().favorites || [];
        } else {
          userFavorites = [];
          await setDoc(userDocRef, { favorites: [], updatedAt: serverTimestamp() });
        }
      } catch (e) {
        console.error("User favorites load error:", e);
        if (e.code === 'permission-denied') {
           console.warn("お気に入りの読み込みが権限エラーでブロックされました。Firebaseセキュリティルールを確認してください。");
        }
        userFavorites = [];
      }
      renderRecipeList();
    }

    function isFavorite(recipeId) {
      return userFavorites.includes(recipeId);
    }

    // --- Standardized Latency-Free Toggle Favorite with Pop Animation ---
    async function toggleFavorite(recipeId, starBtnElement = null) {
      if (!currentUser || !db) {
        openSettingsModal();
        return alert("お気に入り機能を利用するには、設定画面(⚙️)から「Googleでログインして同期」してください。");
      }

      const userDocRef = doc(db, "users", currentUser.uid);
      const isFav = userFavorites.includes(recipeId);

      // 1. In-memory state update
      if (isFav) {
        userFavorites = userFavorites.filter(id => id !== recipeId);
      } else {
        userFavorites.push(recipeId);
      }

      // 2. Standardized instant visual animation on target element
      if (starBtnElement) {
        const iconSpan = starBtnElement.querySelector('span') || starBtnElement;
        iconSpan.innerText = userFavorites.includes(recipeId) ? '⭐' : '☆';
        starBtnElement.classList.remove('star-animating');
        iconSpan.classList.remove('star-animating');
        void starBtnElement.offsetWidth; // trigger reflow
        starBtnElement.classList.add('star-animating');
        iconSpan.classList.add('star-animating');
      }

      // 3. Update list UI & Detail Modal UI instantly
      renderRecipeList();
      if (currentDetailRecipe && currentDetailRecipe.id === recipeId) {
        updateDetailFavStar();
      }

      // 4. Pure Firestore Update in Background
      try {
        if (isFav) {
          await updateDoc(userDocRef, { favorites: arrayRemove(recipeId) });
        } else {
          await updateDoc(userDocRef, { favorites: arrayUnion(recipeId) });
        }
      } catch (err) {
        try {
          await setDoc(userDocRef, { favorites: userFavorites, updatedAt: serverTimestamp() }, { merge: true });
        } catch (setErr) {
          console.error("Fatal Error saving favorite:", setErr);
          alert("クラウドへの保存に失敗しました。\nFirebaseの「Firestore Database」の「ルール (Rules)」タブにて、users コレクションへのアクセス権限（read, write）が許可されていない可能性があります。");
          // Revert visual state
          if (isFav) {
            userFavorites.push(recipeId);
          } else {
            userFavorites = userFavorites.filter(id => id !== recipeId);
          }
          if (starBtnElement) {
             const iconSpan = starBtnElement.querySelector('span') || starBtnElement;
             iconSpan.innerText = isFav ? '⭐' : '☆';
          }
        }
      }
    }

    // --- Logout / Disconnect ---
    async function logoutUser() {
      if (auth) {
        await signOut(auth);
        currentUser = null;
        updateSyncModalUI();
        loadUserFavorites();
      }
    }

    document.getElementById('btn-disconnect-sync').addEventListener('click', async () => {
      if (confirm("同期を解除してログアウトしますか？")) {
        await logoutUser();
        alert("同期を解除しました。");
      }
    });

    function updateSyncModalUI() {
      const syncBanner = document.getElementById('sync-status-banner');
      const btnSyncGoogle = document.getElementById('btn-sync-google');
      const jsonArea = document.getElementById('firebase-config-json');
      const jsonContainer = document.getElementById('firebase-config-container');
      const syncDescription = document.getElementById('sync-description');

      if (currentUser) {
        syncBanner.style.display = 'flex';
        btnSyncGoogle.style.display = 'none';
        if (jsonContainer) jsonContainer.style.display = 'none';
        if (syncDescription) syncDescription.style.display = 'none';
      } else {
        syncBanner.style.display = 'none';
        btnSyncGoogle.style.display = 'flex';
        if (jsonContainer) jsonContainer.style.display = 'block';
        if (syncDescription) syncDescription.style.display = 'block';
      }
    }

    // --- Page & Modal DOM Elements ---
    const pages = {
      list: document.getElementById('page-list'),
      add: document.getElementById('page-add'),
      fridge: document.getElementById('page-fridge')
    };
    const navButtons = {
      list: document.getElementById('nav-list'),
      add: document.getElementById('nav-add')
    };
    const modalSettings = document.getElementById('modal-settings');
    const modalDetail = document.getElementById('modal-recipe-detail');

    function openSettingsModal() {
      updateSyncModalUI();
      modalSettings.classList.add('active');
    }

    // --- Navigation Logic ---
    function switchPage(pageName) {
      Object.values(pages).forEach(p => p.classList.remove('active'));
      Object.values(navButtons).forEach(b => b.classList.remove('active'));
      
      pages[pageName].classList.add('active');
      if (navButtons[pageName]) navButtons[pageName].classList.add('active');
      
      if (pageName === 'add' && !editingRecipeId) {
        resetForm();
      }

      if (pageName === 'list' && app) fetchRecipes();
    }

    navButtons.list.addEventListener('click', () => {
      editingRecipeId = null;
      switchPage('list');
    });
    navButtons.add.addEventListener('click', () => {
      if (!editingRecipeId) resetForm();
      switchPage('add');
    });

    // --- Form Multiple Photo Picker UI Logic ---
    const fileInput = document.getElementById('recipe-images-input');
    const btnAddPhotos = document.getElementById('btn-add-photos');
    const photosPreviewGrid = document.getElementById('photos-preview-grid');

    btnAddPhotos.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;

      for (const file of files) {
        try {
          const b64 = await compressImage(file);
          selectedImagesBase64.push(b64);
        } catch (err) {
          alert(err.message);
        }
      }
      fileInput.value = '';
      renderFormPhotoPreviews();
    });

    function renderFormPhotoPreviews() {
      const existingThumbs = photosPreviewGrid.querySelectorAll('.photo-thumb-wrapper');
      existingThumbs.forEach(t => t.remove());

      selectedImagesBase64.forEach((b64, idx) => {
        const wrap = document.createElement('div');
        wrap.className = 'photo-thumb-wrapper';
        wrap.innerHTML = `
          <img src="${b64}" class="photo-thumb-img" alt="写真">
          <button class="btn-remove-thumb" title="削除">✕</button>
        `;
        wrap.querySelector('.btn-remove-thumb').addEventListener('click', (e) => {
          e.stopPropagation();
          selectedImagesBase64.splice(idx, 1);
          renderFormPhotoPreviews();
        });
        photosPreviewGrid.insertBefore(wrap, btnAddPhotos);
      });
    }

    // Reset Form UI
    function resetForm() {
      editingRecipeId = null;
      selectedImagesBase64 = [];
      document.getElementById('recipe-title').value = '';
      document.getElementById('recipe-category').value = '主菜';
      document.getElementById('recipe-servings').value = '';
      document.getElementById('recipe-ingredients').value = '';
      document.getElementById('recipe-memo').value = '';
      
      recipeStepsRaw.value = '';
      stepsFormContainer.innerHTML = '';
      addStepInputRow(); // start with 1 step
      
      renderFormPhotoPreviews();

      const isRecipe = currentAppMode === 'recipe';
      document.getElementById('form-header-title').innerText = isRecipe ? '📌 基本情報' : '🍽️ メモ情報';
      document.getElementById('nav-add-icon').innerText = '➕';
      document.getElementById('nav-add-text').innerText = isRecipe ? 'レシピ登録' : 'メモする';
      document.getElementById('btn-save-content').innerHTML = `<span>💾</span> ${isRecipe ? 'レシピ' : 'メモ'}を保存する`;
      
      updateFormModeUI();
    }

    // --- Settings Modal Logic ---
    document.getElementById('btn-open-settings').addEventListener('click', openSettingsModal);
    document.getElementById('btn-close-settings').addEventListener('click', () => {
      modalSettings.classList.remove('active');
    });

    // --- Detail Modal Close ---
    document.getElementById('btn-close-detail').addEventListener('click', () => {
      modalDetail.classList.remove('active');
      currentDetailRecipe = null;
    });

    // Close modal when clicking backdrop
    [modalSettings, modalDetail].forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('active');
          currentDetailRecipe = null;
        }
      });
    });

    // --- Image Compression Logic ---
    function compressImage(file, maxWidth = 900, maxHeight = 900, quality = 0.75) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (event) => {
          const img = new Image();
          img.src = event.target.result;
          img.onload = () => {
            let width = img.width;
            let height = img.height;

            if (width > maxWidth || height > maxHeight) {
              if (width > height) {
                height = Math.round(height * (maxWidth / width));
                width = maxWidth;
              } else {
                width = Math.round(width * (maxHeight / height));
                height = maxHeight;
              }
            }

            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            const base64 = canvas.toDataURL('image/jpeg', quality);
            if (base64.length * 0.75 > 900000) {
              reject(new Error("画像サイズが大きすぎます。別の画像を選ぶか、解像度を下げてください。"));
            } else {
              resolve(base64);
            }
          };
          img.onerror = () => reject(new Error("画像の読込に失敗しました。"));
        };
        reader.onerror = () => reject(new Error("ファイルの読込に失敗しました。"));
      });
    }

    // --- Firebase & Auth Initialization ---
    function initFirebase(configStr) {
      try {
        const config = JSON.parse(configStr);
        app = initializeApp(config);
        db = getFirestore(app);
        auth = getAuth(app);

        onAuthStateChanged(auth, async (user) => {
          currentUser = user;
          updateSyncModalUI();
          if (currentUser) {
            modalSettings.classList.remove('active');
            await loadUserFavorites();
          } else {
            loadUserFavorites();
          }
          setupFridgeListener();
        });

        return true;
      } catch (e) {
        console.warn("Silent Firebase init note:", e);
        return false;
      }
    }

    const savedConfig = localStorage.getItem('fbConfig');
    if (savedConfig) {
      document.getElementById('firebase-config-json').value = savedConfig;
      if (initFirebase(savedConfig)) fetchRecipes();
    } else {
      openSettingsModal();
    }

    // --- Silent Google Sync / Auth Handling ---
    document.getElementById('btn-sync-google').addEventListener('click', async () => {
      const configStr = document.getElementById('firebase-config-json').value.trim();
      if (!configStr) {
        return alert("Firebase設定(JSON)を貼り付けてください。");
      }

      if (initFirebase(configStr)) {
        localStorage.setItem('fbConfig', configStr);
        fetchRecipes();

        try {
          const result = await signInWithPopup(auth, googleAuthProvider);
          currentUser = result.user;
          updateSyncModalUI();
          await loadUserFavorites();
          modalSettings.classList.remove('active');
        } catch (e) {
          console.warn("Silent login popup note:", e);
          if (auth && auth.currentUser) {
            currentUser = auth.currentUser;
            updateSyncModalUI();
            await loadUserFavorites();
            modalSettings.classList.remove('active');
          }
        }
      }
    });

    // --- Save / Update Recipe ---
    document.getElementById('btn-save-recipe').addEventListener('click', async () => {
      if (!app) {
        openSettingsModal();
        return alert("先にデータ同期設定画面でFirebase情報を入力してください。");
      }

      const title = document.getElementById('recipe-title').value.trim();
      const category = document.getElementById('recipe-category').value;
      const servings = document.getElementById('recipe-servings').value;
      const rawIngredients = document.getElementById('recipe-ingredients').value;
      const memo = document.getElementById('recipe-memo').value.trim();
      const btnSave = document.getElementById('btn-save-recipe');

      if (!title) return alert("料理名は必須項目です！");

      const ingredients = rawIngredients
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

      // Collect structured steps (title + text)
      const stepRows = stepsFormContainer.querySelectorAll('.step-form-row');
      let steps = [];
      stepRows.forEach(row => {
        const stepTitle = row.querySelector('.step-title-input').value.trim();
        const stepText = row.querySelector('.step-text-input').value.trim();
        if (stepTitle || stepText) {
          steps.push({ title: stepTitle, text: stepText });
        }
      });

      if (steps.length === 0 && recipeStepsRaw.value.trim()) {
        steps = parsePastedStepsText(recipeStepsRaw.value);
      }

      const btnSaveContent = document.getElementById('btn-save-content');
      btnSaveContent.innerHTML = `<span>⏳</span> 保存中...`;
      btnSave.disabled = true;

      try {
        const recipeData = {
          title,
          category: category || "その他",
          servings: servings || "",
          ingredients,
          steps,
          memo,
          imageUrls: selectedImagesBase64,
          imageUrl: selectedImagesBase64[0] || "",
          cookedCount: editingRecipeId ? (recipesCache.find(r => r.id === editingRecipeId)?.cookedCount || 0) : 0,
          createdBy: currentUser ? currentUser.displayName || currentUser.email : "匿名",
          recordType: currentAppMode
        };

        if (editingRecipeId) {
          recipeData.updatedAt = serverTimestamp();
          await updateDoc(doc(db, "recipes", editingRecipeId), recipeData);
          alert(currentAppMode === 'recipe' ? "レシピを更新しました！" : "メモを更新しました！");
        } else {
          recipeData.createdAt = serverTimestamp();
          recipeData.updatedAt = serverTimestamp();
          await addDoc(collection(db, "recipes"), recipeData);
          alert(currentAppMode === 'recipe' ? "レシピを保存しました！" : "メモを保存しました！");
        }

        resetForm();
        switchPage('list');
      } catch (e) {
        console.error(e);
        alert("エラーが発生しました: " + e.message);
      } finally {
        const isEdit = !!editingRecipeId;
        const typeStr = currentAppMode === 'recipe' ? 'レシピ' : 'メモ';
        btnSaveContent.innerHTML = `<span>💾</span> ${typeStr}を${isEdit ? '更新' : '保存'}する`;
        btnSave.disabled = false;
      }
    });

    // --- Fetch Recipes & Render List ---
    async function fetchRecipes() {
      const container = document.getElementById('recipe-list-container');
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔄</div><p>レシピを読み込み中...</p></div>`;

      try {
        const q = query(collection(db, "recipes"), orderBy("createdAt", "desc"));
        const querySnapshot = await getDocs(q);

        recipesCache = [];
        querySnapshot.forEach((docSnap) => {
          recipesCache.push({
            id: docSnap.id,
            ...docSnap.data()
          });
        });

        updateFilterTagsUI();
        renderRecipeList();
      } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><p>データの取得に失敗しました。設定情報を確認してください。</p></div>`;
      }
    }

    // --- Fully Generic Japanese Text Normalization & Search Engine ---

    // =====================================================================
    // Advanced Japanese Search Engine
    // - NFKC normalization
    // - Hiragana ↔ Katakana bidirectional matching
    // - Kanji → reading expansion (comprehensive dictionary)
    // - Rendaku (連濁) normalization (dakuten/handakuten stripping)
    // - Okurigana-aware consecutive duplicate collapsing
    // =====================================================================

    const COMMON_SYNONYMS = {
      "生米": "米",
      "白米": "米",
      "ご飯": "米",
      "ごはん": "米",
      "ライス": "米",
      "精白米": "米",
      "無洗米": "米",
      "豚肉": "豚",
      "豚バラ": "豚",
      "豚ロース": "豚",
      "豚こま": "豚",
      "豚ひき肉": "豚",
      "牛肉": "牛",
      "牛バラ": "牛",
      "牛ロース": "牛",
      "牛こま": "牛",
      "牛ひき肉": "牛",
      "鶏肉": "鶏",
      "鶏もも": "鶏",
      "鶏むね": "鶏",
      "鶏ささみ": "鶏",
      "鶏ひき肉": "鶏",
      "合びき肉": "ミンチ",
      "合いびき肉": "ミンチ",
      "ひき肉": "ミンチ",
      "挽き肉": "ミンチ",
      "玉子": "卵",
      "たまご": "卵",
      "長ねぎ": "ねぎ",
      "白ねぎ": "ねぎ",
      "青ねぎ": "ねぎ",
      "ネギ": "ねぎ",
      "玉ねぎ": "たまねぎ",
      "タマネギ": "たまねぎ",
      "人参": "にんじん",
      "大根": "だいこん",
      "ニンニク": "にんにく",
      "オクラ": "おくら",
      "長芋": "ながいも",
      "コショウ": "こしょう",
      "胡椒": "こしょう",
      "ジャガイモ": "じゃがいも",
      "キャベツ": "きゃべつ",
      "トマト": "とまと",
      "ピーマン": "ぴーまん",
      "レモン": "れもん",
      "ナス": "なす",
      "出汁": "だし",
      "出し": "だし",
      "ダシ": "だし",
      "顆粒": "かりゅう",
      "大豆": "豆",
      "小豆": "豆",
      "グリンピース": "豆",
      "グリーンピース": "豆",
      "ひよこ豆": "豆",
      "えんどう豆": "豆"
    };

    function normalizeJapaneseText(str) {
      if (!str) return '';
      let s = String(str).normalize('NFKC').toLowerCase();
      // Remove spaces, slashes, brackets, separators, Japanese punctuation, wave dashes, etc.
      s = s.replace(/[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】〜~！？!\?\+\*＊&＆×ｘ;；]/g, '');
      
      for (const [key, val] of Object.entries(COMMON_SYNONYMS)) {
        if (s.includes(key)) {
          s = s.replace(new RegExp(key, 'g'), val);
        }
      }
      
      return s;
    }

    function toHiragana(str) {
      if (!str) return '';
      return String(str).replace(/[\u30a1-\u30f6\u30f4]/g, match => String.fromCharCode(match.charCodeAt(0) - 0x60));
    }

    function toKatakana(str) {
      if (!str) return '';
      return String(str).replace(/[\u3041-\u3096\u3094]/g, match => String.fromCharCode(match.charCodeAt(0) + 0x60));
    }

    // --- Shared ingredient matching utility ---
    // Single source of truth: checks if a recipe ingredient matches any fridge stock item.
    // Uses hiragana normalization + synonym replacement + bidirectional substring.
    // Also splits compound fridge names (e.g. "おくら&長芋") on separators.
    function isIngredientInStock(recipeIng, fridgeList, normFridgeListCache) {
      const normIng = toHiragana(normalizeJapaneseText(recipeIng));
      if (!normIng) return false;
      
      // Broaden match by removing common suffixes from recipe ingredient (e.g. "豆スープ" -> "豆")
      const broadenedIng = normIng.replace(/(すーぷ|のもと|の素|かん|缶|ぺーすと|ペースト)$/, '');
      
      const splitRe = /[&＆・、,\/\+×ｘ]/;
      
      for (let i = 0; i < fridgeList.length; i++) {
        const f = fridgeList[i];
        const normF = normFridgeListCache ? normFridgeListCache[i] : toHiragana(normalizeJapaneseText(f));
        
        // 1. Normalized hiragana substring match (bidirectional)
        if (normF.length > 0) {
          if (normIng.includes(normF) || normF.includes(normIng) || broadenedIng.includes(normF) || normF.includes(broadenedIng)) return true;
        }
        
        // 2. Raw text substring match (bidirectional)
        if (recipeIng.includes(f) || f.includes(recipeIng)) return true;
        
        // 3. Split compound fridge items on separators and check each part
        if (splitRe.test(f)) {
          const parts = f.split(splitRe).map(p => p.trim()).filter(p => p.length > 0);
          for (const part of parts) {
            const normPart = toHiragana(normalizeJapaneseText(part));
            if (normPart.length > 0 && (normIng.includes(normPart) || normPart.includes(normIng) || broadenedIng.includes(normPart) || normPart.includes(broadenedIng))) return true;
            if (recipeIng.includes(part) || part.includes(recipeIng)) return true;
          }
        }
      }
      return false;
    }

    // Ingredients that are trivially available (water etc.) - never shown as "missing"
    function isTriviallyAvailable(ing) {
      let cleanIng = String(ing).replace(/[(（].*?[)）]/g, '');
      cleanIng = normalizeJapaneseText(cleanIng);
      cleanIng = cleanIng.replace(/[0-9０-９]/g, '')
                         .replace(/(ml|cc|g|kg|l|かっぷ|おおさじ|こさじ|しょうしょう|てきりょう|ひとつまみ|はい|ふん|くらい|おこのみ|お好み|やく|カップ|大さじ|小さじ|少々|適量|杯|分|約)/g, '');
      cleanIng = toHiragana(cleanIng);
      
      const ALWAYS_AVAILABLE = ["水", "お湯", "熱湯", "氷", "氷水", "ぬるま湯", "冷水"];
      return ALWAYS_AVAILABLE.includes(cleanIng) || ALWAYS_AVAILABLE.includes(cleanIng.replace(/くらい$/, ''));
    }

    function isSeasoningIngredient(ing) {
      if (isTriviallyAvailable(ing)) return true;
      const seasoningKeywords = ["塩","砂糖","醤油","しょうゆ","酒","みりん","油","酢","こしょう","コショウ","胡椒","味噌","みそ","だしの素","だし","コンソメ","ケチャップ","マヨネーズ","ソース","バター","マーガリン","片栗粉","小麦粉","薄力粉","パン粉","めんつゆ","ポン酢","料理酒","オリーブオイル","ごま油","サラダ油","鶏がらスープ","中華スープ","ウスターソース","オイスターソース","ナンプラー","豆板醤","甜麺醤","カレー粉","カレールー","七味","一味","わさび","からし","マスタード","はちみつ","ハチミツ","蜂蜜","練乳","生クリーム","牛乳","チーズ","粉チーズ"];
      const normIng = toHiragana(normalizeJapaneseText(ing));
      return seasoningKeywords.some(kw => {
        const normKw = toHiragana(normalizeJapaneseText(kw));
        return normIng.includes(normKw) || normKw.includes(normIng);
      });
    }

    // Comprehensive Kanji → Hiragana reading dictionary
    // Covers food, cooking, measurements, descriptors, and common daily kanji
    // Multiple readings per kanji are listed for combinatorial expansion

    function computeSearchMatchScore(queryWord, targetText) {
      if (!queryWord || !targetText) return 0;

      const qNorm = normalizeJapaneseText(queryWord);
      const tNorm = normalizeJapaneseText(targetText);
      if (!qNorm || !tNorm) return 0;

      const allQueryWords = { ...(window.FOOD_VECTORS || {}), ...(window.QUERY_VECTORS || {}) };
      const qHira = toHiragana(qNorm);
      const isSemanticQuery = (qNorm in allQueryWords) || (qHira in allQueryWords);

      // Prevent garbage results for short, non-semantic queries (e.g. "あ", "する", "ウニ" when not in dict)
      const isAllHiragana = /^[\u3040-\u309F]+$/.test(qNorm);
      const isAllKatakana = /^[\u30A0-\u30FF]+$/.test(qNorm);
      if (!isSemanticQuery && (isAllHiragana || isAllKatakana) && qNorm.length <= 2) {
        // Only allow Layer 0 strict substring match, completely skip Layer 1 Hiragana fuzzy match
        // because 1-2 character Hiragana/Katakana (like うに) falsely match grammar particles (ように).
        if (tNorm.includes(qNorm)) {
          return 2.5; // Exact Katakana/Hiragana match (e.g. recipe actually contains "ウニ")
        }
        return 0;
      }

      let maxScore = 0;
      // If query is in Semantic Dict, we TRUST Semantic Search (Layer 2) to give the main score (up to 7.0).
      // Layer 0/1 only gives a tiny boost (0.5) for exact matches to help sorting, but not enough to pass the 1.8 threshold alone.
      // If query is NOT in Semantic Dict (e.g. "簡単", "レンジ", "フライパン"), Layer 0/1 gives a passing score (2.5).
      let baseSubstringScore = isSemanticQuery ? 0.5 : 2.5;

      // --- Layer 0: Direct normalized substring match ---
      if (tNorm.includes(qNorm)) {
        maxScore = baseSubstringScore;
      } else {
        // --- Layer 1: Hiragana-unified substring match ---
        // (Only safe for semantic queries OR queries > 2 chars, to avoid false positive particle matches)
        const tHira = toHiragana(tNorm);
        if (tHira.includes(qHira) && maxScore < baseSubstringScore - 0.1) {
          maxScore = baseSubstringScore - 0.1;
        }
      }

      // --- Layer 2: Offline Category Semantic Search ---
      if (window.FOOD_VECTORS) {
        let maxSemanticSim = 0;

          // Strict matching for query vs dictionary word with Subsumption
          const matchedWords = [];
          for (const qWord in allQueryWords) {
            const qWordHira = toHiragana(qWord);
            
            let idx = -1;
            let matchLen = 0;
            if (qNorm === qWord || qHira === qWordHira) {
              idx = 0; matchLen = qNorm.length;
            } else if (qWord.length >= 2 && qNorm.includes(qWord)) {
              idx = qNorm.indexOf(qWord); matchLen = qWord.length;
            } else if (qWord.length >= 2 && qHira.includes(qWordHira)) {
              idx = qHira.indexOf(qWordHira); matchLen = qWordHira.length;
            }

            if (idx !== -1) {
              matchedWords.push({ word: qWord, start: idx, end: idx + matchLen });
            }
          }

          // Filter out matches that are strictly contained within another match
          // (e.g. "にく" inside "にんにく")
          const queryWordsToUse = [];
          for (let i = 0; i < matchedWords.length; i++) {
            let isSubsumed = false;
            for (let j = 0; j < matchedWords.length; j++) {
              if (i === j) continue;
              if (matchedWords[i].start >= matchedWords[j].start && 
                  matchedWords[i].end <= matchedWords[j].end && 
                  (matchedWords[j].end - matchedWords[j].start) > (matchedWords[i].end - matchedWords[i].start)) {
                isSubsumed = true;
                break;
              }
            }
            if (!isSubsumed) {
              queryWordsToUse.push(matchedWords[i].word);
            }
          }

          // === Target Word Subsumption ===
          // Pre-compute all valid dictionary words present in the target text
          // to prevent generic substrings (e.g. "ねぎ") from being extracted out of
          // specific compounds (e.g. "玉ねぎ") if they overlap in the exact same position.
          const matchedTargetWords = [];
          for (const tWord in window.FOOD_VECTORS) {
            let searchIdx = 0;
            while (true) {
              searchIdx = tNorm.indexOf(tWord, searchIdx);
              if (searchIdx === -1) break;
              
              let isValid = true;
              const isKatakanaWord = /^[\u30A0-\u30FF]+$/.test(tWord);
              if (isKatakanaWord) {
                const prevChar = searchIdx > 0 ? tNorm[searchIdx - 1] : '';
                const nextChar = searchIdx + tWord.length < tNorm.length ? tNorm[searchIdx + tWord.length] : '';
                const isPrevKatakana = /[\u30A0-\u30FF]/.test(prevChar);
                const isNextKatakana = /[\u30A0-\u30FF]/.test(nextChar);
                
                if (isPrevKatakana || isNextKatakana) {
                  isValid = false;
                }
              }

              // Critical Heuristic: Prevent short Hiragana words (e.g. "うに", "いか", "す") 
              // from being falsely extracted out of grammar or other words (e.g. "ように", "すいか", "します").
              const isHiraganaWord = /^[\u3040-\u309F]+$/.test(tWord);
              if (isHiraganaWord && tWord.length <= 2) {
                const prevChar = searchIdx > 0 ? tNorm[searchIdx - 1] : '';
                const isPrevHiragana = /[\u3040-\u309F]/.test(prevChar);
                if (isPrevHiragana) {
                  isValid = false;
                }
              }
              
              if (isValid) {
                matchedTargetWords.push({ word: tWord, start: searchIdx, end: searchIdx + tWord.length });
              }
              searchIdx += 1;
            }
          }

          const validTargetWords = new Set();
          for (let i = 0; i < matchedTargetWords.length; i++) {
            let isSubsumed = false;
            for (let j = 0; j < matchedTargetWords.length; j++) {
              if (i === j) continue;
              const wi = matchedTargetWords[i];
              const wj = matchedTargetWords[j];
              if (wi.start >= wj.start && wi.end <= wj.end && (wj.end - wj.start) > (wi.end - wi.start)) {
                isSubsumed = true;
                break;
              }
            }
            if (!isSubsumed) {
              validTargetWords.add(matchedTargetWords[i].word);
            }
          }

          // Compute max semantic similarity between any qWord and valid tWord
          for (const qWord of queryWordsToUse) {
            const qVec = allQueryWords[qWord];
            for (const tWord of validTargetWords) {
              const tVec = window.FOOD_VECTORS[tWord];
              let dot = 0;
              for (let i = 0; i < qVec.length; i++) {
                dot += qVec[i] * tVec[i];
              }
              // Prevent Dimensional Explosion by capping the dot product at 1.0
              if (dot > 1.0) dot = 1.0;
              
              if (dot > maxSemanticSim) maxSemanticSim = dot;
            }
          }
        
        // Exact category match (dot == 1.0) gives semanticScore = 7.0
        if (maxSemanticSim >= 0.55) {
          const semanticScore = (maxSemanticSim - 0.5) * 14.0;
          maxScore = Math.max(maxScore, semanticScore);
        }
      }

      return maxScore >= 1.8 ? maxScore : 0;
    }

    function computeRecipeSemanticScore(recipe, queryStr) {
      // 1. Convert common punctuation separators to spaces to prevent words from merging (e.g. "豚肉、玉ねぎ" -> "豚肉 玉ねぎ")
      let normalizedQuery = queryStr.replace(/[\u3000・,\/、。｜\|]/g, ' ');
      const rawKeywords = normalizedQuery.trim().split(/\s+/).filter(k => k.length > 0);
      if (rawKeywords.length === 0) return 1.0;

      // 2. Filter out short, non-semantic hiragana noise particles (e.g. "と", "で", "の")
      // because they would return score 0 and fail the entire AND-search.
      const keywords = [];
      const allQueryWords = { ...(window.FOOD_VECTORS || {}), ...(window.QUERY_VECTORS || {}) };
      for (const kw of rawKeywords) {
        const qNorm = normalizeJapaneseText(kw);
        const qHira = toHiragana(qNorm);
        const isSemantic = (qNorm in allQueryWords) || (qHira in allQueryWords);
        const isAllHira = /^[\u3040-\u309F]+$/.test(qNorm);
        
        if (!isSemantic && isAllHira && qNorm.length <= 2) continue;
        keywords.push(kw);
      }
      
      // If all keywords were noise particles, fallback to the raw keywords to prevent empty array
      const finalKeywords = keywords.length > 0 ? keywords : rawKeywords;

      let totalScore = 0;

      for (const kw of finalKeywords) {
        let kwMaxScore = computeSearchMatchScore(kw, recipe.title) * 2.0;

        if (Array.isArray(recipe.ingredients)) {
          for (const ing of recipe.ingredients) {
            kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, ing) * 1.5);
          }
        }

        if (Array.isArray(recipe.steps)) {
          for (const st of recipe.steps) {
            const stText = typeof st === 'object' ? `${st.title || ''} ${st.text || st.desc || ''}` : String(st);
            kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, stText) * 0.6);
          }
        }

        if (recipe.memo) {
          kwMaxScore = Math.max(kwMaxScore, computeSearchMatchScore(kw, recipe.memo) * 0.8);
        }

        if (kwMaxScore <= 0) return 0;
        totalScore += kwMaxScore;
      }
      return totalScore;
    }

    // Filter & Render List with Multi-Criteria Sorting
    function renderRecipeList() {
      const container = document.getElementById('recipe-list-container');
      const filterTagSelect = document.getElementById('filter-tag-select');
      const currentFilter = filterTagSelect ? filterTagSelect.value : '';

      const scoredRecipes = recipesCache.map(item => {
        // Mode filtering
        const isFoodRecord = item.recordType === 'food_record';
        if (currentAppMode === 'recipe' && isFoodRecord) return { item, score: 0 };
        if (currentAppMode === 'food_record' && !isFoodRecord) return { item, score: 0 };
        if (currentFilter && (!item.tags || !item.tags.includes(currentFilter))) return { item, score: 0 };

        let categoryMatch = false;
        if (activeCategory === 'all') {
          categoryMatch = true;
        } else if (activeCategory === 'fav') {
          categoryMatch = isFavorite(item.id);
        } else {
          categoryMatch = ((item.category || 'その他') === activeCategory);
        }

        let score = categoryMatch ? computeRecipeSemanticScore(item, searchQuery) : 0;
        return { item, score };
      }).filter(res => res.score > 0);

      // Multi-criteria sorting algorithm
      scoredRecipes.sort((a, b) => {
        if (searchQuery.trim().length > 0) {
          if (b.score !== a.score) return b.score - a.score;
        }

        if (sortBy === 'newest') {
          const timeA = a.item.createdAt?.toMillis ? a.item.createdAt.toMillis() : (a.item.createdAt || 0);
          const timeB = b.item.createdAt?.toMillis ? b.item.createdAt.toMillis() : (b.item.createdAt || 0);
          return timeB - timeA;
        } else if (sortBy === 'oldest') {
          const timeA = a.item.createdAt?.toMillis ? a.item.createdAt.toMillis() : (a.item.createdAt || 0);
          const timeB = b.item.createdAt?.toMillis ? b.item.createdAt.toMillis() : (b.item.createdAt || 0);
          return timeA - timeB;
        } else if (sortBy === 'cooked') {
          return (b.item.cookedCount || 0) - (a.item.cookedCount || 0);
        } else if (sortBy === 'title') {
          return (a.item.title || '').localeCompare(b.item.title || '', 'ja');
        } else if (sortBy === 'fav') {
          const isFavA = isFavorite(a.item.id) ? 1 : 0;
          const isFavB = isFavorite(b.item.id) ? 1 : 0;
          return isFavB - isFavA;
        }
        return 0;
      });

      const filtered = scoredRecipes.map(res => res.item);

      document.getElementById('recipe-count').innerText = filtered.length;

      if (filtered.length === 0) {
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
      }

      const grid = document.createElement('div');
      grid.className = 'recipe-grid';

      filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.addEventListener('click', () => openRecipeDetail(item));

        const photos = getRecipePhotos(item);
        const coverPhoto = photos[0] || "";

        const imageHtml = coverPhoto
          ? `<img src="${coverPhoto}" alt="${item.title}" class="card-img">`
          : `<div class="card-placeholder">🍳</div>`;

        const categoryTag = item.category ? `<div class="card-category-tag">${item.category}</div>` : '';
        const servingsTag = item.servings ? `<span>👤 ${item.servings}</span>` : '';
        const cookedBadgeHtml = (item.recordType === 'food_record') ? '' : `<span class="cooked-badge">🍳 作った: ${item.cookedCount || 0}回</span>`;
        const photoCountBadge = photos.length > 1 ? `<div class="card-photo-count-tag">📷 ${photos.length}</div>` : '';

        const faved = isFavorite(item.id);
        const favBtnHtml = `<button class="card-fav-btn" title="お気に入り"><span>${faved ? '⭐' : '☆'}</span></button>`;

        let ingredientsPreview = '';
        if (Array.isArray(item.ingredients) && item.ingredients.length > 0) {
          ingredientsPreview = `🛒 ${item.ingredients.slice(0, 3).join('・')}${item.ingredients.length > 3 ? '...' : ''}`;
        } else if (item.memo) {
          ingredientsPreview = item.memo;
        }

        let badgesHtml = '';
        if (currentAppMode === 'recipe' && Array.isArray(item.ingredients) && refrigeratorIngredients.length > 0) {
          let missing = [];
          const normFCache = refrigeratorIngredients.map(f => toHiragana(normalizeJapaneseText(f)));
          
          item.ingredients.forEach(ing => {
            if (!isTriviallyAvailable(ing) && !isIngredientInStock(ing, refrigeratorIngredients, normFCache)) {
              missing.push(ing);
            }
          });
          
          if (missing.length > 0) {
            let missingStr = missing.slice(0, 3).join('・');
            if (missing.length > 3) missingStr += ` (他${missing.length - 3}件)`;
            badgesHtml = `<div style="background:#F59E0B; color:white; font-size:0.7rem; font-weight:bold; padding:2px 6px; border-radius:8px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); width: fit-content; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">💡不足: ${escapeHtml(missingStr)}</div>`;
          } else if (item.ingredients.length > 0) {
            badgesHtml = `<div style="background:var(--primary); color:white; font-size:0.7rem; font-weight:bold; padding:2px 6px; border-radius:8px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); width: fit-content; margin-bottom: 4px;">✅ 全て揃っています</div>`;
          }
        }

        const dateHtml = `<div style="font-size: 0.75rem; color: #999; margin-top: 6px; text-align: right;">${formatDateString(item.updatedAt || item.createdAt)}</div>`;

        card.innerHTML = `
          <div class="card-img-wrapper">
            ${imageHtml}
            ${categoryTag}
            ${favBtnHtml}
            ${photoCountBadge}
          </div>
          <div class="card-content">
            <h3 class="card-title">${escapeHtml(item.title)}</h3>
            <div class="card-meta">
              ${servingsTag}
              ${cookedBadgeHtml}
            </div>
            ${badgesHtml}
            ${ingredientsPreview ? `<div class="card-ingredients-preview">${escapeHtml(ingredientsPreview)}</div>` : ''}
            ${dateHtml}
          </div>
        `;

        // Bind pure Firestore instant favorite star click with uniform animation
        const favBtn = card.querySelector('.card-fav-btn');
        favBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          toggleFavorite(item.id, favBtn);
        });

        grid.appendChild(card);
      });

      container.innerHTML = '';
      container.appendChild(grid);
    }

    function updateFilterTagsUI() {
      const filterTagSelect = document.getElementById('filter-tag-select');
      const suggestTagSelect = document.getElementById('suggest-tag-select');
      const currentFilter = filterTagSelect ? filterTagSelect.value : '';
      const currentSuggestFilter = suggestTagSelect ? suggestTagSelect.value : '';

      if (filterTagSelect) {
        filterTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }
      if (suggestTagSelect) {
        suggestTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }

      const allTags = new Set();
      recipesCache.forEach(r => {
        if (r.tags && Array.isArray(r.tags)) {
          r.tags.forEach(t => allTags.add(t));
        }
      });
      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
        if (suggestTagSelect) suggestTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });
      if (filterTagSelect) filterTagSelect.value = currentFilter;
      if (suggestTagSelect) suggestTagSelect.value = currentSuggestFilter;
    }

    // Helper: Extract all photos for a recipe
    function getRecipePhotos(recipe) {
      if (Array.isArray(recipe.imageUrls) && recipe.imageUrls.length > 0) {
        return recipe.imageUrls;
      }
      if (recipe.imageUrl) {
        return [recipe.imageUrl];
      }
      return [];
    }

    // --- Open Detail Modal & Photo Gallery ---
    function openRecipeDetail(recipe) {
      currentDetailRecipe = recipe;
      currentGalleryIndex = 0;

      document.getElementById('detail-title').innerText = recipe.title || '無題';
      document.getElementById('detail-category-badge').innerText = recipe.category || 'その他';
      
      const count = recipe.cookedCount || 0;
      document.getElementById('detail-cooked-count').innerText = count;
      document.getElementById('btn-decrement-cooked').disabled = count <= 0;

      updateDetailFavStar();

      const servingsEl = document.getElementById('detail-servings');
      if (recipe.servings) {
        servingsEl.innerText = `👤 ${recipe.servings}`;
        servingsEl.style.display = 'inline';
      } else {
        servingsEl.style.display = 'none';
      }

      // Dates
      const dateInfoEl = document.getElementById('detail-date-info');
      const createdAtStr = formatDateString(recipe.createdAt);
      const updatedAtStr = formatDateString(recipe.updatedAt || recipe.createdAt);
      let dateHtml = `登録: ${createdAtStr}`;
      if (updatedAtStr && updatedAtStr !== createdAtStr) {
        dateHtml += ` (更新: ${updatedAtStr})`;
      }
      dateInfoEl.innerText = dateHtml;

      // Handle Record Type Sections
      const isRecord = recipe.recordType === 'food_record';
      document.getElementById('section-ingredients').style.display = isRecord ? 'none' : 'block';
      document.getElementById('section-steps').style.display = isRecord ? 'none' : 'block';
      document.getElementById('detail-cooked-counter').style.display = isRecord ? 'none' : 'flex';
      document.getElementById('detail-section-title-memo').innerText = isRecord ? '✏️ 感想・メモ' : '💡 コツ・メモ';
      
      const btnDeleteRecipe = document.getElementById('btn-delete-recipe');
      btnDeleteRecipe.innerHTML = `<span>🗑️</span> ${isRecord ? 'メモ' : 'レシピ'}を削除`;

      // Render Photo Gallery
      const photos = getRecipePhotos(recipe);
      const galleryContainer = document.getElementById('detail-gallery-container');
      const btnPrev = document.getElementById('gallery-btn-prev');
      const btnNext = document.getElementById('gallery-btn-next');
      const thumbsRow = document.getElementById('gallery-thumbs-row');

      if (photos.length > 0) {
        galleryContainer.style.display = 'block';
        updateGalleryPhoto(photos);

        if (photos.length > 1) {
          btnPrev.style.display = 'flex';
          btnNext.style.display = 'flex';
          thumbsRow.style.display = 'flex';
          thumbsRow.innerHTML = '';

          photos.forEach((p, idx) => {
            const thumb = document.createElement('img');
            thumb.className = `gallery-thumb-item ${idx === 0 ? 'active' : ''}`;
            thumb.src = p;
            thumb.addEventListener('click', () => {
              currentGalleryIndex = idx;
              updateGalleryPhoto(photos);
            });
            thumbsRow.appendChild(thumb);
          });
        } else {
          btnPrev.style.display = 'none';
          btnNext.style.display = 'none';
          thumbsRow.style.display = 'none';
        }
      } else {
        galleryContainer.style.display = 'none';
      }

      // Ingredients
      const secIngredients = document.getElementById('section-ingredients');
      const listIngredients = document.getElementById('detail-ingredients-list');
      listIngredients.innerHTML = '';

      if (Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0) {
        secIngredients.style.display = 'block';
        recipe.ingredients.forEach(ing => {
          let isMissing = false;
          
          // AI提案で明示的に不足とされているか、または手元のストックに含まれていないか判定
          if (recipe.missing_ingredients && Array.isArray(recipe.missing_ingredients) && recipe.missing_ingredients.length > 0) {
            isMissing = recipe.missing_ingredients.some(m => ing.includes(m) || m.includes(ing));
          } else if (refrigeratorIngredients && refrigeratorIngredients.length > 0) {
            isMissing = !isTriviallyAvailable(ing) && !isIngredientInStock(ing, refrigeratorIngredients);
          }

          const missingBadge = isMissing 
            ? `<span style="margin-left: 8px; font-size: 0.65rem; background: #F59E0B; color: white; padding: 2px 6px; border-radius: 8px; font-weight: bold; vertical-align: middle;">💡不足</span>` 
            : '';

          const label = document.createElement('label');
          label.className = 'ingredient-item';
          label.innerHTML = `<input type="checkbox"> <span>${escapeHtml(ing)}</span>${missingBadge}`;
          label.querySelector('input').addEventListener('change', (e) => {
            if (e.target.checked) label.classList.add('checked');
            else label.classList.remove('checked');
          });
          listIngredients.appendChild(label);
        });
      } else {
        secIngredients.style.display = 'none';
      }

      // Render Structured Steps (Title + Detail)
      const secSteps = document.getElementById('section-steps');
      const listSteps = document.getElementById('detail-steps-list');
      listSteps.innerHTML = '';

      if (Array.isArray(recipe.steps) && recipe.steps.length > 0) {
        secSteps.style.display = 'block';
        recipe.steps.forEach((step, idx) => {
          let stepTitle = '';
          let stepText = '';

          if (typeof step === 'object' && step !== null) {
            stepTitle = step.title || '';
            stepText = step.text || step.desc || '';
          } else if (typeof step === 'string') {
            const lines = step.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length >= 2) {
              stepTitle = lines[0];
              stepText = lines.slice(1).join('\n');
            } else {
              stepText = step;
            }
          }

          const item = document.createElement('div');
          item.className = 'step-item';
          item.innerHTML = `
            <div class="step-number">${idx + 1}</div>
            <div class="step-body">
              ${stepTitle ? `<div class="step-heading">${escapeHtml(stepTitle)}</div>` : ''}
              ${stepText ? `<div class="step-desc">${escapeHtml(stepText)}</div>` : ''}
            </div>
          `;
          listSteps.appendChild(item);
        });
      } else {
        secSteps.style.display = 'none';
      }

      // Memo
      const secMemo = document.getElementById('section-memo');
      const contentMemo = document.getElementById('detail-memo-content');
      if (recipe.memo) {
        secMemo.style.display = 'block';
        contentMemo.innerText = recipe.memo;
      } else {
        secMemo.style.display = 'none';
      }

      if (recipe.isAiGenerated) {
        document.getElementById('modal-footer-default').style.display = 'none';
        document.getElementById('modal-footer-ai').style.display = 'flex';
        document.getElementById('btn-toggle-fav-detail').style.display = 'none';
        document.getElementById('detail-cooked-counter').style.display = 'none';
      } else {
        document.getElementById('modal-footer-default').style.display = 'flex';
        document.getElementById('modal-footer-ai').style.display = 'none';
        document.getElementById('btn-toggle-fav-detail').style.display = 'block';
      }

      modalDetail.classList.add('active');
    }

    function updateDetailFavStar() {
      const starBtn = document.getElementById('btn-toggle-fav-detail');
      const starText = document.getElementById('detail-fav-star');
      if (currentDetailRecipe && isFavorite(currentDetailRecipe.id)) {
        starText.innerText = '⭐';
        starBtn.style.color = 'var(--star-color)';
      } else {
        starText.innerText = '☆';
        starBtn.style.color = 'var(--text-muted)';
      }
    }

    document.getElementById('btn-toggle-fav-detail').addEventListener('click', () => {
      if (currentDetailRecipe) {
        const starBtn = document.getElementById('btn-toggle-fav-detail');
        toggleFavorite(currentDetailRecipe.id, starBtn);
      }
    });

    // --- Increment Cooked Count Button Listener ---
    document.getElementById('btn-increment-cooked').addEventListener('click', async () => {
      if (!currentDetailRecipe || !db) return;

      currentDetailRecipe.cookedCount = (currentDetailRecipe.cookedCount || 0) + 1;
      document.getElementById('detail-cooked-count').innerText = currentDetailRecipe.cookedCount;
      document.getElementById('btn-decrement-cooked').disabled = currentDetailRecipe.cookedCount <= 0;

      const cacheItem = recipesCache.find(r => r.id === currentDetailRecipe.id);
      if (cacheItem) cacheItem.cookedCount = currentDetailRecipe.cookedCount;

      const btnInc = document.getElementById('btn-increment-cooked');
      btnInc.classList.remove('star-animating');
      void btnInc.offsetWidth;
      btnInc.classList.add('star-animating');

      renderRecipeList();

      try {
        await updateDoc(doc(db, "recipes", currentDetailRecipe.id), {
          cookedCount: increment(1)
        });
      } catch (e) {
        console.error("Cooked count increment failed:", e);
      }
    });

    // --- Decrement Cooked Count (Undo / -1) Button Listener ---
    document.getElementById('btn-decrement-cooked').addEventListener('click', async () => {
      if (!currentDetailRecipe || !db) return;
      if ((currentDetailRecipe.cookedCount || 0) <= 0) return;

      currentDetailRecipe.cookedCount -= 1;
      document.getElementById('detail-cooked-count').innerText = currentDetailRecipe.cookedCount;
      document.getElementById('btn-decrement-cooked').disabled = currentDetailRecipe.cookedCount <= 0;

      const cacheItem = recipesCache.find(r => r.id === currentDetailRecipe.id);
      if (cacheItem) cacheItem.cookedCount = currentDetailRecipe.cookedCount;

      renderRecipeList();

      try {
        await updateDoc(doc(db, "recipes", currentDetailRecipe.id), {
          cookedCount: increment(-1)
        });
      } catch (e) {
        console.error("Cooked count decrement failed:", e);
      }
    });

    function updateGalleryPhoto(photos) {
      const mainImg = document.getElementById('detail-main-img');
      const thumbsRow = document.getElementById('gallery-thumbs-row');
      
      mainImg.src = photos[currentGalleryIndex] || '';

      const thumbs = thumbsRow.querySelectorAll('.gallery-thumb-item');
      thumbs.forEach((i, iIdx) => {
        if (iIdx === currentGalleryIndex) i.classList.add('active');
        else i.classList.remove('active');
      });
    }

    document.getElementById('gallery-btn-prev').addEventListener('click', () => {
      if (!currentDetailRecipe) return;
      const photos = getRecipePhotos(currentDetailRecipe);
      if (photos.length <= 1) return;
      currentGalleryIndex = (currentGalleryIndex - 1 + photos.length) % photos.length;
      updateGalleryPhoto(photos);
    });

    document.getElementById('gallery-btn-next').addEventListener('click', () => {
      if (!currentDetailRecipe) return;
      const photos = getRecipePhotos(currentDetailRecipe);
      if (photos.length <= 1) return;
      currentGalleryIndex = (currentGalleryIndex + 1) % photos.length;
      updateGalleryPhoto(photos);
    });

    // --- Edit Recipe Click Handler ---
    document.getElementById('btn-edit-recipe').addEventListener('click', () => {
      if (!currentDetailRecipe) return;

      editingRecipeId = currentDetailRecipe.id;

      // Populate form basic info
      document.getElementById('recipe-title').value = currentDetailRecipe.title || '';
      document.getElementById('recipe-category').value = currentDetailRecipe.category || '主菜';
      document.getElementById('recipe-servings').value = currentDetailRecipe.servings || '';
      
      document.getElementById('recipe-ingredients').value = Array.isArray(currentDetailRecipe.ingredients)
        ? currentDetailRecipe.ingredients.join('\n')
        : '';
        
      // Populate structured steps & raw textarea
      stepsFormContainer.innerHTML = '';
      const rawLines = [];
      if (Array.isArray(currentDetailRecipe.steps) && currentDetailRecipe.steps.length > 0) {
        currentDetailRecipe.steps.forEach(st => {
          if (typeof st === 'object' && st !== null) {
            addStepInputRow(st.title || '', st.text || st.desc || '');
            if (st.title) rawLines.push(st.title);
            if (st.text || st.desc) rawLines.push(st.text || st.desc);
            rawLines.push('');
          } else if (typeof st === 'string') {
            const lines = st.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length >= 2) {
              addStepInputRow(lines[0], lines.slice(1).join('\n'));
            } else {
              addStepInputRow('', st);
            }
            rawLines.push(st);
            rawLines.push('');
          }
        });
      } else {
        addStepInputRow();
      }

      recipeStepsRaw.value = rawLines.join('\n').trim();

      document.getElementById('recipe-memo').value = currentDetailRecipe.memo || '';

      selectedImagesBase64 = getRecipePhotos(currentDetailRecipe).slice();
      renderFormPhotoPreviews();

      // Update Form Titles
      document.getElementById('form-header-title').innerText = '✏️ レシピを編集';
      document.getElementById('nav-add-icon').innerText = '✏️';
      document.getElementById('nav-add-text').innerText = 'レシピ編集';
      // update the mode internally
      switchAppMode(currentDetailRecipe.recordType || 'recipe');
      updateFormModeUI();
      
      // Close modal and switch tab
      modalDetail.classList.remove('active');
      switchPage('add');
    });

    // --- Delete Recipe ---
    document.getElementById('btn-delete-recipe').addEventListener('click', async () => {
      if (!currentDetailRecipe || !db) return;

      const isRecord = currentDetailRecipe.recordType === 'food_record';
      const typeStr = isRecord ? 'メモ' : 'レシピ';

      if (!confirm(`本当にこの${typeStr}を削除しますか？\n削除すると元に戻せません。`)) {
        return;
      }

      const btnDelete = document.getElementById('btn-delete-recipe');
      btnDelete.innerText = "削除中...";
      btnDelete.disabled = true;

      try {
        await deleteDoc(doc(db, "recipes", currentDetailRecipe.id));
        modalDetail.classList.remove('active');
        currentDetailRecipe = null;
        alert(`${typeStr}を削除しました。`);
        fetchRecipes();
      } catch (e) {
        console.error(e);
        alert("削除に失敗しました: " + e.message);
      } finally {
        btnDelete.innerHTML = `<span>🗑️</span> ${typeStr}を削除`;
        btnDelete.disabled = false;
      }
    });

    // --- Search & Filter Listeners ---
    document.getElementById('search-input').addEventListener('input', (e) => {
      searchQuery = e.target.value;
      renderRecipeList();
    });

    document.getElementById('category-pills').addEventListener('click', (e) => {
      if (e.target.classList.contains('pill')) {
        document.querySelectorAll('#category-pills .pill').forEach(p => p.classList.remove('active'));
        e.target.classList.add('active');
        activeCategory = e.target.dataset.cat;
        renderRecipeList();
      }
    });

    // Sort Listener
    document.getElementById('sort-select').addEventListener('change', (e) => {
      sortBy = e.target.value;
      renderRecipeList();
    });

    // Helper: HTML Escape
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }
    // =====================================================================
    // Refrigerator & AI Suggestion Logic
    // =====================================================================
    
    document.getElementById('gemini-api-key-input').value = geminiApiKey;
    document.getElementById('gemini-api-key-input').addEventListener('change', (e) => {
      geminiApiKey = e.target.value.trim();
      localStorage.setItem('geminiApiKey', geminiApiKey);
    });

    let unsubscribeFridge = null;
    let refrigeratorItems = [];

    function setupFridgeListener() {
      if (!db) return;
      if (unsubscribeFridge) unsubscribeFridge();
      
      const q = query(collection(db, "refrigerators"));
      unsubscribeFridge = onSnapshot(q, (snapshot) => {
        refrigeratorItems = [];
        
        snapshot.forEach((docSnap) => {
          const data = docSnap.data();
          if (data.name) {
            refrigeratorItems.push({ id: docSnap.id, ...data });
          }
        });
        
        refrigeratorItems.sort((a, b) => {
          const timeA = a.createdAt?.toMillis ? a.createdAt.toMillis() : (a.createdAt || 0);
          const timeB = b.createdAt?.toMillis ? b.createdAt.toMillis() : (b.createdAt || 0);
          return timeA - timeB;
        });
        
        refrigeratorIngredients = refrigeratorItems.map(item => item.name);
        
        if (currentAppMode === 'fridge') renderFridgeUI();
        // Re-render recipe list badges when fridge data changes
        if (currentAppMode === 'recipe' || currentAppMode === 'food_record') renderRecipeList();
      }, (error) => {
        console.error("Fridge listener error:", error);
      });
    }

    async function addFridgeItem(name, amount, expiry, storage, category) {
      if (!name || !db) return;
      const nameTrim = name.trim();
      if (!nameTrim) return;
      
      try {
        await addDoc(collection(db, "refrigerators"), {
          name: nameTrim,
          amount: amount.trim(),
          expiry: expiry,
          storage: storage,
          category: category || "",
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        });
      } catch (e) {
        console.error("Failed to add fridge item:", e);
        alert("追加に失敗しました: " + e.message);
      }
    }

    async function removeFridgeItem(id) {
      if (!db) return;
      try {
        await deleteDoc(doc(db, "refrigerators", id));
      } catch (e) {
        console.error("Failed to remove fridge item:", e);
        alert("削除に失敗しました: " + e.message);
      }
    }

    let editingFridgeItemId = null;

    async function updateFridgeItem(id, name, amount, expiry, storage, category) {
      if (!name || !db) return;
      const nameTrim = name.trim();
      if (!nameTrim) return;
      
      try {
        await updateDoc(doc(db, "refrigerators", id), {
          name: nameTrim,
          amount: amount.trim(),
          expiry: expiry,
          storage: storage,
          category: category || "",
          updatedAt: serverTimestamp()
        });
      } catch (e) {
        console.error("Failed to update fridge item:", e);
        alert("更新に失敗しました: " + e.message);
      }
    }

    document.getElementById('btn-add-fridge-item').addEventListener('click', () => {
      const inputName = document.getElementById('fridge-ingredient-input');
      const inputAmount = document.getElementById('fridge-amount-input');
      const inputExpiry = document.getElementById('fridge-expiry-input');
      const inputStorage = document.getElementById('fridge-storage-input');
      const inputCategory = document.getElementById('fridge-category-input');
      const btn = document.getElementById('btn-add-fridge-item');
      
      if (editingFridgeItemId) {
        updateFridgeItem(editingFridgeItemId, inputName.value, inputAmount.value, inputExpiry.value, inputStorage.value, inputCategory.value);
        editingFridgeItemId = null;
        btn.innerText = '追加';
        btn.style.background = 'var(--primary)';
      } else {
        addFridgeItem(inputName.value, inputAmount.value, inputExpiry.value, inputStorage.value, inputCategory.value);
      }
      
      inputName.value = '';
      inputAmount.value = '';
      inputExpiry.value = '';
      inputStorage.value = '';
      inputCategory.value = '';
    });
    document.getElementById('fridge-ingredient-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('btn-add-fridge-item').click();
      }
    });

    window.renderFridgeUI = function() {
      const container = document.getElementById('fridge-tags-container');
      container.innerHTML = '';
      if (refrigeratorItems.length === 0) {
        container.innerHTML = `<div style="font-size:0.9rem; color:#999; margin:10px 0;">食材が登録されていません</div>`;
        suggestLocalRecipes();
        return;
      }
      
      const groupMode = document.getElementById('fridge-group-select')?.value || 'category';
      const sortMode = document.getElementById('fridge-sort-select')?.value || 'newest';

      // 1. Sort
      let sortedItems = [...refrigeratorItems];
      if (sortMode === 'newest') {
        sortedItems.sort((a, b) => {
          const timeA = a.createdAt?.toMillis ? a.createdAt.toMillis() : (a.createdAt || 0);
          const timeB = b.createdAt?.toMillis ? b.createdAt.toMillis() : (b.createdAt || 0);
          return timeB - timeA;
        });
      } else if (sortMode === 'expiry') {
        sortedItems.sort((a, b) => {
          if (!a.expiry && !b.expiry) return 0;
          if (!a.expiry) return 1;
          if (!b.expiry) return -1;
          return a.expiry.localeCompare(b.expiry);
        });
      } else if (sortMode === 'name') {
        sortedItems.sort((a, b) => a.name.localeCompare(b.name));
      }

      // 2. Group
      const grouped = {};
      sortedItems.forEach(item => {
        const gKey = groupMode === 'category' 
          ? (item.category || 'その他') 
          : (item.storage || '指定なし');
        if (!grouped[gKey]) grouped[gKey] = [];
        grouped[gKey].push(item);
      });

      // 3. Order Groups
      let orderedKeys = Object.keys(grouped);
      if (groupMode === 'category') {
        const catOrder = ["野菜・きのこ", "肉類", "魚介類", "卵・乳製品", "穀物・麺類", "調味料", "加工品・その他", "その他"];
        orderedKeys.sort((a, b) => {
           let iA = catOrder.indexOf(a);
           let iB = catOrder.indexOf(b);
           if(iA === -1) iA = 999;
           if(iB === -1) iB = 999;
           return iA - iB;
        });
      } else {
        const storOrder = ["📦 常温", "❄️ 冷蔵", "🧊 冷凍", "指定なし"];
        orderedKeys.sort((a, b) => {
           let iA = storOrder.indexOf(a);
           let iB = storOrder.indexOf(b);
           if(iA === -1) iA = 999;
           if(iB === -1) iB = 999;
           return iA - iB;
        });
      }

      // 4. Render
      orderedKeys.forEach(key => {
        const items = grouped[key];
        const details = document.createElement('details');
        details.open = true;
        details.style.marginBottom = '12px';
        details.style.width = '100%';
        
        let displayTitle = key;
        if (groupMode === 'category') {
          const emojiMap = {
            "野菜・きのこ": "🥬 野菜・きのこ",
            "肉類": "🍖 肉類",
            "魚介類": "🐟 魚介類",
            "卵・乳製品": "🥚 卵・乳製品",
            "穀物・麺類": "🍚 穀物・麺類",
            "調味料": "🧂 調味料",
            "加工品・その他": "🥫 加工品・その他",
            "その他": "❓ その他"
          };
          displayTitle = emojiMap[key] || key;
        }

        const summary = document.createElement('summary');
        summary.style.fontWeight = 'bold';
        summary.style.color = 'var(--primary-dark)';
        summary.style.padding = '8px 12px';
        summary.style.backgroundColor = '#F8FAFC';
        summary.style.borderRadius = '8px';
        summary.style.cursor = 'pointer';
        summary.style.display = 'flex';
        summary.style.justifyContent = 'space-between';
        summary.innerHTML = `<span>${escapeHtml(displayTitle)} <span style="font-size:0.8rem; color:#888;">(${items.length})</span></span> <span style="color:#CBD5E1; font-size: 0.8rem;">▼</span>`;
        
        // Hide default arrow marker in webkit
        const style = document.createElement('style');
        style.innerHTML = `details > summary { list-style: none; } details > summary::-webkit-details-marker { display: none; }`;
        summary.appendChild(style);

        details.appendChild(summary);

        const listWrap = document.createElement('div');
        listWrap.style.display = 'flex';
        listWrap.style.flexWrap = 'wrap';
        listWrap.style.gap = '8px';
        listWrap.style.padding = '12px 4px';

        items.forEach(item => {
          const tag = document.createElement('div');
          tag.className = 'pill';
          tag.style.background = '#E0E7FF';
          tag.style.color = '#4338CA';
          tag.style.border = '1px solid #C7D2FE';
          tag.style.display = 'flex';
          tag.style.flexDirection = 'column';
          tag.style.alignItems = 'flex-start';
          tag.style.padding = '8px 12px';
          tag.style.position = 'relative';
          tag.style.minWidth = '120px';

          let detailsHtml = '';
          const extraTag = groupMode === 'category' ? item.storage : (item.category ? item.category : '');
          
          if (item.amount || item.expiry || extraTag) {
            detailsHtml = `<div style="font-size: 0.75rem; color: #6366F1; margin-top: 4px; font-weight: 500;">
              ${extraTag ? `<span>${escapeHtml(extraTag)}</span> &nbsp; ` : ''}
              ${item.amount ? `⚖️ ${escapeHtml(item.amount)}` : ''}
              ${item.amount && item.expiry ? ' &nbsp; ' : ''}
              ${item.expiry ? `📅 ${escapeHtml(item.expiry)}` : ''}
            </div>`;
          }

          tag.innerHTML = `
            <div style="font-weight: 600; font-size: 0.95rem; padding-right: 48px;">${escapeHtml(item.name)}</div>
            ${detailsHtml}
            <button class="btn-edit-ing" style="position: absolute; top: 6px; right: 30px; background:none;border:none;color:inherit;cursor:pointer;font-size:1.0rem;line-height:1; opacity: 0.6;">✏️</button>
            <button class="btn-remove-ing" style="position: absolute; top: 6px; right: 8px; background:none;border:none;color:inherit;cursor:pointer;font-size:1.2rem;line-height:1; opacity: 0.6;">&times;</button>
          `;
          
          tag.querySelector('.btn-edit-ing').addEventListener('click', () => {
            document.getElementById('fridge-ingredient-input').value = item.name || '';
            document.getElementById('fridge-amount-input').value = item.amount || '';
            document.getElementById('fridge-expiry-input').value = item.expiry || '';
            document.getElementById('fridge-storage-input').value = item.storage || '';
            document.getElementById('fridge-category-input').value = item.category || '';
            
            editingFridgeItemId = item.id;
            const btn = document.getElementById('btn-add-fridge-item');
            btn.innerText = '更新する';
            btn.style.background = '#10B981';
            
            document.getElementById('fridge-ingredient-input').focus();
            window.scrollTo({ top: document.getElementById('page-fridge').offsetTop, behavior: 'smooth' });
          });
          tag.querySelector('.btn-edit-ing').addEventListener('mouseenter', (e) => e.target.style.opacity = '1');
          tag.querySelector('.btn-edit-ing').addEventListener('mouseleave', (e) => e.target.style.opacity = '0.6');

          tag.querySelector('.btn-remove-ing').addEventListener('click', () => {
             if (confirm(`「${item.name}」を削除しますか？`)) {
               if (editingFridgeItemId === item.id) {
                 editingFridgeItemId = null;
                 const btn = document.getElementById('btn-add-fridge-item');
                 btn.innerText = '追加';
                 btn.style.background = 'var(--primary)';
               }
               removeFridgeItem(item.id);
             }
          });
          tag.querySelector('.btn-remove-ing').addEventListener('mouseenter', (e) => e.target.style.opacity = '1');
          tag.querySelector('.btn-remove-ing').addEventListener('mouseleave', (e) => e.target.style.opacity = '0.6');
          listWrap.appendChild(tag);
        });
        
        details.appendChild(listWrap);
        container.appendChild(details);
      });
      
      suggestLocalRecipes();
    };

    function createMiniRecipeCardDOM(item, badgesHtml = '', onClick) {
      const card = document.createElement('div');
      card.className = 'recipe-card';
      card.addEventListener('click', () => onClick(item));

      const photos = getRecipePhotos(item);
      const coverPhoto = photos[0] || "";
      const imageHtml = coverPhoto
        ? `<img src="${coverPhoto}" alt="${item.title}" class="card-img">`
        : `<div class="card-placeholder" style="font-size: 2.5rem;">${item.isAiGenerated ? '✨' : '🍳'}</div>`;

      const categoryTag = item.category ? `<div class="card-category-tag">${item.category}</div>` : '';

      let ingredientsPreview = '';
      if (Array.isArray(item.ingredients) && item.ingredients.length > 0) {
        ingredientsPreview = `🛒 ${item.ingredients.slice(0, 3).join('・')}${item.ingredients.length > 3 ? '...' : ''}`;
      }

      card.innerHTML = `
        <div class="card-img-wrapper">
          ${imageHtml}
          ${categoryTag}
          <div style="position:absolute; top:8px; left:8px; display:flex; flex-direction:column; gap:4px; z-index:10; max-width: 90%;">
            ${badgesHtml}
          </div>
        </div>
        <div class="card-content">
          <h3 class="card-title">${escapeHtml(item.title)}</h3>
          <div class="card-meta">
            ${ingredientsPreview}
          </div>
        </div>
      `;
      return card;
    }

    // === PAGE 3: Refrigerator / Suggest ===
    let currentSuggestPage = 1;
    const ITEMS_PER_SUGGEST_PAGE = 8;
    let currentScoredRecipes = [];
    let aiGeneratedTitles = [];


    function suggestLocalRecipes() {
      const grid = document.getElementById('suggest-local-grid');
      grid.innerHTML = '';
      if (refrigeratorIngredients.length === 0) {
        grid.innerHTML = '<p style="color:#999; font-size:0.9rem; text-align:center; width:100%; margin: 10px 0;">食材を追加すると、作れるレシピが表示されます。</p>';
        return;
      }

      const normFCache = refrigeratorIngredients.map(f => toHiragana(normalizeJapaneseText(f)));
      
      const suggestTagSelect = document.getElementById('suggest-tag-select');
      const selectedTag = suggestTagSelect ? suggestTagSelect.value : '';
      
      const scored = recipesCache.filter(r => {
        if (r.recordType === 'food_record') return false;
        if (selectedTag && (!r.tags || !r.tags.includes(selectedTag))) return false;
        return true;
      }).map(r => {
        let mainMatchCount = 0;
        let totalMainCount = 0;
        let missingAllList = [];
        let seasoningCount = 0;
        
        if (r.ingredients) {
          r.ingredients.forEach(ing => {
            if (isTriviallyAvailable(ing)) return; // skip water etc.
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
        // 提案条件: メイン食材の不足が1つ以下ならOK、またはマッチ数がメイン不足数以上
        return missingMainCount <= 0 || missingMainCount <= 1 || res.matchCount >= missingMainCount;
      });

      scored.sort((a, b) => {
        const aMissing = a.missing.length - a.seasoningCount;
        const bMissing = b.missing.length - b.seasoningCount;
        if (aMissing !== bMissing) return aMissing - bMissing; // 少ない順（全部足りているものが上に来る）
        if (b.matchCount !== a.matchCount) return b.matchCount - a.matchCount; // 次にマッチ数が多い順
        return a.missing.length - b.missing.length;
      });

      currentScoredRecipes = scored;
      renderSuggestPage(1);
    }

    function renderSuggestPage(page) {
      currentSuggestPage = page;
      const grid = document.getElementById('suggest-local-grid');
      grid.innerHTML = '';
      
      if (currentScoredRecipes.length === 0) {
        grid.innerHTML = '<p style="color:#999; font-size:0.9rem; text-align:center; width:100%; margin: 10px 0;">作れる登録済みレシピは見つかりませんでした。</p>';
        return;
      }
      
      const totalPages = Math.ceil(currentScoredRecipes.length / ITEMS_PER_SUGGEST_PAGE);
      const startIdx = (page - 1) * ITEMS_PER_SUGGEST_PAGE;
      const pageData = currentScoredRecipes.slice(startIdx, startIdx + ITEMS_PER_SUGGEST_PAGE);
      
      pageData.forEach(res => {
        let badges = `<div style="background:var(--primary); color:white; font-size:0.75rem; font-weight:bold; padding:4px 8px; border-radius:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); width: fit-content;">✅ 食材一致: ${res.matchCount}</div>`;
        if (res.missing.length > 0) {
          let missingStr = res.missing.slice(0, 3).join('・');
          if (res.missing.length > 3) missingStr += ` (他${res.missing.length - 3}件)`;
          badges += `<div style="background:#F59E0B; color:white; font-size:0.7rem; font-weight:bold; padding:4px 8px; border-radius:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); width: fit-content; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">💡不足: ${escapeHtml(missingStr)}</div>`;
        }
        const card = createMiniRecipeCardDOM(res.item, badges, (item) => openRecipeDetail(item));
        grid.appendChild(card);
      });
      
      if (totalPages > 1) {
        const paginationContainer = document.createElement('div');
        paginationContainer.style.width = '100%';
        paginationContainer.style.display = 'flex';
        paginationContainer.style.justifyContent = 'center';
        paginationContainer.style.gap = '8px';
        paginationContainer.style.marginTop = '16px';
        paginationContainer.style.gridColumn = '1 / -1';
        paginationContainer.style.flexWrap = 'wrap';
        
        for (let i = 1; i <= totalPages; i++) {
          const btn = document.createElement('button');
          btn.textContent = i;
          btn.className = 'btn';
          btn.style.padding = '4px 12px';
          btn.style.minWidth = 'auto';
          btn.style.marginBottom = '8px';
          if (i === page) {
            btn.style.background = 'var(--primary-dark)';
            btn.style.cursor = 'default';
          } else {
            btn.style.background = 'var(--bg-card)';
            btn.style.color = 'var(--text-main)';
            btn.style.border = '1px solid var(--border-color)';
            btn.onclick = () => renderSuggestPage(i);
          }
          paginationContainer.appendChild(btn);
        }
        grid.appendChild(paginationContainer);
      }
    }

    // --- AI Generation Logic ---
    document.getElementById('btn-generate-ai').addEventListener('click', () => doGenerateAI(false));
    document.getElementById('btn-generate-ai-another').addEventListener('click', () => doGenerateAI(true));

    async function doGenerateAI(isAnother = false) {
      if (!geminiApiKey) {
        alert('AIを利用するには、データ同期設定（⚙️）から Gemini API キー を設定してください。');
        openSettingsModal();
        return;
      }
      if (refrigeratorIngredients.length === 0) {
        alert('ストックに食材を追加してから提案を実行してください。');
        return;
      }
      
      if (!isAnother) aiGeneratedTitles = [];

      const genreEl = document.querySelector('input[name="aiGenre"]:checked');
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
      if (style !== '指定なし') conditions.push(`調理スタイル: ${style}`);

      const conditionStr = conditions.length > 0 ? conditions.join('、') : "おすすめ";
      const ingredients = refrigeratorIngredients.join('、');
      
      const excludeStr = aiGeneratedTitles.length > 0 ? `なお、以下の料理はすでに提案済みのため絶対に避けて、別の新しい料理を提案してください: ${aiGeneratedTitles.join('、')}\n` : '';

      document.getElementById('btn-generate-ai').disabled = true;
      document.getElementById('btn-generate-ai-another').disabled = true;
      document.getElementById('ai-loading-spinner').style.display = 'block';
      if (!isAnother) document.getElementById('suggest-ai-grid').innerHTML = '';
      document.getElementById('suggest-ai-controls').style.display = 'none';
      
      try {
        const genAI = new GoogleGenerativeAI(geminiApiKey);
        const prompt = `あなたはプロの料理研究家です。手元にある以下の食材（${ingredients}）をなるべく活用し、【${conditionStr}】という条件に沿った美味しい料理のレシピを${count}個の異なるバリエーションで提案してください。不足している一般的な調味料や多少の追加食材は使って構いません。
${excludeStr}出力は以下のJSON形式の配列のみを返してください。必ず有効なJSONにしてください。
[
  {
    "title": "料理名",
    "category": "主菜",
    "servings": 2,
    "ingredients": ["材料1", "材料2"], // ※使用するすべての材料・調味料（不足分も含む）を記載してください
    "missing_ingredients": ["買い足す必要がある材料1", "材料2"], // ※上記のうち、手元にない不足分の材料のみ記載してください
    "steps": ["手順1", "手順2"]
  }
]`;

        // ユーザーのAPIキーで利用可能なモデルを動的に取得
        let targetModels = ["gemini-1.5-flash"];
        try {
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${geminiApiKey}`);
          const data = await res.json();
          if (data.error) {
            throw new Error(`APIキーのエラー: ${data.error.message} (コード: ${data.error.code})`);
          }
          if (data.models && data.models.length > 0) {
            const validModels = data.models
              .filter(m => m.supportedGenerationMethods && m.supportedGenerationMethods.includes("generateContent"))
              .map(m => m.name.replace("models/", ""));
            const selectedModelPref = document.querySelector('input[name="aiModelSelect"]:checked')?.value || 'auto';
            
            validModels.sort((a, b) => {
              if (selectedModelPref === 'flash') {
                if (a.includes("flash") && !b.includes("flash")) return -1;
                if (!a.includes("flash") && b.includes("flash")) return 1;
              } else if (selectedModelPref === 'pro') {
                if (a.includes("pro") && !b.includes("pro")) return -1;
                if (!a.includes("pro") && b.includes("pro")) return 1;
              } else {
                // Auto: prioritize flash then pro
                if (a.includes("flash") && !b.includes("flash")) return -1;
                if (!a.includes("flash") && b.includes("flash")) return 1;
                if (a.includes("pro") && !b.includes("pro")) return -1;
                if (!a.includes("pro") && b.includes("pro")) return 1;
              }
              return 0;
            });
            if (validModels.length > 0) targetModels = validModels;
          }
        } catch (listErr) {
          if (listErr.message.startsWith("APIキーのエラー")) throw listErr;
          console.warn("モデル一覧の取得に失敗したためデフォルトモデルを使用します:", listErr);
        }

        let result = null;
        let lastError = null;
        let usedModel = "";
        const startTime = performance.now();

        for (const modelName of targetModels) {
          try {
            const model = genAI.getGenerativeModel({ model: modelName });
            result = await model.generateContent(prompt);
            if (result) {
              usedModel = modelName;
              break;
            }
          } catch (e) {
            console.warn(`モデル ${modelName} の呼び出しに失敗しました。次のモデルを試します...`, e);
            lastError = e;
          }
        }

        if (!result) throw lastError || new Error("利用可能なGeminiモデルが見つかりませんでした。");
        
        const endTime = performance.now();
        const durationSec = ((endTime - startTime) / 1000).toFixed(1);

        let text = result.response.text();
        text = text.replace(/```json/g, '').replace(/```/g, '').trim();
        const recipes = JSON.parse(text);

        const grid = document.getElementById('suggest-ai-grid');
        
        const infoDiv = document.createElement('div');
        infoDiv.style.cssText = "width: 100%; text-align: right; font-size: 0.8rem; color: #888; margin-bottom: 12px; margin-top: -8px;";
        infoDiv.textContent = `⚡ 使用モデル: ${usedModel} / 処理時間: ${durationSec}秒`;
        grid.appendChild(infoDiv);

        if (isAnother) {
          const divider = document.createElement('div');
          divider.style.gridColumn = '1 / -1';
          divider.style.borderTop = '2px dashed var(--border-color)';
          divider.style.margin = '16px 0';
          divider.style.paddingTop = '16px';
          divider.style.textAlign = 'center';
          divider.style.color = '#999';
          divider.style.fontSize = '0.85rem';
          divider.textContent = '🔻 別の新しく提案されたレシピ 🔻';
          grid.appendChild(divider);
        }

        recipes.forEach(r => {
          if (r.title) aiGeneratedTitles.push(r.title);
          r.isAiGenerated = true;
          let badges = `<div style="background:var(--primary); color:white; font-size:0.75rem; font-weight:bold; padding:4px 8px; border-radius:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); width: fit-content;">✨ AI提案</div>`;
          if (r.missing_ingredients && r.missing_ingredients.length > 0) {
            const missingStr = r.missing_ingredients.join('・');
            badges += `<div style="background:#F59E0B; color:white; font-size:0.7rem; font-weight:bold; padding:4px 8px; border-radius:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); width: fit-content; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">💡不足: ${escapeHtml(missingStr)}</div>`;
          }
          const card = createMiniRecipeCardDOM(r, badges, (item) => openRecipeDetail(item));
          grid.appendChild(card);
        });
        
        document.getElementById('suggest-ai-controls').style.display = 'block';
      } catch (err) {
        console.error(err);
        alert('AIレシピの生成に失敗しました: ' + err.message);
      } finally {
        document.getElementById('btn-generate-ai').disabled = false;
        document.getElementById('btn-generate-ai-another').disabled = false;
        document.getElementById('ai-loading-spinner').style.display = 'none';
      }
    }

    // --- AI Save Logic ---
    document.getElementById('btn-save-ai-recipe').addEventListener('click', async () => {
      if (!currentDetailRecipe || !db) return;
      document.getElementById('btn-save-ai-recipe').disabled = true;
      document.getElementById('btn-save-ai-recipe').innerHTML = '保存中...';
      
      try {
        const newRecipe = {
          title: currentDetailRecipe.title || '',
          category: currentDetailRecipe.category || 'その他',
          servings: currentDetailRecipe.servings || 2,
          ingredients: currentDetailRecipe.ingredients || [],
          steps: currentDetailRecipe.steps || [],
          memo: 'AIによって提案されたレシピです。',
          recordType: 'recipe',
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
          cookedCount: 0
        };
        await addDoc(collection(db, "recipes"), newRecipe);
        alert('マイレシピに保存しました！');
        modalDetail.classList.remove('active');
        fetchRecipes();
      } catch (err) {
        console.error(err);
        alert('保存に失敗しました: ' + err.message);
      } finally {
        document.getElementById('btn-save-ai-recipe').disabled = false;
        document.getElementById('btn-save-ai-recipe').innerHTML = '<span>💾</span> このレシピをマイレシピに登録する';
      }
    });

  