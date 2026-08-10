import logging
import time

from app.services.ollama_service import chat_with_qwen
from app.services.retrieval_service import build_context, retrieve
from app.utils.logging_steps import step

logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = (
    "I couldn't find this information in the uploaded document."
)


def chat(
    question: str,
    top_k: int = 5,
    history: list[dict] | None = None,
) -> dict:
    total_started = time.perf_counter()
    step(
        logger,
        "chat",
        "pipeline start",
        question=question,
        top_k=top_k,
        history_len=len(history or []),
    )

    if history is None:
        history = []

    # Keep prompt small: only the most recent turns matter for references.
    recent_history = history[-6:]
    step(logger, "chat", "using recent history turns", turns=len(recent_history))

    step(logger, "chat", "1/5 retrieve relevant chunks")
    retrieve_started = time.perf_counter()
    results = retrieve(query=question, top_k=top_k)
    retrieve_duration = time.perf_counter() - retrieve_started
    step(
        logger,
        "chat",
        "retrieve finished",
        chunks=len(results),
        duration_s=round(retrieve_duration, 3),
    )

    if not results:
        total_s = round(time.perf_counter() - total_started, 3)
        step(
            logger,
            "chat",
            "no relevant chunks -> skip LLM, return not-found",
            total_s=total_s,
        )
        return {
            "answer": NOT_FOUND_MESSAGE,
            "sources": [],
            "found": False,
            "timings": {
                "retrieve_s": round(retrieve_duration, 3),
                "prompt_s": 0.0,
                "llm_s": 0.0,
                "total_s": total_s,
            },
        }

    for index, result in enumerate(results, start=1):
        step(
            logger,
            "chat",
            "context chunk",
            index=index,
            source=result["source"],
            page=result["page"],
            distance=round(result["distance"], 4),
            preview=result["text"][:80],
        )

    step(logger, "chat", "2/5 build prompt from context + history")
    prompt_started = time.perf_counter()
    context = build_context(results)
    history_text = "\n".join(
        f'{message["role"]}: {message["content"]}'
        for message in recent_history
    )

    prompt = f"""You are a document Q&A assistant.

Use ONLY the PDF context below. Never use outside knowledge.

Conversation history (for pronouns/references only):
{history_text or "(none)"}

PDF context:
{context}

Question:
{question}

Rules:
1. If the question asks what the document is about, its topic, overview, or main purpose, summarize the kind of document and what it covers using the PDF context (for example: a company newsletter, product update, meeting notes).
2. Answer only when the PDF context supports the answer.
3. If the PDF context does not contain enough information for this question, reply exactly:
{NOT_FOUND_MESSAGE}
4. Do not guess and do not use general world knowledge (for example city capitals, sports results, or facts not present in the context).
5. Be concise.
6. Answer in the same language as the question.
"""
    prompt_duration = time.perf_counter() - prompt_started
    step(
        logger,
        "chat",
        "prompt ready",
        prompt_chars=len(prompt),
        context_chars=len(context),
        duration_s=round(prompt_duration, 3),
    )

    step(logger, "chat", "3/5 call Ollama LLM qwen3:8b")
    llm_started = time.perf_counter()
    answer = chat_with_qwen(prompt).strip()
    llm_duration = time.perf_counter() - llm_started
    step(
        logger,
        "chat",
        "LLM response received",
        answer_chars=len(answer),
        answer_preview=answer[:120],
        duration_s=round(llm_duration, 3),
    )

    step(logger, "chat", "4/5 check grounding / sources")
    grounded = NOT_FOUND_MESSAGE.lower() not in answer.lower()
    sources: list[dict] = []
    if grounded:
        unique_sources: dict[tuple, dict] = {}
        for result in results:
            key = (result["source"], result["page"])
            if key not in unique_sources:
                unique_sources[key] = {
                    "page": result["page"],
                    "source": result["source"],
                    "distance": result["distance"],
                }
        sources = list(unique_sources.values())
        step(logger, "chat", "answer grounded -> attach sources", sources=sources)
    else:
        answer = NOT_FOUND_MESSAGE
        step(logger, "chat", "answer not grounded -> clear sources")

    total_duration = time.perf_counter() - total_started
    step(
        logger,
        "chat",
        "5/5 CHAT SUCCESS",
        found=grounded,
        sources=len(sources),
        retrieve_s=round(retrieve_duration, 3),
        prompt_s=round(prompt_duration, 3),
        llm_s=round(llm_duration, 3),
        total_s=round(total_duration, 3),
    )

    return {
        "answer": answer,
        "sources": sources,
        "found": grounded,
        "timings": {
            "retrieve_s": round(retrieve_duration, 3),
            "prompt_s": round(prompt_duration, 3),
            "llm_s": round(llm_duration, 3),
            "total_s": round(total_duration, 3),
        },
    }
