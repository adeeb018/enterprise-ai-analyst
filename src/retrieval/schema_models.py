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


class TableInfo(BaseModel):
    schema_name: str
    table: str

    columns: list[ColumnInfo] = Field(default_factory=list)
    primary_keys: list[str] = Field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = Field(default_factory=list)