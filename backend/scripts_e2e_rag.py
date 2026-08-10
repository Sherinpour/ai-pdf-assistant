"""End-to-end checks for upload + grounded chat behavior."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from app.services.chat_service import chat
from app.services.chunk_service import chunk_pages
from app.services.embedding_service import generate_embeddings
from app.services.pdf_service import extract_pdf
from app.services.vector_store import vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def reindex(pdf_path: Path) -> None:
    started = time.perf_counter()
    pages = extract_pdf(str(pdf_path))
    chunks = chunk_pages(pages)
    deleted = vector_store.delete_by_source(pdf_path.name)
    embeddings = generate_embeddings([c.text for c in chunks])
    vector_store.add(chunks, embeddings)
    print(
        f"reindex {pdf_path.name}: pages={len(pages)} chunks={len(chunks)} "
        f"deleted_old={deleted} duration={time.perf_counter() - started:.3f}s "
        f"collection={vector_store.collection.count()}"
    )


def main() -> None:
    pdf_path = Path("uploads/drylab.pdf")
    if not pdf_path.exists():
        raise SystemExit(f"Missing {pdf_path}")

    reindex(pdf_path)

    print("\n=== TEST: in-document question ===")
    in_doc = chat("What is Drylab Viewer?", top_k=3)
    print("answer:", in_doc["answer"][:400])
    print("found:", in_doc["found"])
    print("sources:", in_doc["sources"])
    print("timings:", in_doc["timings"])

    print("\n=== TEST: out-of-document question ===")
    out_doc = chat("What is the capital of France?", top_k=3)
    print("answer:", out_doc["answer"])
    print("found:", out_doc["found"])
    print("sources:", out_doc["sources"])
    print("timings:", out_doc["timings"])

    print("\n=== TEST: consecutive question (should not re-embed PDF) ===")
    second = chat("When is the Annual General Meeting?", top_k=3)
    print("answer:", second["answer"][:400])
    print("found:", second["found"])
    print("sources:", second["sources"])
    print("timings:", second["timings"])


if __name__ == "__main__":
    main()
