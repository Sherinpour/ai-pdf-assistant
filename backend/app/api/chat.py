from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services.chat_service import chat


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/")
def chat_with_pdf(request: ChatRequest):
    return chat(
        question=request.question,
        top_k=request.top_k,
    )