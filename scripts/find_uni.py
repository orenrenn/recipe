import json

def normalize_text(s):
    import unicodedata, re
    if not s: return ""
    s = unicodedata.normalize('NFKC', s).lower()
    return re.sub(r'[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】]', '', s)

def to_hiragana(s):
    res = ""
    for c in s:
        code = ord(c)
        if 0x30A1 <= code <= 0x30F6 or code == 0x30F4:
            res += chr(code - 0x60)
        else:
            res += c
    return res

recipes = [
    {
        "title": "玄米と麦と白米",
        "ingredients": ["玄米：3合（60% - 不動のメイン）", "押し麦：1合（20% - プチプチ食感をしっかり味わえる）", "白米：1合（20% - 全体のまとまり役）"],
        "steps": [],
        "memo": ""
    },
    {
        "title": "豆スープリゾット",
        "ingredients": [
            "生米：1合（洗わずに使います）",
            "余った豆スープ＋お湯：合計で600〜800ml",
            "お好みのキノコ（しめじ、マッシュルームなど）：1/2パック",
            "粉チーズ、粗挽き黒こしょう：お好みで",
            "フライパンにオリーブオイル（大さじ1）とみじん切りにしたニンニク（1片）を入れ、弱火で香りを出す"
        ],
        "steps": [],
        "memo": ""
    }
]

qNorm = normalize_text("ウニ")
qHira = to_hiragana(qNorm)

for r in recipes:
    texts = [r['title']] + r['ingredients'] + r['steps'] + [r['memo']]
    for t in texts:
        if not t: continue
        tNorm = normalize_text(t)
        tHira = to_hiragana(tNorm)
        if qNorm in tNorm or qHira in tHira:
            print(f"Match found in: {t}")
            print(f"tNorm: {tNorm}")
            print(f"tHira: {tHira}")

