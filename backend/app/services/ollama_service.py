import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"


def chat_with_qwen(prompt: str) -> str:
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
            "options": {
                "temperature": 0.2,
            },
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]