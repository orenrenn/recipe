import re

with open('food_vectors.js', 'r') as f:
    text = f.read()

# food_vectors.js contains: window.FOOD_VECTORS = {...}; window.QUERY_VECTORS = {...};
keys = re.findall(r'"([^"]+)":', text)
for k in keys:
    if "う" in k or "に" in k or "ウ" in k or "ニ" in k:
        print("Key matches:", k)
