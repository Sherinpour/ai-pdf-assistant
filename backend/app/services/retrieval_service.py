import logging
import re
import time

from app.services.embedding_service import create_embedding
from app.services.vector_store import vector_store
from app.utils.logging_steps import step

logger = logging.getLogger(__name__)

# Chroma collection uses hnsw:space=cosine.
# collection.query() returns cosine *distance* (not similarity):
#   0.0 = identical, 1.0 = orthogonal, 2.0 = opposite
# Lower distance => more similar.
MAX_COSINE_DISTANCE = 0.55
RELATIVE_MARGIN = 0.12

META_QUESTION_RE = re.compile(
    r"\b("
    r"about|"
    r"purpose|"
    r"summarize|"
    r"summary|"
    r"overview|"
    r"topic|"
    r"main idea|"
    r"what is this (document|pdf|file|newsletter)"
    r")\b",
    re.IGNORECASE,
)


def _filter_relevant(
    candidates: list[dict],
    *,
    max_distance: float,
    relative_margin: float,
) -> list[dict]:
    if not candidates:
        step(logger, "retrieve", "filter: no candidates")
        return []

    best = min(item["distance"] for item in candidates)
    step(
        logger,
        "retrieve",
        "filter start",
        best_distance=round(best, 6),
        max_distance=max_distance,
        relative_margin=relative_margin,
        candidates=len(candidates),
    )

    if best > max_distance:
        for item in candidates:
            step(
                logger,
                "retrieve",
                "Rejected",
                page=item["page"],
                distance=round(item["distance"], 6),
                reason="best_above_max_distance",
                threshold=max_distance,
                preview=item["text"][:100],
            )
        return []

    kept: list[dict] = []
    seen_texts: set[str] = set()
    limit = min(best + relative_margin, max_distance)
    step(logger, "retrieve", "relative accept limit", limit=round(limit, 6))

    for item in sorted(candidates, key=lambda row: row["distance"]):
        distance = item["distance"]
        preview = item["text"][:100]
        if distance > limit:
            step(
                logger,
                "retrieve",
                "Rejected",
                page=item["page"],
                distance=round(distance, 6),
                reason="above_relative_limit",
                limit=round(limit, 6),
                preview=preview,
            )
            continue

        normalized = " ".join(item["text"].split())
        if normalized in seen_texts:
            step(
                logger,
                "retrieve",
                "Rejected",
                page=item["page"],
                distance=round(distance, 6),
                reason="duplicate",
                preview=preview,
            )
            continue
        seen_texts.add(normalized)

        step(
            logger,
            "retrieve",
            "Accepted",
            page=item["page"],
            source=item["source"],
            distance=round(distance, 6),
            reason="within_limit",
            preview=preview,
        )
        kept.append(item)

    step(logger, "retrieve", "filter done", kept=len(kept))
    return kept


def _front_matter_chunks(limit: int = 3) -> list[dict]:
    """Page-1 excerpts help answer generic 'about/purpose' questions."""
    step(logger, "retrieve", "fetch page-1 front matter", limit=limit)
    try:
        raw = vector_store.collection.get(
            where={"page": 1},
            include=["documents", "metadatas"],
        )
    except Exception as exc:  # pragma: no cover - chroma edge cases
        step(logger, "retrieve", "front matter fetch failed", error=str(exc))
        return []

    ids = raw.get("ids") or []
    documents = raw.get("documents") or []
    metadatas = raw.get("metadatas") or []
    chunks: list[dict] = []

    for chunk_id, document, metadata in zip(ids, documents, metadatas):
        chunks.append(
            {
                "id": chunk_id,
                "text": document,
                "page": metadata.get("page", 1),
                "source": metadata.get("source", "unknown"),
                "distance": 0.4,
            }
        )
        if len(chunks) >= limit:
            break

    step(logger, "retrieve", "front matter ready", added=len(chunks))
    return chunks


def retrieve(
    query: str,
    top_k: int = 5,
    max_distance: float = MAX_COSINE_DISTANCE,
    relative_margin: float = RELATIVE_MARGIN,
) -> list[dict]:
    total_started = time.perf_counter()
    is_meta = bool(META_QUESTION_RE.search(query))
    step(
        logger,
        "retrieve",
        "pipeline start",
        query=query,
        top_k=top_k,
        meta=is_meta,
        metric="cosine",
        max_distance=max_distance,
        relative_margin=relative_margin,
        collection=vector_store.collection.name,
        collection_count=vector_store.collection.count(),
    )

    step(logger, "retrieve", "1/4 embed query with nomic-embed-text")
    embed_started = time.perf_counter()
    query_embedding = create_embedding(query, for_query=True)
    embed_duration = time.perf_counter() - embed_started
    step(
        logger,
        "retrieve",
        "query embedding ready",
        dims=len(query_embedding),
        duration_s=round(embed_duration, 3),
    )

    step(logger, "retrieve", "2/4 chroma vector search")
    search_started = time.perf_counter()
    fetch_k = max(top_k * 2, top_k)
    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=fetch_k,
    )
    search_duration = time.perf_counter() - search_started

    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []
    ids = results["ids"][0] if results["ids"] else []
    step(
        logger,
        "retrieve",
        "vector search raw hits",
        fetch_k=fetch_k,
        raw_hits=len(documents),
        duration_s=round(search_duration, 3),
    )

    candidates: list[dict] = []
    for index, (chunk_id, document, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances),
        start=1,
    ):
        step(
            logger,
            "retrieve",
            "raw hit",
            index=index,
            page=metadata.get("page"),
            source=metadata.get("source"),
            distance=round(float(distance), 6),
            preview=document[:120],
        )
        candidates.append(
            {
                "id": chunk_id,
                "text": document,
                "page": metadata["page"],
                "source": metadata["source"],
                "distance": float(distance),
            }
        )

    step(logger, "retrieve", "3/4 relevance filter")
    effective_margin = relative_margin + (0.05 if is_meta else 0.0)
    retrieved_chunks = _filter_relevant(
        candidates,
        max_distance=max_distance,
        relative_margin=effective_margin,
    )

    if is_meta:
        step(logger, "retrieve", "meta question -> add page-1 front matter")
        seen_ids = {chunk["id"] for chunk in retrieved_chunks}
        scored = [chunk["distance"] for chunk in retrieved_chunks if chunk["distance"] > 0]
        front_distance = min(scored) if scored else 0.4
        for front in _front_matter_chunks(limit=3):
            if front["id"] in seen_ids:
                continue
            front["distance"] = front_distance
            step(
                logger,
                "retrieve",
                "Accepted",
                page=front["page"],
                distance=round(front["distance"], 6),
                reason="front_matter_for_meta_question",
                preview=front["text"][:100],
            )
            retrieved_chunks.insert(0, front)
            seen_ids.add(front["id"])

    retrieved_chunks = retrieved_chunks[:top_k]
    step(
        logger,
        "retrieve",
        "4/4 RETRIEVE SUCCESS",
        kept=len(retrieved_chunks),
        query_embedding_s=round(embed_duration, 3),
        vector_search_s=round(search_duration, 3),
        total_s=round(time.perf_counter() - total_started, 3),
    )
    return retrieved_chunks


def build_context(results: list[dict]) -> str:
    if not results:
        step(logger, "retrieve", "build_context empty")
        return ""

    step(logger, "retrieve", "build_context", chunks=len(results))
    context_parts = []
    for result in results:
        context_parts.append(
            f"""Source: {result["source"]}
Page: {result["page"]}

{result["text"]}"""
        )
    return "\n\n".join(context_parts)
