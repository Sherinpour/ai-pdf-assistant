import logging
import time

import requests

from app.utils.logging_steps import step

logger = logging.getLogger(__name__)

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text"
KEEP_ALIVE = "60m"

QUERY_PREFIX = "search_query: "
DOCUMENT_PREFIX = "search_document: "


def _embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        step(logger, "embed", "skip empty batch")
        return []

    step(
        logger,
        "embed",
        "calling Ollama /api/embed",
        model=EMBEDDING_MODEL,
        count=len(texts),
        url=OLLAMA_EMBED_URL,
    )
    started = time.perf_counter()
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": texts,
            "keep_alive": KEEP_ALIVE,
        },
        timeout=300,
    )
    response.raise_for_status()
    embeddings = response.json()["embeddings"]
    step(
        logger,
        "embed",
        "batch complete",
        count=len(texts),
        dims=len(embeddings[0]) if embeddings else 0,
        duration_s=round(time.perf_counter() - started, 3),
    )
    return embeddings


def create_embedding(text: str, *, for_query: bool = True) -> list[float]:
    prefix = QUERY_PREFIX if for_query else DOCUMENT_PREFIX
    kind = "query" if for_query else "document"
    step(logger, "embed", f"single {kind} embedding", prefix=prefix.strip(), chars=len(text))
    return _embed_batch([f"{prefix}{text}"])[0]


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed document chunks in one batched Ollama request."""
    step(logger, "embed", "document batch embedding", chunks=len(texts), prefix=DOCUMENT_PREFIX.strip())
    prefixed = [f"{DOCUMENT_PREFIX}{text}" for text in texts]
    return _embed_batch(prefixed)
