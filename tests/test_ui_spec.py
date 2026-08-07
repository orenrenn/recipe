"""
もぐレシピ UI仕様凍結テスト (E2E)

このテストスイートは、index.html の現在の仕様を完全に固定し、
修正のたびに実行して意図しない変更 (デグレ) を検出します。

注意:
  - テストはすべて「読み取り専用」です。データを作成・編集・削除しません。
  - .env にAPIキー等を記入しなくてもUI構造テストは実行可能です。
"""

import re
import pytest
from playwright.sync_api import expect


# =====================================================================
# 1. 初期レンダリングテスト
# =====================================================================
class TestInitialRendering:
    """ページ読み込み直後のUI構造が仕様通りであること"""

    def test_page_title(self, page):
        """ページタイトルが『もぐレシピ 🍳』であること"""
        expect(page).to_have_title("もぐレシピ 🍳")

    def test_header_logo_visible(self, page):
        """ヘッダーのアプリロゴが表示されること"""
        logo = page.locator(".app-logo")
        expect(logo).to_be_visible()

    def test_nav_tabs_exist(self, page):
        """ナビゲーションタブ（レシピ一覧・レシピ登録）が存在すること"""
        expect(page.locator("#nav-list")).to_be_visible()
        expect(page.locator("#nav-add")).to_be_visible()

    def test_recipe_list_tab_active_by_default(self, page):
        """初期状態でレシピ一覧タブがアクティブであること"""
        nav_list = page.locator("#nav-list")
        expect(nav_list).to_have_class(re.compile(r"active"))

    def test_recipe_add_tab_not_active_by_default(self, page):
        """初期状態でレシピ登録タブは非アクティブであること"""
        nav_add = page.locator("#nav-add")
        expect(nav_add).not_to_have_class(re.compile(r"active"))

    def test_page_list_visible(self, page):
        """レシピ一覧ページが表示されていること"""
        expect(page.locator("#page-list")).to_be_visible()

    def test_page_add_hidden(self, page):
        """レシピ登録ページが非表示であること"""
        expect(page.locator("#page-add")).to_be_hidden()

    def test_search_input_exists(self, page):
        """検索入力欄が存在すること"""
        expect(page.locator("#search-input")).to_be_visible()

    def test_category_select_exists(self, page):
        """カテゴリ選択プルダウンが存在すること"""
        select = page.locator("#category-select")
        expect(select).to_be_visible()

    def test_category_select_options(self, page):
        """カテゴリ選択プルダウンの選択肢が仕様通りであること"""
        options = page.locator("#category-select option")
        texts = options.all_text_contents()
        expected = [
            "すべてのカテゴリ", "😋 おいしかった",
            "🍱 主菜", "🥗 副菜", "🍲 汁物",
            "🍚 主食", "🍰 デザート", "📦 その他",
        ]
        assert texts == expected, f"カテゴリ選択肢が仕様と異なります: {texts}"

    def test_settings_button_exists(self, page):
        """設定ボタン (⚙️) が存在すること"""
        settings_btn = page.locator("#btn-open-settings")
        expect(settings_btn).to_be_visible()


