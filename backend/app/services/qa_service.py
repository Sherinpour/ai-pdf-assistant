import logging
import time

from app.services.chat_service import NOT_FOUND_MESSAGE
from app.services.ollama_service import chat_with_qwen
from app.services.retrieval_service import build_context, retrieve
from app.utils.logging_steps import step

logger = logging.getLogger(__name__)


def answer_question(
    question: str,
    top_k: int = 5,
) -> dict:
    total_started = time.perf_counter()
    step(logger, "qa", "pipeline start", question=question, top_k=top_k)

    step(logger, "qa", "1/3 retrieve")
    results = retrieve(query=question, top_k=top_k)
    if not results:
        step(logger, "qa", "no chunks -> not-found")
        return {
            "question": question,
            "answer": NOT_FOUND_MESSAGE,
            "sources": [],
            "found": False,
        }

    step(logger, "qa", "2/3 build prompt + call LLM", chunks=len(results))
    context = build_context(results)
    prompt = f"""You are a document Q&A assistant.

Answer ONLY using the PDF context below. Never use outside knowledge.

PDF context:
{context}

Question:
{question}

Rules:
1. If the PDF context does not explicitly support the answer, reply exactly:
{NOT_FOUND_MESSAGE}
2. Do not guess. Do not use general knowledge.
3. Be concise.
"""

    answer = chat_with_qwen(prompt).strip()
    grounded = NOT_FOUND_MESSAGE.lower() not in answer.lower()
    sources = results if grounded else []
    if not grounded:
        answer = NOT_FOUND_MESSAGE

    step(
        logger,
        "qa",
        "3/3 QA SUCCESS",
        found=grounded,
        sources=len(sources),
        total_s=round(time.perf_counter() - total_started, 3),
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "found": grounded,
    }
