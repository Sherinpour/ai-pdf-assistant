from app.services.ollama_service import chat_with_qwen
from app.services.retrieval_service import build_context, retrieve


def chat(
    question: str,
    top_k: int = 5,
    history: list[dict] | None = None,
) -> dict:

    if history is None:
        history = []

    results = retrieve(
        query=question,
        top_k=top_k,
    )

    context = build_context(results)

    history_text = "\n".join(
        f'{message["role"]}: {message["content"]}'
        for message in history
    )

    prompt = f"""
You are a helpful assistant for answering questions about a PDF document.

Use ONLY the information provided in the context below.

Conversation history:
{history_text}

Context:
{context}

Current question:
{question}

Instructions:

- Answer the current question directly and concisely.
- Use the conversation history only to understand references such as "it", "they", "where", or "when".
- Use only information explicitly supported by the PDF context.
- Do not add unrelated information from the context.
- Do not make assumptions or use outside knowledge.
- If the context does not contain enough information to answer the question, say:
  "The provided context does not contain enough information to answer this question."
- Answer in the same language as the current question.
"""

    answer = chat_with_qwen(prompt)

    unique_sources = {}

    for result in results:
        key = (
            result["source"],
            result["page"],
        )

        if key not in unique_sources:
            unique_sources[key] = {
                "page": result["page"],
                "source": result["source"],
                "distance": result["distance"],
            }

    return {
        "answer": answer,
        "sources": list(unique_sources.values()),
    }