# =====================================================================
# 2. 食材ストック (冷蔵庫) セクションテスト
# =====================================================================
class TestFridgeSection:
    """食材ストックUIの構造が仕様通りであること"""

    def test_fridge_section_header(self, page):
        """食材ストックのセクションヘッダーが表示されること"""
        header = page.locator("text=食材ストック")
        expect(header.first).to_be_visible()

    def test_add_ingredient_button(self, page):
        """「新しい食材を登録する」ボタンが存在すること"""
        btn = page.locator("text=新しい食材を登録する")
        expect(btn.first).to_be_visible()

    def test_fridge_accordion_closed_by_default(self, page):
        """食材一覧アコーディオンが初期状態で閉じていること"""
        accordion = page.locator("#fridge-master-accordion")
        # <details> が open 属性を持たない = 閉じている
        is_open = accordion.get_attribute("open")
        assert is_open is None, "食材一覧アコーディオンが初期状態で開いています"

    def test_fridge_accordion_summary_text(self, page):
        """食材一覧アコーディオンのサマリーテキストが正しいこと"""
        summary = page.locator("#fridge-master-accordion summary")
        expect(summary).to_contain_text("食材ストック一覧を開く/閉じる")

    def test_fridge_group_select_options(self, page):
        """グルーピング選択肢が「種類でまとめる」「場所でまとめる」であること"""
        options = page.locator("#fridge-group-select option")
        texts = options.all_text_contents()
        assert texts == ["種類でまとめる", "場所でまとめる"]

    def test_fridge_sort_default_name(self, page):
        """ソートの初期値が「名前順」であること"""
        select = page.locator("#fridge-sort-select")
        selected_value = select.input_value()
        assert selected_value == "name", f"ソート初期値が 'name' ではなく '{selected_value}'"

    def test_fridge_sort_select_options(self, page):
        """ソート選択肢が「名前順」「新しい順」「期限が近い順」であること"""
        options = page.locator("#fridge-sort-select option")
        texts = options.all_text_contents()
        assert texts == ["名前順", "新しい順", "期限が近い順"]

    def test_suggest_subtabs_exist(self, page):
        """サジェストサブタブ（マイレシピ提案 / AI提案）が存在すること"""
        expect(page.locator("#subtab-suggest-local")).to_be_visible()
        expect(page.locator("#subtab-suggest-ai")).to_be_visible()


# =====================================================================
# 3. 食材登録モーダルテスト
# =====================================================================
class TestFridgeItemModal:
    """食材登録モーダルのUI構造が仕様通りであること"""

    def _open_fridge_modal(self, page):
        page.evaluate("openFridgeItemModal()")
        page.wait_for_timeout(200)

    def test_fridge_modal_opens(self, page):
        """「新しい食材を登録する」ボタンをクリックでモーダルが開くこと"""
        self._open_fridge_modal(page)
        modal = page.locator("#modal-fridge-item")
        expect(modal).to_have_class(re.compile(r"active"))

    def test_fridge_modal_title(self, page):
        """モーダルタイトルが「🥦 食材の登録」であること"""
        self._open_fridge_modal(page)
        title = page.locator("#fridge-modal-title")
        expect(title).to_contain_text("食材の登録")

    def test_fridge_modal_input_fields(self, page):
        """食材名、保存場所、カテゴリの入力欄が存在すること"""
        self._open_fridge_modal(page)
        expect(page.locator("#fridge-ingredient-input")).to_be_visible()
        expect(page.locator("#fridge-storage-input")).to_be_visible()
        expect(page.locator("#fridge-category-input")).to_be_visible()

    def test_fridge_storage_options(self, page):
        """保存場所の選択肢が仕様通りであること"""
        self._open_fridge_modal(page)
        options = page.locator("#fridge-storage-input option")
        values = [o.get_attribute("value") for o in options.all()]
        assert values == ["❄️ 冷蔵", "🧊 冷凍", "📦 常温"]

    def test_fridge_category_options(self, page):
        """カテゴリの選択肢が仕様通りであること"""
        self._open_fridge_modal(page)
        options = page.locator("#fridge-category-input option")
        values = [o.get_attribute("value") for o in options.all()]
        expected = [
            "野菜・きのこ", "肉類", "魚介類", "卵・乳製品",
            "豆腐・豆類", "米・麺・粉", "調味料・油",
            "缶詰・乾物", "その他",
        ]
        assert values == expected, f"カテゴリ選択肢が仕様と異なります: {values}"


