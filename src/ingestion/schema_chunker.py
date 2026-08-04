import json
from pathlib import Path

from src.ingestion.schema_models import Chunk, TableInfo
from src.config.paths import ENRICHED_SCHEMA_JSON


class SchemaChunker:
    def __init__(
        self,
    ):
        self.schema_path = Path(ENRICHED_SCHEMA_JSON)

    def load_schema(self) -> list[TableInfo]:
        with open(
            self.schema_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        return [TableInfo.model_validate(table) for table in data]

    def create_chunks(self) -> list[Chunk]:

        schema = self.load_schema()

        chunks = []

        for table in schema:

            lines = []

            lines.append(f"Schema: {table.schema_name}")
            lines.append(f"Table: {table.table}")

            if table.description:
                lines.append("\nDescription:")
                lines.append(table.description)

            if table.keywords:
                lines.append("\nKeywords:")
                for keyword in table.keywords:
                    lines.append(f"- {keyword}")

            lines.append("\nColumns:")
            for column in table.columns:
                lines.append(
                    f"- {column.name} ({column.data_type})"
                )

            if table.primary_keys:
                lines.append("\nPrimary Keys:")
                for pk in table.primary_keys:
                    lines.append(f"- {pk}")

            if table.foreign_keys:
                lines.append("\nForeign Keys:")
                for fk in table.foreign_keys:
                    lines.append(
                        f"- {fk.column} -> "
                        f"{fk.referred_table}.{fk.referred_column}"
                    )

            chunks.append(
                Chunk(
                    id=f"{table.schema_name}.{table.table}",
                    schema_name=table.schema_name,
                    table=table.table,
                    text="\n".join(lines),
                    metadata={
                        "schema": table.schema_name,
                        "table": table.table,
                        "keywords": table.keywords,
                    },
                )
            )

        return chunks