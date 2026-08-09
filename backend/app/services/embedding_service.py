import requests


OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["embedding"]


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    return [
        create_embedding(text)
        for text in texts
    ]