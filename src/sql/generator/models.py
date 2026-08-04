from pydantic import BaseModel, ConfigDict, Field

from src.ingestion.schema_models import TableInfo


class SchemaRelationship(BaseModel):
    source_schema: str
    source_table: str
    source_column: str

    target_schema: str
    target_table: str
    target_column: str

class TableReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_: str = Field(alias="schema")
    table: str

class SchemaContext(BaseModel):
    tables: list[TableInfo] = Field(default_factory=list)

    relationships: list[SchemaRelationship] = Field(default_factory=list)

    primary_tables: list[TableReference] = Field(default_factory=list)


