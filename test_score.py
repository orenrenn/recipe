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
        elif len(qWord) >= 2 and qWordHira in qHira:
            idx = qHira.find(qWordHira); matchLen = len(qWordHira)
        elif len(qNorm) >= 2 and qNorm in qWord:
            idx = 0; matchLen = len(qNorm)
        elif len(qNorm) >= 2 and qHira in qWordHira:
            idx = 0; matchLen = len(qHira)
            
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
    "豆スープリゾット",
    "生米：1合（洗わずに使います）",
    "余った豆スープ ＋ お湯： 合計で600〜800ml",
    "お好みのキノコ（しめじ、マッシュルームなど）： 1/2〜1パック",
    "オリーブオイル（またはバター）： 大さじ1.5",
    "バター（仕上げ用）： 20g",
    "粉チーズ： 大さじ2〜3",
    "塩、黒こしょう： 少々",
    "コンソメ顆粒： 少々",
    "下準備余った豆スープと追加のお湯を合わせ、別の小鍋やレンジでしっかり熱い状態にしておきます。ここで一度味見をして、味が薄ければコンソメ顆粒を少し足して整えておきます。",
    "キノコの旨みを引き出すフライパンにオリーブオイル（またはバター）を中弱火で熱し、キノコを炒めます。キノコがしんなりとして、香ばしい香りが立つまでしっかり炒めるのがポイントです。",
    "お米を炒めるキノコが炒まったら、そこに**洗っていない生米（1合）**を加えます。中火にし、お米のまわりが少し透き通るまで、木べら等で炒め合わせます。",
    "熱いスープを少しずつ加える熱々にしておいたスープをお玉2〜3杯分（お米がひたひたになる程度）加えます。フツフツと軽く沸き立つ中弱火をキープします。",
    "触りすぎずに煮るぐるぐると混ぜすぎず、たまに鍋底が焦げ付かないよう優しくこする程度にします。水分が減って鍋底が見えるようになってきたら、再びスープをお玉1〜2杯足す、という作業を15〜18分ほど繰り返します。",
    "アルデンテを確認して火を止めるお米を少し食べてみて、中心にわずかに芯が残る程度（アルデンテ）になっていればベストなタイミングです。水分が少し残り、全体がトロッとした状態で火を止めます。",
    "仕上げ（乳化させる）火を止めたフライパンに、**仕上げ用のバター（20g）と粉チーズ（大さじ2〜3）**を一気に加えます。フライパンを揺すりながら、全体を手早く空気を含ませるように混ぜ合わせます。ここでリゾット特有のクリーミーさが生まれます。",
    "完成味見をして、足りなければ塩で整えます。お皿に盛り付け、お好みでたっぷりの黒こしょうを挽いて完成です。"
]

total = 0
for t in texts:
    score = compute_search_match_score("揚げ", t)
    if score > 0:
        print(f"Matched: '{t[:30]}...' with score {score}")
    total += score
    
print(f"TOTAL RECIPE SCORE: {total}")
