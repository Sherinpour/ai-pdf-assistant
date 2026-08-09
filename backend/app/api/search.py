from fastapi import APIRouter

from app.schemas.search import SearchRequest
from app.services.retrieval_service import retrieve


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post("/")
def search(request: SearchRequest):
    results = retrieve(
        query=request.query,
        top_k=request.top_k,
    )

    return {
        "query": request.query,
        "results": results,
    }