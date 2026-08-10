from fastapi import APIRouter

from app.schemas.search import SearchRequest
from app.services.retrieval_service import retrieve
from app.utils.logging_steps import get_logger, step

logger = get_logger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post("/")
def search(request: SearchRequest):
    step(logger, "search.api", "request received", query=request.query, top_k=request.top_k)
    results = retrieve(
        query=request.query,
        top_k=request.top_k,
    )
    step(logger, "search.api", "response ready", results=len(results))
    return {
        "query": request.query,
        "results": results,
    }
