from app.services.embedding_service import create_embedding
from app.services.vector_store import vector_store


def retrieve(
    query: str,
    top_k: int = 5,
):
    query_embedding = create_embedding(query)

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
    )

    retrieved_chunks = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        retrieved_chunks.append(
            {
                "id": chunk_id,
                "text": document,
                "page": metadata["page"],
                "source": metadata["source"],
                "distance": distance,
            }
        )

    return retrieved_chunks


def build_context(results: list[dict]) -> str:
    context_parts = []

    for result in results:
        context_parts.append(
            f"""
Source: {result["source"]}
Page: {result["page"]}

{result["text"]}
"""
        )

    return "\n\n".join(context_parts)