from pydantic import BaseModel


class PDFPage(BaseModel):
    page: int
    text: str
    source: str