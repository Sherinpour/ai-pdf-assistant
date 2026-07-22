from fastapi import FastAPI

from app.api.upload import router as upload_router

app = FastAPI(title="AI PDF Assistant")

app.include_router(upload_router)


@app.get("/")
def root():
    return {"message": "AI PDF Assistant API"}
