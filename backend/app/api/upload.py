from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.chunk_service import chunk_pages
from app.services.pdf_service import extract_pdf
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import vector_store

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    filename = Path(file.filename).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File content is not a valid PDF.")

    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)

    try:
        pages = extract_pdf(str(file_path))
    except (FileNotFoundError, RuntimeError) as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = chunk_pages(pages)

    texts = [chunk.text for chunk in chunks]

    embeddings = generate_embeddings(texts)

    vector_store.add(chunks, embeddings)

    return {
        "filename": filename,
        "status": "uploaded",
        "page_count": len(pages),
        "chunk_count": len(chunks),
    }
