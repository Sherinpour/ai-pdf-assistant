from app.models.chunk import Chunk
from app.services.embedding_service import create_embedding
from app.services.vector_store import VectorStore


def main():
    # 1. Create test chunks
    chunks = [
        Chunk(
            id="test-1",
            text="Python is a programming language.",
            page=1,
            source="test.pdf",
        ),
        Chunk(
            id="test-2",
            text="FastAPI is a Python web framework.",
            page=2,
            source="test.pdf",
        ),
        Chunk(
            id="test-3",
            text="Machine learning uses data to train models.",
            page=3,
            source="test.pdf",
        ),
    ]

    # 2. Create embeddings
    embeddings = [
        create_embedding(chunk.text)
        for chunk in chunks
    ]

    print("Embeddings created successfully!")

    # 3. Create vector store
    vector_store = VectorStore(
        persist_directory="./test_chroma_db"
    )

    # 4. Store chunks + embeddings
    vector_store.add(
        chunks=chunks,
        embeddings=embeddings,
    )

    print("Chunks added to vector store successfully!")

    # 5. Create embedding for search query
    query = "What is FastAPI?"
    query_embedding = create_embedding(query)

    # 6. Search similar chunks
    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=2,
    )

    print("\nSearch results:")
    print(results)


if __name__ == "__main__":
    main()