# =====================================================================
# 4. AI詳細条件モーダルテスト (こだわり条件)
# =====================================================================
class TestAiFilterModal:
    """AI詳細条件モーダルのUI構造が仕様通りであること"""

    def _open_modal(self, page):
        """AI詳細条件モーダルを開くヘルパー"""
        page.evaluate("openAiFilterModal()")
        page.wait_for_timeout(300)

    def test_modal_opens(self, page):
        """モーダルが正常に開くこと"""
        self._open_modal(page)
        modal = page.locator("#modal-ai-filter")
        expect(modal).to_have_class(re.compile(r"active"))

    def test_modal_title(self, page):
        """モーダルタイトルが正しいこと"""
        self._open_modal(page)
        expect(page.locator("#modal-ai-filter")).to_contain_text("こだわり条件の徹底絞り込み")

    def test_8_category_tabs_exist(self, page):
        """8つのカテゴリタブが存在すること"""
        self._open_modal(page)
        tab_ids = [
            "ai-tab-btn-role", "ai-tab-btn-genre", "ai-tab-btn-taste",
            "ai-tab-btn-purpose", "ai-tab-btn-style", "ai-tab-btn-time",
            "ai-tab-btn-nutrition", "ai-tab-btn-strictness",
        ]
        for tab_id in tab_ids:
            expect(page.locator(f"#{tab_id}")).to_be_visible()

    def test_role_tab_active_by_default(self, page):
        """初期状態で「役割」タブがアクティブであること"""
        self._open_modal(page)
        expect(page.locator("#ai-tab-btn-role")).to_have_class(re.compile(r"active"))

    def test_role_panel_visible_by_default(self, page):
        """初期状態で役割パネルが表示されていること"""
        self._open_modal(page)
        panel = page.locator("#ai-cat-panel-role")
        expect(panel).to_be_visible()

    def test_role_options(self, page):
        """役割タブの選択肢が仕様通りであること (ラジオボタン)"""
        self._open_modal(page)
        radios = page.locator("#ai-cat-panel-role input[type='radio']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = [
            "おまかせ",
            "メインおかず (主菜)",
            "サブおかず・副菜・小鉢",
            "主食 (ご飯もの・丼・チャーハン)",
            "主食 (麺・パスタ・うどん・そば)",
            "主食 (パン・サンドイッチ・トースト)",
            "スープ・汁物・鍋",
            "サラダ・前菜",
            "スイーツ・デザート・おやつ",
            "ドリンク・スムージー",
        ]
        assert values == expected, f"役割の選択肢が仕様と異なります: {values}"

    def test_role_default_selection(self, page):
        """役割タブのデフォルト選択が「おまかせ」であること"""
        self._open_modal(page)
        checked = page.locator("#ai-cat-panel-role input[type='radio']:checked")
        assert checked.get_attribute("value") == "おまかせ"

    def test_genre_options(self, page):
        """ジャンルタブの選択肢が仕様通りであること"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-genre").click()
        page.wait_for_timeout(100)
        radios = page.locator("#ai-cat-panel-genre input[type='radio']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = [
            "おまかせ",
            "和食・家庭料理",
            "洋食 (ハンバーグ・グラタン等)",
            "イタリアン・パスタ",
            "フレンチ・ビストロ風",
            "中華料理",
            "韓国料理",
            "タイ・ベトナム・東南アジア料理",
            "インド・スパイス料理・カレー",
            "メキシカン・アメリカン",
            "カフェ風・おしゃれワンプレート",
            "無国籍・創作・フュージョン料理",
        ]
        assert values == expected, f"ジャンルの選択肢が仕様と異なります: {values}"

    def test_taste_options(self, page):
        """味付けタブの選択肢が仕様通りであること (チェックボックス)"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-taste").click()
        page.wait_for_timeout(100)
        checks = page.locator("#ai-cat-panel-taste input[type='checkbox']")
        count = checks.count()
        assert count == 12, f"味付けの選択肢数が12個ではなく{count}個です"

    def test_purpose_options(self, page):
        """目的タブの選択肢が仕様通りであること (チェックボックス)"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-purpose").click()
        page.wait_for_timeout(100)
        checks = page.locator("#ai-cat-panel-purpose input[type='checkbox']")
        values = [c.get_attribute("value") for c in checks.all()]
        expected = [
            "おつまみ・お酒のお供",
            "弁当・作り置き (冷めても美味しい)",
            "朝ごはん・ブランチ",
            "時短・爆速 (10〜15分以内で完成)",
            "がっつり・スタミナ・ボリューム満点",
            "ヘルシー・ダイエット向け",
            "野菜たっぷり・野菜メイン",
            "子供が喜ぶ・マイルドで食べやすい",
            "節約・コスパ重視 (少ない食材で美味しく)",
            "おもてなし・ホームパーティ向け・見栄えよく",
            "夜食・胃に優しい (消化重視)",
            "疲労回復・体が温まる",
            "冷たい料理・暑い日にぴったり",
        ]
        assert values == expected, f"目的の選択肢が仕様と異なります: {values}"

    def test_style_options_count(self, page):
        """調理法タブの選択肢が12個あること"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-style").click()
        page.wait_for_timeout(100)
        checks = page.locator("#ai-cat-panel-style input[type='checkbox']")
        count = checks.count()
        assert count == 12, f"調理法の選択肢数が12個ではなく{count}個です"

    def test_time_options(self, page):
        """時間タブの選択肢が仕様通りであること (ラジオ)"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-time").click()
        page.wait_for_timeout(100)
        radios = page.locator("#ai-cat-panel-time input[type='radio']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = [
            "指定なし",
            "5分以内の超爆速スピード調理",
            "10〜15分程度の時短お手軽調理",
            "20〜30分程度の標準調理",
            "40分以上のじっくり本格調理",
            "煮込み・オーブンなど放置時間は含めない",
            "料理初心者向け・失敗なしのカンタンレシピ",
            "本格プロ・シェフ級の本格派レシピ",
        ]
        assert values == expected, f"時間の選択肢が仕様と異なります: {values}"

    def test_nutrition_options_count(self, page):
        """栄養タブの選択肢が10個あること"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-nutrition").click()
        page.wait_for_timeout(100)
        checks = page.locator("#ai-cat-panel-nutrition input[type='checkbox']")
        count = checks.count()
        assert count == 10, f"栄養の選択肢数が10個ではなく{count}個です"

    def test_strictness_options(self, page):
        """食材タブの選択肢が仕様通りであること (ラジオ)"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-strictness").click()
        page.wait_for_timeout(100)
        radios = page.locator("#ai-cat-panel-strictness input[type='radio']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = [
            "手元にある食材のみ (買い足しゼロ)",
            "定番調味料・野菜の買い足しOK",
            "今から買い物に行く (買い足し自由)",
        ]
        assert values == expected, f"食材の選択肢が仕様と異なります: {values}"

    def test_strictness_default_selection(self, page):
        """食材タブのデフォルトが「買い足しゼロ」であること"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-strictness").click()
        page.wait_for_timeout(100)
        checked = page.locator("#ai-cat-panel-strictness input[type='radio']:checked")
        assert checked.get_attribute("value") == "手元にある食材のみ (買い足しゼロ)"

    def test_modal_close_button(self, page):
        """モーダルの✕ボタンで閉じられること"""
        self._open_modal(page)
        page.evaluate("closeAiFilterModal()")
        page.wait_for_timeout(300)
        modal = page.locator("#modal-ai-filter")
        expect(modal).not_to_have_class(re.compile(r"active"))

    def test_modal_footer_buttons(self, page):
        """モーダルフッターに「この条件で決定する」と「リセット」ボタンがあること"""
        self._open_modal(page)
        expect(page.locator("#modal-ai-filter").locator("text=この条件で決定する")).to_be_visible()
        expect(page.locator("#modal-ai-filter").locator("text=リセット")).to_be_visible()

    def test_tab_switching_hides_other_panels(self, page):
        """タブを切り替えると他のパネルが非表示になること"""
        self._open_modal(page)
        page.locator("#ai-tab-btn-genre").click()
        page.wait_for_timeout(100)
        expect(page.locator("#ai-cat-panel-genre")).to_be_visible()
        expect(page.locator("#ai-cat-panel-role")).to_be_hidden()


