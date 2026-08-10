from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services.chat_service import chat
from app.utils.logging_steps import get_logger, step

logger = get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/")
def chat_with_pdf(request: ChatRequest):
    step(
        logger,
        "chat.api",
        "request received",
        question=request.question,
        top_k=request.top_k,
        history_len=len(request.history),
    )
    result = chat(
        question=request.question,
        top_k=request.top_k,
        history=[
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.history
        ],
    )
    step(
        logger,
        "chat.api",
        "response ready",
        found=result.get("found"),
        sources=len(result.get("sources") or []),
        timings=result.get("timings"),
    )
    return result
