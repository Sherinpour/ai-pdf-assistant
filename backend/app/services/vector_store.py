import logging
import time

import chromadb

from app.models.chunk import Chunk
from app.utils.logging_steps import step

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        step(logger, "chroma", "init PersistentClient", path=persist_directory)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="pdf_chunks_v2",
            metadata={"hnsw:space": "cosine"},
        )
        step(
            logger,
            "chroma",
            "collection ready",
            name=self.collection.name,
            metric="cosine",
            count=self.collection.count(),
        )

    def delete_by_source(self, source: str) -> int:
        step(logger, "chroma", "delete_by_source lookup", source=source)
        existing = self.collection.get(where={"source": source})
        ids = existing.get("ids") or []
        if ids:
            self.collection.delete(ids=ids)
            step(logger, "chroma", "chunks deleted", source=source, count=len(ids))
        else:
            step(logger, "chroma", "no chunks to delete", source=source)
        return len(ids)

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must be equal.")

        if not chunks:
            step(logger, "chroma", "add skipped empty")
            return

        step(logger, "chroma", "adding vectors", count=len(chunks))
        started = time.perf_counter()
        self.collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "page": chunk.page,
                    "source": chunk.source,
                }
                for chunk in chunks
            ],
        )
        step(
            logger,
            "chroma",
            "add complete",
            count=len(chunks),
            collection_count=self.collection.count(),
            duration_s=round(time.perf_counter() - started, 3),
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ):
        count = self.collection.count()
        step(logger, "chroma", "query start", top_k=top_k, collection_count=count)
        started = time.perf_counter()
        if count == 0:
            step(logger, "chroma", "query skipped empty collection")
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        n_results = min(top_k, count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        hits = len(results["ids"][0]) if results.get("ids") else 0
        step(
            logger,
            "chroma",
            "query complete",
            n_results=n_results,
            hits=hits,
            duration_s=round(time.perf_counter() - started, 3),
        )
        return results


vector_store = VectorStore()
