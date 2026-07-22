import os

import fitz

from app.models.pdf import PDFPage

def open_pdf(file_path: str) -> fitz.Document:
    """
    Open a PDF document.

    Raises:
        FileNotFoundError
        RuntimeError
    """

    try:
        return fitz.open(file_path)

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF not found: {file_path}")

    except Exception as e:
        raise RuntimeError(f"Unable to open PDF: {e}")

def get_pages(document: fitz.Document):
    for page_number in range(len(document)):
        yield page_number, document.load_page(page_number)

def extract_page_text(page: fitz.Page) -> str:
    return page.get_text("text").strip()

def extract_pages(document: fitz.Document, source: str) -> list[PDFPage]:

    pages = []

    for page_number, page in get_pages(document):

        text = extract_page_text(page)

        pages.append(
            PDFPage(
                page=page_number + 1,
                text=text,
                source=source,
            )
        )

    return pages

def extract_pdf(file_path: str) -> list[PDFPage]:

    document = open_pdf(file_path)

    pages = extract_pages(
        document=document,
        source=os.path.basename(file_path),
    )

    document.close()

    return pages