import json

# Specific synonym clusters (Query only activates its own cluster)
# Specific synonym clusters (Query only activates its own cluster)
# Specific synonym clusters (Query only activates its own cluster)
# Specific synonym clusters (Query only activates its own cluster)
synonyms = {
    # Meats
    "PORK": ["豚", "豚肉", "ベーコン", "ハム", "ウインナー", "ソーセージ", "豚バラ", "豚こま", "豚ロース", "豚ひき肉", "ぶた", "ぶたにく", "べーこん", "はむ", "ういんなー", "そーせーじ"],
    "BEEF": ["牛", "牛肉", "牛すじ", "牛バラ", "牛ひき肉", "うし", "ぎゅうにく"],
    "CHICKEN": ["鶏", "鶏肉", "鳥肉", "鶏もも", "鶏むね", "ささみ", "手羽先", "手羽元", "鶏ひき肉", "とり", "とりにく"],
    "MINCE": ["ひき肉", "挽肉", "挽き肉", "合い挽き肉", "あいびき肉", "ミンチ", "豚ひき肉", "牛ひき肉", "鶏ひき肉", "みんち"],
    
    # Seafood
    "SALMON": ["鮭", "サケ", "シャケ", "さけ", "しゃけ"],
    "TUNA": ["マグロ", "まぐろ", "ツナ"],
    "BLUE_FISH": ["サバ", "鯖", "アジ", "鯵", "ブリ", "さば", "あじ", "ぶり", "サンマ", "さんま", "秋刀魚", "イワシ", "いわし", "鰯", "カツオ", "かつお", "鰹"],
    "WHITE_FISH": ["鯛", "タラ", "鱈", "たい", "たら", "ヒラメ", "ひらめ", "平目", "カレイ", "かれい", "鰈", "フグ", "ふぐ", "河豚"],
    "SQUID_OCTO": ["イカ", "タコ", "いか", "たこ"],
    "SHRIMP_CRAB": ["エビ", "海老", "カニ", "蟹", "えび", "かに"],
    "SHELLFISH": ["ホタテ", "アサリ", "しじみ", "牡蠣", "ほたて", "あさり", "かき", "アワビ", "あわび", "サザエ", "さざえ", "ハマグリ", "はまぐり"],
    "MENTAIKO": ["明太子", "たらこ", "めんたいこ", "明太", "めんたい"],
    "IKURA": ["イクラ", "いくら"],
    "KAZUNOKO": ["数の子", "かずのこ"],
    "UNI": ["ウニ", "うに", "海胆", "雲丹"],
    "EEL": ["うなぎ", "鰻", "ウナギ", "あなご", "穴子", "アナゴ"],
    "FISH_PASTE": ["ちくわ", "かまぼこ", "カニカマ", "かにかま"],
    "SEAWEED": ["海藻", "わかめ", "ワカメ", "昆布", "コンブ", "海苔", "ひじき", "もずく", "かいそう", "こんぶ", "のり"],
    
    # Vegetables
    "CABBAGE": ["キャベツ", "きゃべつ"],
    "LETTUCE": ["レタス", "れたす"],
    "HAKUSAI": ["白菜", "はくさい"],
    "SPINACH": ["ほうれん草", "ほうれんそう"],
    "KOMATSUNA": ["小松菜", "こまつな"],
    "BOK_CHOY": ["青梗菜", "チンゲン菜", "ちんげんさい"],
    "SHISO": ["大葉", "シソ", "しそ"],
    "ONION": ["玉ねぎ", "タマネギ", "玉葱", "たまねぎ"],
    "GREEN_ONION": ["ネギ", "葱", "長ネギ", "長ねぎ", "ねぎ", "ながねぎ"],
    "GARLIC": ["にんにく", "ニンニク"],
    "NIRA": ["ニラ", "にら"],
    "CARROT": ["にんじん", "人参"],
    "RADISH": ["大根", "だいこん"],
    "TURNIP": ["カブ", "かぶ"],
    "RENKON": ["れんこん", "レンコン"],
    "GOBO": ["ごぼう", "牛蒡"],
    "TOMATO": ["トマト", "プチトマト", "ミニトマト", "とまと", "ぷちとまと", "みにとまと"],
    "EGGPLANT": ["茄子", "ナス", "なす"],
    "CUCUMBER": ["きゅうり", "キュウリ", "胡瓜"],
    "PEPPERS": ["ピーマン", "パプリカ", "ぴーまん", "ぱぷりか"],
    "PUMPKIN": ["かぼちゃ", "カボチャ", "南瓜"],
    "GOYA": ["ゴーヤ", "ごーや"],
    "OKRA": ["オクラ", "おくら"],
    "ASPARAGUS": ["アスパラガス", "アスパラ", "あすぱらがす", "あすぱら"],
    "CELERY": ["セロリ", "せろり"],
    "ZUCCHINI": ["ズッキーニ", "ずっきーに"],
    "BROCCOLI": ["ブロッコリー", "カリフラワー"],
    "TAKENOKO": ["たけのこ", "タケノコ", "筍", "竹の子"],
    "MOYASHI": ["もやし", "モヤシ"],
    "HERB": ["パセリ", "パクチー", "バジル", "ミント", "ハーブ", "香草"],
    "POTATO": ["じゃがいも", "ジャガイモ", "ポテト", "ぽてと"],
    "SWEET_POTATO": ["さつまいも", "サツマイモ", "薩摩芋"],
    "SATOIMO": ["里芋", "さといも"],
    "YAMAIMO": ["長芋", "山芋", "ながいも", "やまいも"],
    "CORN": ["とうもろこし", "コーン", "こーん"],
    "GINGER": ["生姜", "しょうが"],
    "MYOGA": ["みょうが", "ミョウガ"],
    
    # Beans & Others
    "SOYBEAN": ["大豆", "黒豆", "枝豆", "えだまめ", "だいず", "くろまめ"],
    "AZUKI": ["小豆", "あずき"],
    "GREEN_PEAS": ["グリンピース", "グリーンピース", "ピース", "えんどう豆"],
    "SORAMAME": ["そら豆", "そらまめ"],
    "INGEN": ["インゲン", "いんげん"],
    "SNAP_PEA": ["スナップエンドウ"],
    "TOFU": ["豆腐", "とうふ"],
    "FRIED_TOFU": ["油揚げ", "あぶらあげ", "厚揚げ", "あつあげ", "がんもどき", "がんも", "薄揚げ"],
    "NATTO": ["納豆", "なっとう"],
    "OKARA": ["おから", "オカラ"],
    "SOY_MILK": ["豆乳", "とうにゅう"],
    "KONJAC": ["こんにゃく", "コンニャク", "蒟蒻", "しらたき", "糸こんにゃく"],
    
    # Mushrooms
    "SHIITAKE": ["しいたけ", "シイタケ", "椎茸"],
    "ENOKI": ["えのき", "エノキ", "えのき茸"],
    "SHIMEJI": ["しめじ", "シメジ"],
    "MAITAKE": ["まいたけ", "マイタケ", "舞茸"],
    "ERINGI": ["エリンギ", "えりんぎ"],
    "MUSHROOM": ["マッシュルーム", "まっしゅるーむ"],
    "KIKURAGE": ["きくらげ", "キクラゲ", "木耳"],
    "NAMEKO": ["なめこ", "ナメコ"],
    
    # Dairy & Egg
    "EGG": ["卵", "たまご", "玉子", "うずら"],
    "MILK": ["牛乳", "ミルク", "ぎゅうにゅう", "みるく"],
    "CHEESE": ["チーズ", "粉チーズ", "クリームチーズ", "ピザ用チーズ", "とろけるチーズ", "ちーず", "こなちーず", "くりーむちーず"],
    "BUTTER": ["バター", "マーガリン", "有塩バター", "無塩バター", "ばたー", "まーがりん"],
    "CREAM": ["生クリーム", "なまクリーム"],
    
    # Fruit
    "APPLE": ["りんご", "リンゴ", "林檎"],
    "PEAR": ["梨", "なし", "ナシ", "洋梨"],
    "PERSIMMON": ["柿", "かき"],
    "BANANA": ["バナナ", "ばなな"],
    "GRAPE": ["ぶどう", "ブドウ", "葡萄", "マスカット"],
    "KIWI": ["キウイ", "きうい"],
    "MELON": ["メロン", "めろん", "スイカ", "すいか", "西瓜"],
    "CITRUS": ["みかん", "ミカン", "オレンジ", "おれんじ", "レモン", "れもん", "ゆず", "柚子", "すだち"],
    "PEACH": ["桃", "もも", "モモ"],
    "UME": ["梅", "梅干し", "うめぼし", "うめ", "梅肉"],
    "PINEAPPLE": ["パイナップル", "ぱいなっぷる"],
    
    # Carbs
    "PASTA": ["パスタ", "スパゲッティ", "ぱすた", "すぱげってぃ", "すぱげてぃ"],
    "UDON": ["うどん", "饂飩"],
    "SOBA": ["そば", "蕎麦", "ソバ"],
    "RAMEN": ["ラーメン", "らーめん", "中華麺", "ちゅうかめん"],
    "SOUMEN": ["そうめん", "素麺", "ひやむぎ", "冷麦"],
    "HARUSAME": ["春雨", "はるさめ", "マロニー"],
    "ONIGIRI": ["おにぎり", "おむすび", "オニギリ"],
    "RISOTTO": ["リゾット", "りぞっと"],
    "OKAYU": ["おかゆ", "お粥"],
    "CHAHAN": ["チャーハン", "炒飯", "ちゃーはん"],
    "PILAF": ["ピラフ", "ぴらふ"],
    "OMURICE": ["オムライス", "おむらいす"],
    "TAKIKOMI": ["炊き込みご飯", "炊き込みごはん", "炊き込み", "たきこみごはん"],
    "MAZEGOHAN": ["混ぜご飯", "まぜごはん"],
    "TOAST": ["トースト", "とーすと"],
    "FRENCH_TOAST": ["フレンチトースト", "ふれんちとーすと"],
    "SANDWICH": ["サンドイッチ", "さんどいっち"],
    "FRENCH_BREAD": ["フランスパン", "ふらんすぱん", "バゲット"],
    "CEREAL": ["オートミール", "シリアル", "コーンフレーク", "グラノーラ"],
    
    # Flours & Starches
    "FLOUR": ["小麦粉", "こむぎこ", "薄力粉", "はくりきこ", "強力粉", "きょうりきこ", "米粉", "こめこ", "中力粉"],
    "POTATO_STARCH": ["片栗粉", "かたくりこ"],
    "BREAD_CRUMBS": ["パン粉", "ぱんこ"],
    "BAKING_POWDER": ["ベーキングパウダー", "べーきんぐぱうだー"],
    "YEAST": ["ドライイースト", "イースト"],

    # Cooking Methods
    "FRY": ["揚げる", "揚げ物", "揚げ", "揚げて"],
    "FRIED_FOOD": ["フライ", "天ぷら", "唐揚げ", "から揚げ", "素揚げ", "竜田揚げ", "カツ", "ふらい", "かつ"],
    "BOIL": ["煮る", "煮物", "煮込み", "煮込む", "煮て", "煮"],
    "BOIL_WATER": ["茹でる", "ゆでる", "茹で", "ゆで", "茹でて", "ゆでて"],
    "GRILL_MEAT": ["焼く", "焼き物", "ソテー", "ロースト", "炙る", "焼き", "焼いて", "そてー", "ろーすと"],
    "STIR_FRY": ["炒める", "炒め物", "炒め", "炒めて"],
    "STEAM": ["蒸す", "蒸し物", "蒸し", "蒸して"],
    
    # Seasonings
    "SALT": ["塩", "しお", "ソルト", "岩塩"],
    "SUGAR": ["砂糖", "さとう", "サトウ", "グラニュー糖", "上白糖", "はちみつ", "ハチミツ"],
    "SOY_SAUCE": ["醤油", "しょうゆ", "ショウユ", "めんつゆ", "白だし", "ポン酢"],
    "VINEGAR": ["酢", "す", "お酢", "黒酢"],
    "MIRIN_SAKE": ["みりん", "味醂", "酒", "料理酒", "さけ"],
    "MISO": ["味噌", "みそ", "ミソ", "白味噌", "赤味噌", "合わせ味噌"],
    "OIL": ["油", "あぶら", "サラダ油", "ごま油", "ゴマ油", "オリーブオイル", "バター"],
    "MAYO_KETCHUP": ["マヨネーズ", "マヨ", "ケチャップ", "ソース", "ウスターソース", "中濃ソース", "お好みソース"],
    "SOUP_STOCK": ["コンソメ", "鶏ガラスープ", "だしの素", "出汁", "ダシ", "ブイヨン", "ウェイパァー", "香味ペースト", "中華あじ", "煮干し", "こんそめ", "とりがらすーぷ"],
    "SPICE": ["こしょう", "胡椒", "コショウ", "塩こしょう", "ブラックペッパー", "粗挽き黒こしょう", "カレー粉", "カレールー"],
    "MUSTARD_WASABI": ["マスタード", "からし", "カラシ", "わさび", "ワサビ", "山葵", "柚子胡椒", "ゆずこしょう"],
    "ASIAN_SAUCE": ["豆板醤", "とうばんじゃん", "コチュジャン", "甜麺醤", "オイスターソース", "コチジャン", "ナンプラー", "スイートチリソース"],
    "CHILI": ["唐辛子", "とうがらし", "鷹の爪", "ラー油", "七味", "一味"],
    "CURRY": ["カレー粉", "カレールー", "かれーこ", "かれーるー", "シチュールー", "ハヤシルー"],
    "KATSUO_KONBU": ["かつお節", "鰹節", "かつおぶし", "塩昆布", "塩こんぶ", "昆布", "こんぶ", "煮干し"],
    "SESAME": ["ごま", "ゴマ", "胡麻", "白ごま", "黒ごま", "いりごま", "すりごま"],
    "NUTS": ["くるみ", "クルミ", "アーモンド", "ピーナッツ", "落花生", "カシューナッツ", "松の実", "ナッツ", "ピスタチオ"],
    "CANNED": ["ツナ缶", "ツナ", "トマト缶", "カットトマト", "ホールトマト", "サバ缶", "コーン缶"],
    
    # Tools
    "MICROWAVE": ["レンジ", "電子レンジ", "レンチン", "チン", "れんじ"],
    "PAN": ["フライパン", "ふらいぱん"],
    "POT": ["鍋", "なべ"],
    "OVEN_TOASTER": ["オーブン", "トースター", "おーぶん", "とーすたー"],
    "RICE_COOKER": ["炊飯器", "すいはんき"],
    
    # Rice Types
    "RICE_TYPES": ["白米", "玄米", "押し麦", "無洗米", "もち米", "ご飯", "ごはん", "ライス"]
}

