import json
import re

with open('food_vectors.js', 'r') as f:
    content = f.read()

# Extract json
food_match = re.search(r'window\.FOOD_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)
query_match = re.search(r'window\.QUERY_VECTORS\s*=\s*(\{.*?\});', content, re.DOTALL)

if food_match:
    food_vecs = json.loads(food_match.group(1))
else:
    food_vecs = {}
if query_match:
    query_vecs = json.loads(query_match.group(1))
else:
    query_vecs = {}

def get_vec(w):
    return food_vecs.get(w) or query_vecs.get(w)

def dot(v1, v2):
    if not v1 or not v2: return 0
    return sum(a*b for a,b in zip(v1, v2))

w1 = "白米"
w2 = "生米"
print(f"w1: {w1}, w2: {w2}")
print(f"Has w1: {w1 in food_vecs or w1 in query_vecs}")
print(f"Has w2: {w2 in food_vecs or w2 in query_vecs}")
print(f"Dot: {dot(get_vec(w1), get_vec(w2))}")

w3 = "米"
w4 = "ご飯"
print(f"Dot 白米・米: {dot(get_vec('白米'), get_vec('米'))}")
print(f"Dot 米・ご飯: {dot(get_vec('米'), get_vec('ご飯'))}")
