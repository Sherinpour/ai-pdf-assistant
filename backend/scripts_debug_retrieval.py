"""Debug retrieval distances for drylab regression investigation."""
from __future__ import annotations

import logging

from app.services.embedding_service import create_embedding
from app.services.retrieval_service import MAX_COSINE_DISTANCE, retrieve
from app.services.vector_store import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


def inspect(query: str, top_k: int = 5) -> None:
    print("=" * 72)
    print(f"Query: {query}")
    print(f"collection={vector_store.collection.name} count={vector_store.collection.count()}")
    print(f"metadata={vector_store.collection.metadata}")
    print(f"threshold={MAX_COSINE_DISTANCE} (reject if distance > threshold)")

    emb = create_embedding(query, for_query=True)
    raw = vector_store.search(emb, top_k=top_k)
    docs = raw["documents"][0] if raw["documents"] else []
    metas = raw["metadatas"][0] if raw["metadatas"] else []
    dists = raw["distances"][0] if raw["distances"] else []

    if not docs:
        print("No raw hits from Chroma.")
        return

    for i, (distance, meta, doc) in enumerate(zip(dists, metas, docs), start=1):
        decision = "Accepted" if distance <= MAX_COSINE_DISTANCE else "Rejected"
        print(f"\nRetrieved chunk {i}:")
        print(f"  page: {meta.get('page')}")
        print(f"  source: {meta.get('source')}")
        print(f"  distance: {distance:.6f}")
        print(f"  text preview: {doc[:120]!r}")
        print(f"  {decision}")
        print(f"  Reason: threshold={MAX_COSINE_DISTANCE} actual_distance={distance:.6f}")

    kept = retrieve(query, top_k=top_k)
    print(f"\nAfter filter/dedupe kept={len(kept)}")


def main() -> None:
    for q in [
        "What is this document about?",
        "What is the main purpose of this document?",
        "What is the capital of France?",
        "What is Drylab Viewer?",
        "When is the Annual General Meeting?",
    ]:
        inspect(q)


if __name__ == "__main__":
    main()
