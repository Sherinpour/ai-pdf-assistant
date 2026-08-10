"""Verify retrieval + chat grounding for drylab regression cases."""
from __future__ import annotations

import logging

from app.services.chat_service import chat
from app.services.retrieval_service import MAX_COSINE_DISTANCE, RELATIVE_MARGIN, retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

CASES = [
    "What is this document about?",
    "What is the main purpose of this document?",
    "What is the capital of France?",
    "When is the Annual General Meeting?",
]


def main() -> None:
    print(
        f"threshold max_cosine_distance={MAX_COSINE_DISTANCE} "
        f"relative_margin={RELATIVE_MARGIN}"
    )
    for question in CASES:
        print("\n" + "=" * 72)
        print("QUESTION:", question)
        chunks = retrieve(question, top_k=5)
        print("kept_chunks:", len(chunks))
        for chunk in chunks:
            print(
                f"  page={chunk['page']} distance={chunk['distance']:.4f} "
                f"preview={chunk['text'][:80]!r}"
            )
        result = chat(question, top_k=5)
        print("answer:", result["answer"][:400])
        print("found:", result["found"])
        print("sources:", result["sources"])
        print("timings:", result["timings"])


if __name__ == "__main__":
    main()
