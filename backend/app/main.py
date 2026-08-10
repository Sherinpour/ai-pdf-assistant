import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.qa import router as qa_router
from app.utils.logging_steps import step

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger("app.main")

app = FastAPI(title="AI PDF Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    step(
        logger,
        "http",
        "request received",
        method=request.method,
        path=request.url.path,
    )
    response = await call_next(request)
    step(
        logger,
        "http",
        "response sent",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )
    return response


app.include_router(upload_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(qa_router)

step(logger, "startup", "AI PDF Assistant API ready")


@app.get("/")
def root():
    step(logger, "http", "health check")
    return {"message": "AI PDF Assistant API"}