# Generic Parent Categories (Target words project upwards to these, Query words match them exactly)
parent_categories = {
    "MEAT_GENERIC": ["肉", "お肉"],
    "SEAFOOD_GENERIC": ["魚介", "魚介類", "シーフード"],
    "FISH_GENERIC": ["魚", "しらす", "ちりめんじゃこ"],
    "VEG_GENERIC": ["野菜"],
    "POTATO_GENERIC": ["いも", "芋"],
    "BEAN_GENERIC": ["豆", "大豆製品"],
    "MUSHROOM_GENERIC": ["きのこ", "キノコ"],
    "DAIRY_GENERIC": ["乳製品"],
    "FRUIT_GENERIC": ["果物", "フルーツ"],
    "NOODLE_GENERIC": ["麺", "めん"],
    "RICE_GENERIC": ["米", "ご飯", "ごはん", "ライス"],
    "BREAD_GENERIC": ["パン"],
    "CARB_GENERIC": ["ご飯", "パン", "麺", "粉", "炭水化物"]
}

# Hierarchy: Which synonym clusters belong to which parent
hierarchy = {
    "MEAT_GENERIC": ["PORK", "BEEF", "CHICKEN", "MINCE", "PROCESSED_MEAT"],
    "SEAFOOD_GENERIC": ["FISH_GENERIC", "SALMON", "TUNA", "BLUE_FISH", "WHITE_FISH", "SQUID_OCTO", "SHRIMP_CRAB", "SHELLFISH", "MENTAIKO", "IKURA", "KAZUNOKO", "UNI", "EEL", "FISH_PASTE"],
    "FISH_GENERIC": ["SALMON", "TUNA", "BLUE_FISH", "WHITE_FISH", "EEL"],
    "VEG_GENERIC": ["CABBAGE", "LETTUCE", "HAKUSAI", "SPINACH", "KOMATSUNA", "BOK_CHOY", "SHISO", "ONION", "GREEN_ONION", "GARLIC", "NIRA", "CARROT", "RADISH", "TURNIP", "RENKON", "GOBO", "TOMATO", "EGGPLANT", "CUCUMBER", "PEPPERS", "PUMPKIN", "GOYA", "OKRA", "ASPARAGUS", "CELERY", "ZUCCHINI", "BROCCOLI", "TAKENOKO", "MOYASHI", "HERB", "POTATO", "SWEET_POTATO", "SATOIMO", "YAMAIMO", "CORN", "GINGER", "MYOGA"],
    "POTATO_GENERIC": ["POTATO", "SWEET_POTATO", "SATOIMO", "YAMAIMO", "CHESTNUT"],
    "BEAN_GENERIC": ["SOYBEAN", "AZUKI", "GREEN_PEAS", "SORAMAME", "INGEN", "SNAP_PEA", "TOFU", "FRIED_TOFU", "NATTO", "OKARA", "SOY_MILK"],
    "MUSHROOM_GENERIC": ["SHIITAKE", "ENOKI", "SHIMEJI", "MAITAKE", "ERINGI", "MUSHROOM", "KIKURAGE", "NAMEKO"],
    "DAIRY_GENERIC": ["MILK", "CHEESE", "YOGURT", "BUTTER"],
    "FRUIT_GENERIC": ["APPLE", "BANANA", "GRAPE", "KIWI", "MELON", "CITRUS", "PEACH", "PEAR", "UME", "PINEAPPLE"],
    "NOODLE_GENERIC": ["PASTA", "UDON", "SOBA", "RAMEN", "SOUMEN", "HARUSAME"],
    "RICE_GENERIC": ["RICE_TYPES", "ONIGIRI", "RISOTTO", "OKAYU", "CHAHAN", "PILAF", "OMURICE", "TAKIKOMI", "MAZEGOHAN"],
    "BREAD_GENERIC": ["TOAST", "FRENCH_TOAST", "SANDWICH", "FRENCH_BREAD"],
    "CARB_GENERIC": ["RICE_GENERIC", "BREAD_GENERIC", "NOODLE_GENERIC", "CEREAL", "FLOUR", "POTATO_STARCH", "BREAD_CRUMBS"]
}

