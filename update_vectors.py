import re

with open('extract_synthetic_vectors.py', 'r') as f:
    content = f.read()

new_synonyms = """synonyms = {
    # Meats
    "PORK": ["豚", "豚肉", "ベーコン", "ハム", "ウインナー", "ソーセージ", "豚バラ", "豚こま", "豚ロース", "豚ひき肉", "ぶた", "ぶたにく", "べーこん", "はむ", "ういんなー", "そーせーじ"],
    "BEEF": ["牛", "牛肉", "牛すじ", "牛バラ", "牛ひき肉", "うし", "ぎゅうにく"],
    "CHICKEN": ["鶏", "鶏肉", "鳥肉", "鶏もも", "鶏むね", "ささみ", "手羽先", "手羽元", "鶏ひき肉", "とり", "とりにく"],
    "MINCE": ["ひき肉", "挽肉", "挽き肉", "合い挽き肉", "あいびき肉", "ミンチ", "豚ひき肉", "牛ひき肉", "鶏ひき肉", "みんち"],
    
    # Seafood
    "SALMON": ["鮭", "サケ", "シャケ", "さけ", "しゃけ"],
    "TUNA": ["マグロ", "まぐろ", "ツナ"],
    "BLUE_FISH": ["サバ", "鯖", "アジ", "鯵", "ブリ", "さば", "あじ", "ぶり"],
    "WHITE_FISH": ["鯛", "タラ", "鱈", "たい", "たら"],
    "SQUID_OCTO": ["イカ", "タコ", "いか", "たこ"],
    "SHRIMP_CRAB": ["エビ", "海老", "カニ", "蟹", "えび", "かに"],
    "SHELLFISH": ["ホタテ", "アサリ", "しじみ", "牡蠣", "ほたて", "あさり", "かき"],
    "MENTAIKO": ["明太子", "たらこ", "めんたいこ", "明太", "めんたい"],
    "IKURA": ["イクラ", "いくら"],
    "KAZUNOKO": ["数の子", "かずのこ"],
    "FISH_PASTE": ["ちくわ", "かまぼこ"],
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
    "TAKENOKO": ["たけのこ", "タケノコ", "筍"],
    "MOYASHI": ["もやし"],
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
    "FRIED_TOFU": ["油揚げ", "厚揚げ", "あぶらあげ", "あつあげ"],
    "NATTO": ["納豆", "なっとう"],
    "OKARA": ["おから"],
    "SOY_MILK": ["豆乳", "とうにゅう"],
    "KONJAC": ["こんにゃく", "コンニャク", "蒟蒻", "しらたき", "糸こんにゃく"],
    
    # Mushrooms
    "SHIITAKE": ["しいたけ", "シイタケ", "椎茸"],
    "ENOKI": ["えのき", "エノキ"],
    "SHIMEJI": ["しめじ", "シメジ"],
    "MAITAKE": ["まいたけ", "マイタケ"],
    "ERINGI": ["エリンギ", "えりんぎ"],
    "MUSHROOM": ["マッシュルーム", "まっしゅるーむ"],
    
    # Dairy & Egg
    "EGG": ["卵", "たまご", "玉子", "うずら"],
    "MILK": ["牛乳", "ミルク", "ぎゅうにゅう", "みるく"],
    "CHEESE": ["チーズ", "粉チーズ", "クリームチーズ", "ピザ用チーズ", "とろけるチーズ", "ちーず", "こなちーず", "くりーむちーず"],
    "BUTTER": ["バター", "マーガリン", "有塩バター", "無塩バター", "ばたー", "まーがりん"],
    "CREAM": ["生クリーム", "なまクリーム"],
    
    # Fruit
    "APPLE": ["りんご", "リンゴ", "林檎"],
    "PEAR": ["梨", "なし"],
    "PERSIMMON": ["柿", "かき"],
    "ORANGE": ["みかん", "ミカン", "オレンジ", "蜜柑", "おれんじ"],
    "LEMON": ["レモン", "れもん"],
    "YUZU": ["ユズ", "ゆず"],
    "STRAWBERRY": ["いちご", "イチゴ", "苺"],
    "GRAPE": ["ぶどう", "ブドウ", "マスカット", "ますかっと"],
    "BANANA": ["バナナ", "ばなな"],
    "PEACH": ["桃", "もも"],
    "MELON": ["メロン", "めろん"],
    "WATERMELON": ["スイカ", "すいか"],
    "KIWI": ["キウイ", "きうい"],
    "PINEAPPLE": ["パイナップル", "ぱいなっぷる"],
    "UME": ["梅", "梅干し", "うめぼし", "うめ"],
    
    # Carbs
    "PASTA": ["パスタ", "スパゲッティ", "ぱすた", "すぱげってぃ", "すぱげてぃ"],
    "UDON": ["うどん", "饂飩"],
    "SOBA": ["そば", "蕎麦", "ソバ"],
    "RAMEN": ["ラーメン", "らーめん"],
    "SOUMEN": ["そうめん", "素麺", "ひやむぎ"],
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
    "FRENCH_BREAD": ["フランスパン", "食パン", "ぱん", "パン"],
    
    # Cooking Methods
    "FRY": ["揚げる", "揚げ物", "揚げ", "揚げて"],
    "FRIED_FOOD": ["フライ", "天ぷら", "唐揚げ", "から揚げ", "素揚げ", "竜田揚げ", "カツ", "ふらい", "かつ"],
    "BOIL": ["煮る", "煮物", "煮込み", "煮込む", "煮て", "煮"],
    "BOIL_WATER": ["茹でる", "ゆでる", "茹で", "ゆで", "茹でて", "ゆでて"],
    "GRILL_MEAT": ["焼く", "焼き物", "ソテー", "ロースト", "炙る", "焼き", "焼いて", "そてー", "ろーすと"],
    "STIR_FRY": ["炒める", "炒め物", "炒め", "炒めて"],
    "STEAM": ["蒸す", "蒸し物", "蒸し", "蒸して"],
    
    # Seasonings
    "SALT": ["塩", "塩こしょう", "しお"],
    "SUGAR": ["砂糖", "さとう"],
    "SOY_SAUCE_PURE": ["醤油", "しょうゆ"],
    "SOY_SAUCE_MIX": ["めんつゆ", "ポン酢", "ぽん酢", "ぽんず"],
    "MISO": ["味噌", "みそ"],
    "VINEGAR": ["酢", "す"],
    "SAKE": ["酒", "さけ"],
    "MIRIN": ["みりん", "味醂"],
    "OIL_GENERIC": ["油", "サラダ油", "あぶら"],
    "SESAME_OIL": ["ごま油", "ゴマ油", "ごまあぶら"],
    "OLIVE_OIL": ["オリーブオイル", "おりーぶおいる"],
    "MAYO": ["マヨネーズ", "まよねーず"],
    "KETCHUP": ["ケチャップ", "けちゃっぷ"],
    "SAUCE": ["ソース", "オイスターソース", "そーす", "おいすたーそーす"],
    "BROTH": ["白だし", "出汁", "ダシ", "コンソメ", "鶏ガラスープ", "中華あじ", "煮干し", "だし", "にぼし", "こんそめ", "とりがらすーぷ"],
    "CURRY": ["カレー粉", "カレールー", "かれーこ", "かれーるー"],
    "PEPPER": ["胡椒", "こしょう", "コショウ", "塩こしょう"],
    "SALT_PEPPER": ["塩こしょう"],
    "TOUBANJAN": ["豆板醤", "とうばんじゃん"],
    "KOCHUJAN": ["コチュジャン", "こちゅじゃん"],
    "LAYU": ["ラー油", "らーゆ"],
    "CHILI": ["唐辛子", "とうがらし", "七味", "一味"],
    "WASABI": ["わさび", "ワサビ"],
    "MUSTARD": ["からし", "カラシ", "マスタード", "ますたーど"],
    "SESAME": ["ごま", "ゴマ", "胡麻", "白ごま", "黒ごま", "いりごま", "すりごま"],
    
    # Tools
    "MICROWAVE": ["レンジ", "電子レンジ", "レンチン", "チン", "れんじ"],
    "PAN": ["フライパン", "ふらいぱん"],
    "POT": ["鍋", "なべ"],
    "OVEN_TOASTER": ["オーブン", "トースター", "おーぶん", "とーすたー"],
    "RICE_COOKER": ["炊飯器", "すいはんき"],
    
    # Rice Types
    "WHITE_RICE": ["白米", "はくまい"],
    "BROWN_RICE": ["玄米", "げんまい"],
    "BARLEY_RICE": ["麦", "押し麦", "麦ご飯", "むぎ"],
    "MOCHI_RICE": ["もち米", "もちごめ"]
}"""

