from fastapi import APIRouter

from app.schemas.qa import QARequest
from app.services.qa_service import answer_question
from app.utils.logging_steps import get_logger, step

logger = get_logger(__name__)

router = APIRouter(
    prefix="/qa",
    tags=["QA"],
)


@router.post("/")
def ask_question(request: QARequest):
    step(logger, "qa.api", "request received", question=request.question, top_k=request.top_k)
    result = answer_question(
        question=request.question,
        top_k=request.top_k,
    )
    step(
        logger,
        "qa.api",
        "response ready",
        found=result.get("found"),
        sources=len(result.get("sources") or []),
    )
    return result
