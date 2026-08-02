import re

def toHiragana(s):
    result = []
    for c in s:
        code = ord(c)
        if 0x30A1 <= code <= 0x30F6 or code == 0x30F4:
            result.append(chr(code - 0x60))
        else:
            result.append(c)
    return ''.join(result)

def normalizeJapaneseText(str):
    if not str: return ''
    s = str.lower()
    s = re.sub(r'[\s\u3000・,\-_/\\\\()（）\u3001\u3002「」【】〜~！？!?+*＊&＆×ｘ]', '', s)
    return s

def isTriviallyAvailable(ing):
    cleanIng = re.sub(r'[(（].*?[)）]', '', ing)
    cleanIng = toHiragana(normalizeJapaneseText(cleanIng))
    cleanIng = re.sub(r'[0-9０-９\s\u3000]', '', cleanIng)
    cleanIng = re.sub(r'(ml|cc|g|kg|l|かっぷ|おおさじ|こさじ|しょうしょう|てきりょう|ひとつまみ|はい|ふん|くらい|おこのみ|やく)', '', cleanIng)
    ALWAYS_AVAILABLE_HIRA = ["みず", "おゆ", "ねっとう", "こおり", "こおりみず", "ぬるまゆ", "れいすい"]
    return cleanIng in ALWAYS_AVAILABLE_HIRA

tests = ['水(熱湯)', '水（200ml）', '水 200ml', 'お湯 適量', '水菜', '氷', '水大さじ2']
for t in tests:
    print(t, "->", isTriviallyAvailable(t))
