from pydantic import BaseModel, Field


class SchemaColumn(BaseModel):
    name: str

    description: str | None = None

    is_primary_key: bool = False

    is_foreign_key: bool = False


class SchemaTable(BaseModel):
    schema: str

    name: str

    description: str | None = None

    columns: list[SchemaColumn] = Field(default_factory=list)

class SchemaRelationship(BaseModel):
    source_schema: str
    source_table: str
    source_column: str

    target_schema: str
    target_table: str
    target_column: str

class TableReference(BaseModel):
    schema: str
    table: str

class SchemaContext(BaseModel):
    tables: list[SchemaTable] = Field(default_factory=list)

    relationships: list[SchemaRelationship] = Field(default_factory=list)

    primary_tables: list[TableReference] = Field(default_factory=list)


