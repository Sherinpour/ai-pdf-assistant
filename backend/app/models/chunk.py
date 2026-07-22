from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    page: int
    text: str
    source: str