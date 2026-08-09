from app.services.retrieval_service import retrieve, build_context
from app.services.ollama_service import chat_with_qwen


def answer_question(
    question: str,
    top_k: int = 5,
) -> dict:
    # 1. Retrieve relevant chunks
    results = retrieve(
        query=question,
        top_k=top_k,
    )

    # 2. Build context from retrieved chunks
    context = build_context(results)

    # 3. Create prompt
    prompt = f"""
You are an AI assistant that answers questions based only on the provided context.

Rules:
- Answer only using the provided context.
- If the answer is not in the context, say that you don't know.
- Do not make up information.
- Answer clearly and concisely.
- Mention the page number when it is relevant.

Context:
{context}

Question:
{question}

Answer:
"""

    # 4. Generate answer using Qwen
    answer = chat_with_qwen(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": results,
    }