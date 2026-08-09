from app.services.ollama_service import chat_with_qwen


answer = chat_with_qwen(
    "Explain what RAG is in one short paragraph."
)

print(answer)