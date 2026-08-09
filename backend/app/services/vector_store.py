
import chromadb

from app.models.chunk import Chunk


class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name="pdf_chunks"
        )

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must be equal."
            )

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

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )


vector_store = VectorStore()