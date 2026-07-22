from uuid import uuid4

from app.models.chunk import Chunk
from app.models.pdf import PDFPage

def chunk_pages(
    pages: list[PDFPage],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:

    chunks = []

    for page in pages:

        text = page.text

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    id=str(uuid4()),
                    page=page.page,
                    text=chunk_text,
                    source=page.source,
                )
            )

            start += chunk_size - overlap

    return chunks