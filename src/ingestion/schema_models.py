from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool


class ForeignKeyInfo(BaseModel):
    column: str
    referred_schema: str | None = None
    referred_table: str | None = None
    referred_column: str | None = None


class EnrichmentInfo(BaseModel):
    description: str
    keywords: list[str]


class TableInfo(BaseModel):
    schema_name: str
    table: str

    description: str | None = None
    keywords: list[str] = Field(default_factory=list)

    columns: list[ColumnInfo] = Field(default_factory=list)
    primary_keys: list[str] = Field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = Field(default_factory=list)

    description_embedding: list[float] | None = None


class Chunk(BaseModel):
    id: str
    schema_name: str
    table: str
    text: str
    metadata: dict


class EmbeddedChunk(Chunk):
    embedding: list[float]