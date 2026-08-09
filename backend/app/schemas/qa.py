from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    top_k: int = 5


class QAResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]
