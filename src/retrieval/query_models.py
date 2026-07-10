from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    score: float
    schema_name: str
    table: str
    text: str
    keywords: list[str]