new_hierarchy = """hierarchy = {
    "MEAT_GENERIC": ["PORK", "BEEF", "CHICKEN", "MINCE"],
    "SEAFOOD_GENERIC": ["FISH_GENERIC", "SALMON", "TUNA", "BLUE_FISH", "WHITE_FISH", "SQUID_OCTO", "SHRIMP_CRAB", "SHELLFISH", "MENTAIKO", "IKURA", "KAZUNOKO", "FISH_PASTE"],
    "FISH_GENERIC": ["SALMON", "TUNA", "BLUE_FISH", "WHITE_FISH"],
    "VEG_GENERIC": ["CABBAGE", "LETTUCE", "HAKUSAI", "SPINACH", "KOMATSUNA", "BOK_CHOY", "SHISO", "ONION", "GREEN_ONION", "GARLIC", "NIRA", "CARROT", "RADISH", "TURNIP", "RENKON", "GOBO", "TOMATO", "EGGPLANT", "CUCUMBER", "PEPPERS", "PUMPKIN", "GOYA", "OKRA", "ASPARAGUS", "CELERY", "TAKENOKO", "MOYASHI", "POTATO", "SWEET_POTATO", "SATOIMO", "YAMAIMO", "CORN", "GINGER", "MYOGA"],
    "POTATO_GENERIC": ["POTATO", "SWEET_POTATO", "SATOIMO", "YAMAIMO"],
    "BEAN_GENERIC": ["SOYBEAN", "AZUKI", "GREEN_PEAS", "SORAMAME", "INGEN", "SNAP_PEA", "TOFU", "FRIED_TOFU", "NATTO", "OKARA", "SOY_MILK"],
    "MUSHROOM_GENERIC": ["SHIITAKE", "ENOKI", "SHIMEJI", "MAITAKE", "ERINGI", "MUSHROOM"],
    "DAIRY_GENERIC": ["MILK", "CHEESE", "BUTTER", "CREAM"],
    "FRUIT_GENERIC": ["APPLE", "PEAR", "PERSIMMON", "ORANGE", "LEMON", "YUZU", "STRAWBERRY", "GRAPE", "BANANA", "PEACH", "MELON", "WATERMELON", "KIWI", "PINEAPPLE", "UME"],
    "NOODLE_GENERIC": ["PASTA", "UDON", "SOBA", "RAMEN", "SOUMEN"],
    "RICE_GENERIC": ["RICE_TYPES", "ONIGIRI", "RISOTTO", "OKAYU", "CHAHAN", "PILAF", "OMURICE", "TAKIKOMI", "MAZEGOHAN"],
    "BREAD_GENERIC": ["TOAST", "FRENCH_TOAST", "SANDWICH", "FRENCH_BREAD"]
}"""

content = re.sub(r'synonyms = \{.*?\n\}\n', new_synonyms + '\n', content, flags=re.DOTALL)
content = re.sub(r'hierarchy = \{.*?\n\}\n', new_hierarchy + '\n', content, flags=re.DOTALL)

with open('extract_synthetic_vectors.py', 'w') as f:
    f.write(content)

