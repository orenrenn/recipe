import json
import re

with open('food_vectors.js', 'r') as f:
    content = f.read()

food_match = re.search(r'window\.FOOD_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)
query_match = re.search(r'window\.QUERY_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)

food_vecs = json.loads(food_match.group(1)) if food_match else {}
query_vecs = json.loads(query_match.group(1)) if query_match else {}

def get_vec(w): return food_vecs.get(w) or query_vecs.get(w)
def dot(v1, v2):
    if not v1 or not v2: return 0
    return sum(a*b for a,b in zip(v1, v2))

print(f"にんにく vs ニンニク: {dot(get_vec('にんにく'), get_vec('ニンニク'))}")
print(f"オクラ vs 長芋: {dot(get_vec('オクラ'), get_vec('長芋'))}")
