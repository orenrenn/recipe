import re

def to_hiragana(s):
    res = ""
    for c in s:
        code = ord(c)
        if 0x30A1 <= code <= 0x30F6 or code == 0x30F4:
            res += chr(code - 0x60)
        else:
            res += c
    return res

text1 = "玄米：3合（60% - 不動のメイン） ・押し麦：1合（20% - プチプチ食感をしっかり味わえる） ・白米：1合（20% - 全体のまとまり役）"
text2 = "生米：1合（洗わずに使います）・余った豆スープ＋お湯：合計で600〜800ml・お好みのキノコ（しめじ、マッシュルームなど）：1/2パック・粉チーズ、粗挽き黒こしょう：お好みで・フライパンにオリーブオイル（大さじ1）とみじん切りにしたニンニク（1片）を入れ、弱火で香りを出す"

norm1 = re.sub(r'[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】]', '', text1)
norm2 = re.sub(r'[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】]', '', text2)

hira1 = to_hiragana(norm1)
hira2 = to_hiragana(norm2)

print("hira1:", hira1)
print("hira2:", hira2)
print("hira1 contains うに?", "うに" in hira1)
print("hira2 contains うに?", "うに" in hira2)
