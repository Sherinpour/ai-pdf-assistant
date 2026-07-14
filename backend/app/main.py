from fastapi import FastAPI

app = FastAPI(title="AI PDF Assistant")


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "AI PDF Assistant API is running"
    }