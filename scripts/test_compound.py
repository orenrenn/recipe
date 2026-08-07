import json
import re

def normalize_japanese_text(s):
    if not s: return ""
    import unicodedata
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r'[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】]', '', s)
    return s

def to_hiragana(s):
    if not s: return ""
    return "".join(chr(ord(c) - 0x60) if 0x30a1 <= ord(c) <= 0x30f6 or ord(c) == 0x30f4 else c for c in s)

with open("food_vectors.js") as f:
    text = f.read()
    start = text.find("window.FOOD_VECTORS = ") + len("window.FOOD_VECTORS = ")
    end = text.find(";", start)
    FOOD_VECTORS = json.loads(text[start:end])
    
    start2 = text.find("window.QUERY_VECTORS = ") + len("window.QUERY_VECTORS = ")
    end2 = text.find(";\n", start2)
    QUERY_VECTORS = json.loads(text[start2:end2])

ALL_QUERY_WORDS = {**FOOD_VECTORS, **QUERY_VECTORS}

def compute_search_match_score(query_word, target_text):
    qNorm = normalize_japanese_text(query_word)
    tNorm = normalize_japanese_text(target_text)
    if not qNorm or not tNorm: return 0

    qHira = to_hiragana(qNorm)
    isSemanticQuery = qNorm in ALL_QUERY_WORDS or qHira in ALL_QUERY_WORDS
    
    isAllHiragana = bool(re.match(r"^[\u3040-\u309F]+$", qNorm))
    if not isSemanticQuery and isAllHiragana and len(qNorm) <= 2:
        return 0

    maxScore = 0
    baseSubstringScore = 0.5 if isSemanticQuery else 2.5

    if qNorm in tNorm:
        maxScore = baseSubstringScore
    else:
        tHira = to_hiragana(tNorm)
        if qHira in tHira and maxScore < baseSubstringScore - 0.1:
            maxScore = baseSubstringScore - 0.1

    maxSemanticSim = 0
    matchedWords = []
    
    for qWord in ALL_QUERY_WORDS:
        qWordHira = to_hiragana(qWord)
        idx = -1
        matchLen = 0
        
        if qNorm == qWord or qHira == qWordHira:
            idx = 0; matchLen = len(qNorm)
        elif len(qWord) >= 2 and qWord in qNorm:
            idx = qNorm.find(qWord); matchLen = len(qWord)
        elif len(qWord) >= 2 and qHira in qWordHira:
            idx = qHira.find(qWordHira); matchLen = len(qWordHira)
            
        if idx != -1:
            matchedWords.append({"word": qWord, "start": idx, "end": idx + matchLen})
            
    queryWordsToUse = []
    for i in range(len(matchedWords)):
        isSubsumed = False
        for j in range(len(matchedWords)):
            if i == j: continue
            if matchedWords[i]["start"] >= matchedWords[j]["start"] and \
               matchedWords[i]["end"] <= matchedWords[j]["end"] and \
               (matchedWords[j]["end"] - matchedWords[j]["start"]) > (matchedWords[i]["end"] - matchedWords[i]["start"]):
                isSubsumed = True
                break
        if not isSubsumed:
            queryWordsToUse.append(matchedWords[i]["word"])
            
    for qWord in queryWordsToUse:
        qVec = ALL_QUERY_WORDS[qWord]
        for tWord in FOOD_VECTORS:
            isTargetMatch = False
            if tWord in tNorm:
                isKatakanaWord = bool(re.match(r"^[\u30A0-\u30FF]+$", tWord))
                if isKatakanaWord:
                    matchIdx = tNorm.find(tWord)
                    while matchIdx != -1:
                        prevChar = tNorm[matchIdx - 1] if matchIdx > 0 else ""
                        nextChar = tNorm[matchIdx + len(tWord)] if matchIdx + len(tWord) < len(tNorm) else ""
                        isPrevKatakana = bool(re.match(r"[\u30A0-\u30FF]", prevChar)) if prevChar else False
                        isNextKatakana = bool(re.match(r"[\u30A0-\u30FF]", nextChar)) if nextChar else False
                        if not isPrevKatakana and not isNextKatakana:
                            isTargetMatch = True
                            break
                        matchIdx = tNorm.find(tWord, matchIdx + 1)
                else:
                    isTargetMatch = True
                    
            if isTargetMatch:
                tVec = FOOD_VECTORS[tWord]
                dot = sum(q * t for q, t in zip(qVec, tVec))
                if dot > 0:
                    print(f"  MATCH! qWord={qWord} tWord={tWord} dot={dot}")
                if dot > maxSemanticSim:
                    maxSemanticSim = dot

    if maxSemanticSim >= 0.55:
        semanticScore = (maxSemanticSim - 0.5) * 14.0
        maxScore = max(maxScore, semanticScore)
        
    return maxScore if maxScore >= 1.8 else 0

texts = [
    "ミニトマトのサラダ",
    "粉チーズをかける",
    "豚バラの炒め物"
]

queries = ["トマト", "チーズ", "豚肉"]

for q, t in zip(queries, texts):
    print(f"\nQuery: {q}  Text: {t}")
    score = compute_search_match_score(q, t)
    print(f"Final Score: {score}")

