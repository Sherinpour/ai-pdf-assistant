from fastapi import APIRouter

from app.schemas.qa import QARequest
from app.services.qa_service import answer_question


router = APIRouter(
    prefix="/qa",
    tags=["QA"],
)


@router.post("/")
def ask_question(request: QARequest):
    return answer_question(
        question=request.question,
        top_k=request.top_k,
    )