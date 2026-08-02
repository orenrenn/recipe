import re

def normalizeJapaneseText(str):
    if not str: return ''
    s = str.lower()
    s = re.sub(r'[\s\u3000・,\-_/\\\\()（）\u3001\u3002「」【】〜~！？!?+*＊&＆×ｘ]', '', s)
    return s

def isTriviallyAvailable(ing):
    cleanIng = re.sub(r'[(（].*?[)）]', '', ing)
    cleanIng = normalizeJapaneseText(cleanIng)
    cleanIng = re.sub(r'[0-9０-９]', '', cleanIng)
    cleanIng = re.sub(r'(ml|cc|g|kg|l|かっぷ|おおさじ|こさじ|しょうしょう|てきりょう|ひとつまみ|はい|ふん|くらい|おこのみ|おこのみ|やく|カップ|大さじ|小さじ|少々|適量|杯|分|お好み|約)', '', cleanIng)
    
    ALWAYS_AVAILABLE = ["水", "お湯", "熱湯", "氷", "氷水", "ぬるま湯", "冷水"]
    for a in ALWAYS_AVAILABLE:
        normA = normalizeJapaneseText(a)
        if cleanIng == normA:
            return True
    return False

tests = ['水(熱湯)', '水（200ml）', '水 200ml', 'お湯 適量', '水菜', '氷', '水大さじ2']
for t in tests:
    print(t, "->", isTriviallyAvailable(t))
