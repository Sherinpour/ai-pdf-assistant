import logging
import time
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.chunk_service import chunk_pages
from app.services.embedding_service import generate_embeddings
from app.services.pdf_service import extract_pdf
from app.services.vector_store import vector_store
from app.utils.logging_steps import step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    total_started = time.perf_counter()
    step(logger, "upload", "request received", filename=file.filename)

    if not file.filename:
        step(logger, "upload", "reject missing filename")
        raise HTTPException(status_code=400, detail="Filename is required.")

    filename = Path(file.filename).name
    if not filename.lower().endswith(".pdf"):
        step(logger, "upload", "reject non-pdf", filename=filename)
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    step(logger, "upload", "reading file bytes", filename=filename)
    content = await file.read()
    if not content:
        step(logger, "upload", "reject empty file", filename=filename)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if not content.startswith(b"%PDF"):
        step(logger, "upload", "reject invalid pdf magic bytes", filename=filename)
        raise HTTPException(status_code=400, detail="File content is not a valid PDF.")

    file_path = UPLOAD_DIR / filename
    step(logger, "upload", "saving file to disk", path=str(file_path), bytes=len(content))
    file_path.write_bytes(content)

    try:
        step(logger, "upload", "extracting text with PyMuPDF", filename=filename)
        extract_started = time.perf_counter()
        pages = extract_pdf(str(file_path))
        extract_duration = time.perf_counter() - extract_started
        step(
            logger,
            "upload",
            "text extraction complete",
            pages=len(pages),
            duration_s=round(extract_duration, 3),
        )
    except (FileNotFoundError, RuntimeError) as exc:
        file_path.unlink(missing_ok=True)
        step(logger, "upload", "extraction failed, file removed", error=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    step(logger, "upload", "chunking pages", chunk_size=500, overlap=50)
    chunk_started = time.perf_counter()
    chunks = chunk_pages(pages)
    chunk_duration = time.perf_counter() - chunk_started
    step(
        logger,
        "upload",
        "chunking complete",
        chunks=len(chunks),
        duration_s=round(chunk_duration, 3),
    )

    step(logger, "upload", "removing previous index for same filename", filename=filename)
    deleted = vector_store.delete_by_source(filename)
    step(logger, "upload", "old chunks removed", deleted_chunks=deleted)

    texts = [chunk.text for chunk in chunks]
    step(logger, "upload", "embedding chunks via Ollama nomic-embed-text", chunks=len(texts))
    embed_started = time.perf_counter()
    embeddings = generate_embeddings(texts)
    embed_duration = time.perf_counter() - embed_started
    step(
        logger,
        "upload",
        "embeddings ready",
        embeddings=len(embeddings),
        duration_s=round(embed_duration, 3),
    )

    step(logger, "upload", "storing vectors in ChromaDB", collection="pdf_chunks_v2")
    store_started = time.perf_counter()
    vector_store.add(chunks, embeddings)
    store_duration = time.perf_counter() - store_started
    step(
        logger,
        "upload",
        "chroma store complete",
        collection_count=vector_store.collection.count(),
        duration_s=round(store_duration, 3),
    )

    total_duration = time.perf_counter() - total_started
    step(
        logger,
        "upload",
        "UPLOAD SUCCESS",
        filename=filename,
        pages=len(pages),
        chunks=len(chunks),
        total_s=round(total_duration, 3),
    )

    return {
        "filename": filename,
        "status": "uploaded",
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "replaced_chunks": deleted,
        "timings": {
            "extract_s": round(extract_duration, 3),
            "chunk_s": round(chunk_duration, 3),
            "embed_s": round(embed_duration, 3),
            "store_s": round(store_duration, 3),
            "total_s": round(total_duration, 3),
        },
    }


@router.delete("/{filename}")
async def delete_pdf(filename: str):
    safe_name = Path(filename).name
    step(logger, "delete", "request received", filename=safe_name)

    if not safe_name.lower().endswith(".pdf"):
        step(logger, "delete", "reject non-pdf filename", filename=safe_name)
        raise HTTPException(status_code=400, detail="Only PDF filenames are allowed.")

    step(logger, "delete", "removing chroma chunks by source", filename=safe_name)
    deleted_chunks = vector_store.delete_by_source(safe_name)

    file_path = UPLOAD_DIR / safe_name
    file_existed = file_path.exists()
    if file_existed:
        step(logger, "delete", "removing file from disk", path=str(file_path))
        file_path.unlink(missing_ok=True)
    else:
        step(logger, "delete", "no file on disk", path=str(file_path))

    if deleted_chunks == 0 and not file_existed:
        step(logger, "delete", "not found", filename=safe_name)
        raise HTTPException(status_code=404, detail="PDF not found.")

    step(
        logger,
        "delete",
        "DELETE SUCCESS",
        filename=safe_name,
        deleted_chunks=deleted_chunks,
        file_removed=file_existed,
        collection_count=vector_store.collection.count(),
    )

    return {
        "filename": safe_name,
        "status": "deleted",
        "deleted_chunks": deleted_chunks,
        "file_removed": file_existed,
    }
