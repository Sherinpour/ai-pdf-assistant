from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.qa import router as qa_router

app = FastAPI(title="AI PDF Assistant")

app.include_router(upload_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(qa_router)

@app.get("/")
def root():
    return {"message": "AI PDF Assistant API"}
