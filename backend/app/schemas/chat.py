from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5
    history: list[ChatMessage] = Field(default_factory=list)