"""One-off timing/distance diagnostics for the RAG pipeline."""
from __future__ import annotations

import time

import requests

from app.services.embedding_service import create_embedding
from app.services.ollama_service import chat_with_qwen
from app.services.retrieval_service import build_context, retrieve
from app.services.vector_store import vector_store


def timed(label: str, fn):
    t0 = time.perf_counter()
    out = fn()
    dt = time.perf_counter() - t0
    print(f"{label}: {dt:.3f}s")
    return out, dt


def main() -> None:
    print("collection_count", vector_store.collection.count())
    print("collection_metadata", vector_store.collection.metadata)

    requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": "warmup", "keep_alive": "60m"},
        timeout=120,
    )
    requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen3:8b",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False,
            "think": False,
            "keep_alive": "60m",
            "options": {"num_predict": 8},
        },
        timeout=300,
    )

    print("\n--- distances ---")
    for q in [
        "What is this document about?",
        "What is the capital of France?",
        "dry lab experiment results",
    ]:
        emb, _ = timed(f"embed[{q[:40]}]", lambda query=q: create_embedding(query))
        res = vector_store.search(emb, top_k=5)
        dists = res["distances"][0]
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        print(f"QUERY: {q}")
        for distance, meta, doc in zip(dists, metas, docs):
            print(
                f"  dist={distance:.4f} page={meta.get('page')} "
                f"source={meta.get('source')} text={doc[:90]!r}"
            )
        print()

    print("--- full chat pipeline timing (in-doc) ---")
    q = "What is this document about?"
    t_total0 = time.perf_counter()
    t0 = time.perf_counter()
    emb = create_embedding(q)
    print(f"query_embedding: {time.perf_counter() - t0:.3f}s")
    t0 = time.perf_counter()
    vector_store.search(emb, top_k=5)
    print(f"vector_search: {time.perf_counter() - t0:.3f}s")
    chunks, _ = timed("retrieve_total", lambda: retrieve(q, top_k=5))
    ctx, _ = timed("build_context", lambda: build_context(chunks))
    prompt = f"""You are a helpful assistant for answering questions about a PDF document.
Use ONLY the information provided in the context below.
Context:
{ctx}
Current question:
{q}
Instructions:
- Answer directly and concisely.
- If the context does not contain enough information, say you could not find it.
"""
    print("prompt_chars", len(prompt), "chunks", len(chunks))
    ans, _ = timed("llm_generation", lambda: chat_with_qwen(prompt))
    print("answer:", ans[:500])
    print("TOTAL", round(time.perf_counter() - t_total0, 3))

    print("\n--- irrelevant ---")
    q2 = "What is the capital of France?"
    chunks2, _ = timed("retrieve_irr", lambda: retrieve(q2, top_k=5))
    print("top distances", [round(c["distance"], 4) for c in chunks2])
    print(
        "sources",
        [(c["source"], c["page"], round(c["distance"], 4)) for c in chunks2],
    )


if __name__ == "__main__":
    main()
