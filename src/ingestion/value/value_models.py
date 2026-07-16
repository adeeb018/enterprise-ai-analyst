from typing import Any
from pydantic import BaseModel, Field


class ValueChunk(BaseModel):
    id: str
    schema_name: str
    table: str
    column: str
    text: str
    values: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddedValueChunk(ValueChunk):
    embedding: list[float]