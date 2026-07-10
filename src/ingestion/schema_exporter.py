import json
from pathlib import Path
from src.config.paths import SCHEMA_JSON

from src.ingestion.schema_models import TableInfo


class SchemaExporter:
    def __init__(self):
        self.output_path = SCHEMA_JSON

    def export(
        self,
        schema: list[TableInfo],
    ) -> None:
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.output_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                [table.model_dump() for table in schema],
                f,
                indent=2,
            )

        print(f"✅ Schema exported to {self.output_path}")