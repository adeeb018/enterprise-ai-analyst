import json
from pathlib import Path

from src.retrieval.schema_models import TableInfo


class SchemaExporter:
    def __init__(self, output_path: str = "data/schema/schema.json"):
        self.output_path = Path(output_path)

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