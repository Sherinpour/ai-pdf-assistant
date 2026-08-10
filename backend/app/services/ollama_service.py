import logging
import time

import requests

from app.utils.logging_steps import step

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"
KEEP_ALIVE = "60m"


def chat_with_qwen(prompt: str, *, max_tokens: int = 512) -> str:
    step(
        logger,
        "llm",
        "calling Ollama /api/chat",
        model=MODEL_NAME,
        prompt_chars=len(prompt),
        max_tokens=max_tokens,
        url=OLLAMA_URL,
    )
    started = time.perf_counter()
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "think": False,
            "keep_alive": KEEP_ALIVE,
            "options": {
                "temperature": 0.1,
                "num_predict": max_tokens,
            },
        },
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()
    content = data["message"]["content"]

    eval_duration_ns = data.get("eval_duration") or 0
    load_duration_ns = data.get("load_duration") or 0
    step(
        logger,
        "llm",
        "generation complete",
        duration_s=round(time.perf_counter() - started, 3),
        eval_count=data.get("eval_count"),
        prompt_eval_count=data.get("prompt_eval_count"),
        load_s=round(load_duration_ns / 1e9, 3),
        eval_s=round(eval_duration_ns / 1e9, 3),
        answer_preview=content[:120],
    )
    return content
