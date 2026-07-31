import json

with open("food_vectors.js") as f:
    text = f.read()
    start = text.find("window.FOOD_VECTORS = ") + len("window.FOOD_VECTORS = ")
    end = text.find(";", start)
    FOOD_VECTORS = json.loads(text[start:end])

# Check 1: 豚ひき肉 is in PORK and MINCE
v = FOOD_VECTORS["豚ひき肉"]
dims = [i for i, x in enumerate(v) if x > 0]
print(f"豚ひき肉 is in {len(dims)} categories")

# Check 2: "炒めます" matching STIR_FRY?
# We don't have the whole scoring engine here, but we can verify "炒め" is in FOOD_VECTORS
print("炒め in FOOD_VECTORS:", "炒め" in FOOD_VECTORS)

# Check 3: "油揚げ" in FOOD_VECTORS, "揚げ" in FOOD_VECTORS
print("油揚げ in FOOD_VECTORS:", "油揚げ" in FOOD_VECTORS)
print("揚げ in FOOD_VECTORS:", "揚げ" in FOOD_VECTORS)

