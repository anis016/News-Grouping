import math

# https://en.wikipedia.org/wiki/Jaccard_index
def jaccard_similarity(A, B):
    intersection = set(A).intersection(set(B))
    union        = set(A).union(set(B))
    return len(intersection)/len(union)

# https://en.wikipedia.org/wiki/Cosine_similarity
def cosine_similarity(A, B):
    dot_product = sum(p*q for p, q in zip(A, B))
    magnitude   = math.sqrt(sum([value**2 for value in A])) * math.sqrt(sum([value**2 for value in B]))
    if not magnitude:
        return 0
    return dot_product / magnitude
