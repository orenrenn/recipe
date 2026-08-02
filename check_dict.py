import json
import re

with open('food_vectors.js', 'r') as f:
    content = f.read()

food_match = re.search(r'window\.FOOD_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)
query_match = re.search(r'window\.QUERY_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)

food_vecs = json.loads(food_match.group(1)) if food_match else {}
query_vecs = json.loads(query_match.group(1)) if query_match else {}

for w in ["にんにく", "ニンニク", "オクラ", "おくら", "長芋", "ながいも", "ナガイモ"]:
    print(f"{w} in FOOD: {w in food_vecs}, in QUERY: {w in query_vecs}")