# Hiragana Aliases strictly for QUERY matching
query_aliases = {
    "たら": "WHITE_FISH",
    "えび": "SHRIMP_CRAB",
    "あさり": "SHELLFISH",
    "しそ": "SHISO",
    "にら": "NIRA",
    "かぶ": "RADISH",
    "なす": "EGGPLANT",
    "ゆず": "YUZU",
    "そば": "SOBA",
    "ねぎ": "GREEN_ONION",
    "みそ": "MISO",
    "だいこん": "RADISH",
    "たまねぎ": "ONION",
    "うめ": "UME",
    "揚げ": "FRY",
    "焼き": "GRILL_MEAT",
    "炒め": "STIR_FRY",
    "蒸し": "STEAM",
    "煮": "BOIL",
    "煮込み": "BOIL",
    "茹で": "BOIL_WATER",
    "にく": "MEAT_GENERIC",
    "おにく": "MEAT_GENERIC",
    "ぶたにく": "PORK",
    "ぶた": "PORK",
    "ぎゅうにく": "BEEF",
    "うし": "BEEF",
    "とりにく": "CHICKEN",
    "とり": "CHICKEN",
    "ひきにく": "MINCE",
    "さかな": "FISH_GENERIC",
    "ぎょかい": "SEAFOOD_GENERIC",
    "やさい": "VEG_GENERIC",
    "いも": "POTATO_GENERIC",
    "まめ": "BEAN_GENERIC",
    "きのこ": "MUSHROOM_GENERIC",
    "たまご": "EGG",
    "ぎゅうにゅう": "MILK",
    "にゅうせいひん": "DAIRY_GENERIC",
    "くだもの": "FRUIT_GENERIC",
    "フルーツ": "FRUIT_GENERIC",
    "あげる": "FRY",
    "あげもの": "FRIED_FOOD",
    "にる": "BOIL",
    "ゆでる": "BOIL_WATER",
    "やく": "GRILL_MEAT",
    "いためる": "STIR_FRY",
    "むす": "STEAM",
    "めん": "NOODLE_GENERIC",
    "こめ": "RICE_GENERIC",
    "ごはん": "RICE_GENERIC",
    "さとう": "SUGAR",
    "しお": "SALT",
    "しょうゆ": "SOY_SAUCE_PURE",
    "す": "VINEGAR",
    "さけ": "SAKE",
    "あぶら": "OIL_GENERIC",
    "だし": "BROTH"
}

