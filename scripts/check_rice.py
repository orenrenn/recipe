import json
import re

with open('food_vectors.js', 'r') as f:
    content = f.read()

food_match = re.search(r'window\.FOOD_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)
food_vecs = json.loads(food_match.group(1)) if food_match else {}

print("米 in keys:", "米" in food_vecs)
print("おくら in keys:", "おくら" in food_vecs)
print("にんにく in keys:", "にんにく" in food_vecs)