# =====================================================================
# 5. レシピ登録フォームテスト
# =====================================================================
class TestRecipeAddForm:
    """レシピ登録フォームの構造が仕様通りであること"""

    def _switch_to_add_tab(self, page):
        page.evaluate("switchPage('add')")
        page.wait_for_timeout(200)

    def test_form_visible_after_tab_click(self, page):
        """レシピ登録タブを押すとフォームが表示されること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#page-add")).to_be_visible()

    def test_form_has_title_input(self, page):
        """料理名の入力欄が存在すること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#recipe-title")).to_be_visible()

    def test_form_category_options(self, page):
        """カテゴリ選択肢が仕様通りであること"""
        self._switch_to_add_tab(page)
        options = page.locator("#recipe-category option")
        texts = options.all_text_contents()
        expected = ["主菜", "副菜", "汁物", "主食", "デザート", "その他"]
        assert texts == expected, f"登録フォームのカテゴリが仕様と異なります: {texts}"

    def test_form_servings_options(self, page):
        """人数選択肢が仕様通りであること"""
        self._switch_to_add_tab(page)
        options = page.locator("#recipe-servings option")
        texts = options.all_text_contents()
        expected = ["指定なし", "1人分", "2人分", "3人分", "4人分", "5人分以上", "作りやすい分量"]
        assert texts == expected, f"人数選択肢が仕様と異なります: {texts}"

    def test_form_has_ingredients_textarea(self, page):
        """材料テキストエリアが存在すること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#recipe-ingredients")).to_be_visible()

    def test_form_has_steps_textarea(self, page):
        """作り方テキストエリアが存在すること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#recipe-steps-raw")).to_be_visible()

    def test_form_has_memo_textarea(self, page):
        """メモテキストエリアが存在すること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#recipe-memo")).to_be_visible()

    def test_form_has_save_button(self, page):
        """保存ボタンが存在すること"""
        self._switch_to_add_tab(page)
        expect(page.locator("#btn-save-recipe")).to_be_visible()


# =====================================================================
# 6. 設定モーダルテスト
# =====================================================================
class TestSettingsModal:
    """設定モーダルのUI構造が仕様通りであること"""

    def _open_settings(self, page):
        page.evaluate("openSettingsModal()")
        page.wait_for_timeout(200)

    def test_settings_modal_opens(self, page):
        """設定ボタンでモーダルが開くこと"""
        self._open_settings(page)
        modal = page.locator("#modal-settings")
        expect(modal).to_have_class(re.compile(r"active"))

    def test_settings_has_title(self, page):
        """設定モーダルに「データ同期設定」タイトルがあること"""
        self._open_settings(page)
        expect(page.locator("#modal-settings")).to_contain_text("データ同期設定")

    def test_settings_has_firebase_textarea(self, page):
        """Firebase設定用のテキストエリアが存在すること"""
        self._open_settings(page)
        expect(page.locator("#firebase-config-json")).to_be_visible()

    def test_settings_has_gemini_key_input(self, page):
        """Gemini APIキー入力欄が存在すること"""
        self._open_settings(page)
        expect(page.locator("#gemini-api-key-input")).to_be_visible()

    def test_settings_has_login_button(self, page):
        """Googleログインボタンが存在すること"""
        self._open_settings(page)
        expect(page.locator("#btn-sync-google")).to_be_visible()

    def test_settings_close_button(self, page):
        """設定モーダルの✕ボタンが存在すること"""
        self._open_settings(page)
        expect(page.locator("#btn-close-settings")).to_be_visible()


# =====================================================================
# 7. AI提案セクションテスト
# =====================================================================
class TestAiSuggestSection:
    """AI提案セクションの構造が仕様通りであること"""

    def _switch_to_ai_tab(self, page):
        page.evaluate("switchSuggestSubTab('ai')")
        page.wait_for_timeout(200)

    def test_ai_subtab_switch(self, page):
        """AI提案タブに切り替えるとサブパネルが表示されること"""
        self._switch_to_ai_tab(page)
        expect(page.locator("#subpanel-suggest-ai")).to_be_visible()

    def test_ai_required_ingredients_input(self, page):
        """「使いたい食材・キーワード」入力欄が存在すること"""
        self._switch_to_ai_tab(page)
        expect(page.locator("#ai-required-ingredients")).to_be_visible()

    def test_ai_filter_button_exists(self, page):
        """「詳細条件を絞り込む」ボタンが存在すること"""
        self._switch_to_ai_tab(page)
        expect(page.locator("#btn-open-ai-filter-modal")).to_be_visible()

    def test_ai_servings_radios(self, page):
        """人数ラジオボタンが仕様通りであること"""
        self._switch_to_ai_tab(page)
        radios = page.locator("input[name='aiServings']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = ["1人分", "2人分", "3〜4人分", "5人分以上 (作り置き・パーティ)"]
        assert values == expected, f"AI人数の選択肢が仕様と異なります: {values}"

    def test_ai_servings_default_2(self, page):
        """AI人数のデフォルトが2人分であること"""
        self._switch_to_ai_tab(page)
        checked = page.locator("input[name='aiServings']:checked")
        assert checked.get_attribute("value") == "2人分"

    def test_ai_count_radios(self, page):
        """提案数ラジオボタンが仕様通りであること"""
        self._switch_to_ai_tab(page)
        radios = page.locator("input[name='aiCount']")
        values = [r.get_attribute("value") for r in radios.all()]
        expected = ["3", "5", "10"]
        assert values == expected, f"提案数の選択肢が仕様と異なります: {values}"

    def test_ai_count_default_5(self, page):
        """提案数のデフォルトが5個であること"""
        self._switch_to_ai_tab(page)
        checked = page.locator("input[name='aiCount']:checked")
        assert checked.get_attribute("value") == "5"

    def test_generate_button_exists(self, page):
        """「レシピを提案する」ボタンが存在すること"""
        self._switch_to_ai_tab(page)
        expect(page.locator("#btn-generate-ai")).to_be_visible()


# =====================================================================
# 8. CSSカスタムプロパティ (デザイントークン) テスト
# =====================================================================
class TestDesignTokens:
    """CSSカスタムプロパティ（デザイントークン）が仕様通りであること"""

    def test_primary_color(self, page):
        """--primary が #FF6B52 であること"""
        val = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--primary').trim()")
        assert val == "#FF6B52", f"--primary が '{val}' です"

    def test_bg_color(self, page):
        """--bg が #FFFDF9 であること"""
        val = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()")
        assert val == "#FFFDF9", f"--bg が '{val}' です"

    def test_text_color(self, page):
        """--text が #2D2725 であること"""
        val = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--text').trim()")
        assert val == "#2D2725", f"--text が '{val}' です"


# =====================================================================
# 9. モーダル排他制御テスト
# =====================================================================
class TestModalExclusion:
    """複数モーダルの排他制御が正しく動作すること"""

    def test_only_one_modal_open_at_time(self, page):
        """モーダルは1つしか同時に開けないこと"""
        # 設定モーダルを開く
        page.evaluate("openSettingsModal()")
        page.wait_for_timeout(300)
        expect(page.locator("#modal-settings")).to_have_class(re.compile(r"active"))

        # AI条件モーダルを開こうとする
        page.evaluate("openAiFilterModal()")
        page.wait_for_timeout(300)

        # 設定モーダルは閉じて、AI条件モーダルが開く
        expect(page.locator("#modal-ai-filter")).to_have_class(re.compile(r"active"))
        expect(page.locator("#modal-settings")).not_to_have_class(re.compile(r"active"))