# Combine all dimensions
dimensions = list(synonyms.keys()) + list(parent_categories.keys())
num_categories = len(dimensions)

def build_vector(cat_name):
    vec = [0.0] * num_categories
    if cat_name in dimensions:
        vec[dimensions.index(cat_name)] = 1.0
    
    # If it's a generic (parent) category, project DOWNWARDS to all children
    if cat_name in hierarchy:
        for child in hierarchy[cat_name]:
            if child in dimensions:
                vec[dimensions.index(child)] = 1.0
    return vec

# 1. Build TARGET_VECTORS (Generic terms are FAT, Specific terms are SPARSE)
target_vectors = {}
for cat_name, words in synonyms.items():
    vec = build_vector(cat_name)
    for word in words:
        if word not in target_vectors:
            target_vectors[word] = [0.0] * num_categories
        for i in range(num_categories):
            if vec[i] > 0:
                target_vectors[word][i] = 1.0

for cat_name, words in parent_categories.items():
    vec = build_vector(cat_name)
    for word in words:
        if word not in target_vectors:
            target_vectors[word] = [0.0] * num_categories
        for i in range(num_categories):
            if vec[i] > 0:
                target_vectors[word][i] = 1.0

# 2. Build QUERY_VECTORS (Generic terms are SPARSE, Specific terms are FAT)
query_vectors = {}
for alias, target_cat in query_aliases.items():
    query_vectors[alias] = build_vector(target_cat)

for cat_name, words in synonyms.items():
    q_vec = build_vector(cat_name)
    for word in words:
        if word not in query_vectors:
            query_vectors[word] = [0.0] * num_categories
        for i in range(num_categories):
            if q_vec[i] > 0:
                query_vectors[word][i] = 1.0

for cat_name, words in parent_categories.items():
    vec = build_vector(cat_name)
    for word in words:
        query_vectors[word] = vec

output_path = "food_vectors.js"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("window.FOOD_VECTORS = ")
    json.dump(target_vectors, f, ensure_ascii=False)
    f.write(";\n")
    f.write("window.QUERY_VECTORS = ")
    json.dump(query_vectors, f, ensure_ascii=False)
    f.write(";\n")

print(f"Generated {len(target_vectors)} TARGET_VECTORS and {len(query_vectors)} QUERY_VECTORS using Downward Expansion across {num_categories} dimensions.")
