function normalizeJapaneseText(str) {
  if (!str) return '';
  let s = String(str).normalize('NFKC').toLowerCase();
  s = s.replace(/[\s\u3000・,\-_\/\\\(\)\u3001\u3002\u300C\u300D\u3010\u3011「」【】〜~！？!\?\+\*＊&＆×ｘ]/g, '');
  return s;
}

function toHiragana(str) {
  if (!str) return '';
  return String(str).replace(/[\u30a1-\u30f6\u30f4]/g, match => String.fromCharCode(match.charCodeAt(0) - 0x60));
}

function isTriviallyAvailable(ing) {
  let cleanIng = String(ing).replace(/[(（].*?[)）]/g, '');
  cleanIng = toHiragana(normalizeJapaneseText(cleanIng));
  cleanIng = cleanIng.replace(/[0-9０-９\s\u3000]/g, '')
                     .replace(/(ml|cc|g|kg|l|かっぷ|おおさじ|こさじ|しょうしょう|てきりょう|ひとつまみ|はい|ふん|くらい|おこのみ|やく)/g, '');
  const ALWAYS_AVAILABLE_HIRA = ["みず", "おゆ", "ねっとう", "こおり", "こおりみず", "ぬるまゆ", "れいすい"];
  return ALWAYS_AVAILABLE_HIRA.includes(cleanIng);
}

const tests = ['水(熱湯)', '水（200ml）', '水 200ml', 'お湯 適量', '水菜', '氷', '水大さじ2'];
for (const t of tests) {
  console.log(t, "->", isTriviallyAvailable(t));
}
