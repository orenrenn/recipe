import re

FOOD_VECTORS = {
    "玉ねぎ": [1, 0, 0],
    "ねぎ": [0, 1, 0],
    "もも": [0, 0, 1],
    "鶏もも": [1, 0, 1]
}

tNorm = "玉ねぎとねぎを切ります。鶏もも肉を用意します。"

matchedTargetWords = []
for tWord in FOOD_VECTORS.keys():
    searchIdx = 0
    while True:
        searchIdx = tNorm.find(tWord, searchIdx)
        if searchIdx == -1:
            break
        
        isValid = True
        isKatakanaWord = bool(re.match(r"^[\u30A0-\u30FF]+$", tWord))
        if isKatakanaWord:
            prevChar = tNorm[searchIdx - 1] if searchIdx > 0 else ""
            nextChar = tNorm[searchIdx + len(tWord)] if searchIdx + len(tWord) < len(tNorm) else ""
            isPrevKatakana = bool(re.match(r"[\u30A0-\u30FF]", prevChar)) if prevChar else False
            isNextKatakana = bool(re.match(r"[\u30A0-\u30FF]", nextChar)) if nextChar else False
            if isPrevKatakana or isNextKatakana:
                isValid = False
                
        if isValid:
            matchedTargetWords.append({"word": tWord, "start": searchIdx, "end": searchIdx + len(tWord)})
        
        searchIdx += 1

validTargetWords = set()
for i in range(len(matchedTargetWords)):
    isSubsumed = False
    for j in range(len(matchedTargetWords)):
        if i == j: continue
        w_i = matchedTargetWords[i]
        w_j = matchedTargetWords[j]
        if w_i["start"] >= w_j["start"] and w_i["end"] <= w_j["end"] and (w_j["end"] - w_j["start"]) > (w_i["end"] - w_i["start"]):
            isSubsumed = True
            break
    if not isSubsumed:
        validTargetWords.add(matchedTargetWords[i]["word"])

print("tNorm:", tNorm)
print("Matched Words:", [w["word"] for w in matchedTargetWords])
print("Valid Target Words:", list(validTargetWords))

