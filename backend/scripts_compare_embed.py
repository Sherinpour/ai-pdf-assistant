"""Compare raw vs prefixed nomic embeddings and L2 vs cosine."""
from __future__ import annotations

import math

import requests

URL = "http://localhost:11434/api/embed"
MODEL = "nomic-embed-text"


def embed(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        URL,
        json={"model": MODEL, "input": texts, "keep_alive": "60m"},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def l2(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def cosine_distance(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return 1.0 - (dot / (na * nb))


docs = [
    "Drylab Viewer helps cinematographers review footage on set with collaborators.",
    "Annual General Meeting: Drylab's AGM will be held on June 16th at 15:00.",
    "Sales team contacts: Holmsen, Torstein Hansen, and Jostein Aanensen.",
]

queries = [
    "What is Drylab Viewer?",
    "When is the AGM?",
    "What is the capital of France?",
    "Who won the World Cup?",
]

print("=== WITHOUT prefixes ===")
doc_emb = embed(docs)
for q in queries:
    qe = embed([q])[0]
    scores = [
        (cosine_distance(qe, de), l2(qe, de), docs[i][:60])
        for i, de in enumerate(doc_emb)
    ]
    scores.sort()
    print(q)
    for cos_d, l2_d, text in scores:
        print(f"  cos_dist={cos_d:.4f} l2={l2_d:.4f} :: {text}")

print("\n=== WITH nomic prefixes ===")
doc_emb_p = embed([f"search_document: {d}" for d in docs])
for q in queries:
    qe = embed([f"search_query: {q}"])[0]
    scores = [
        (cosine_distance(qe, de), l2(qe, de), docs[i][:60])
        for i, de in enumerate(doc_emb_p)
    ]
    scores.sort()
    print(q)
    for cos_d, l2_d, text in scores:
        print(f"  cos_dist={cos_d:.4f} l2={l2_d:.4f} :: {text}")
