import json
from pathlib import Path

from pydantic import ValidationError

from src.embedding.embedding_service import EmbeddingService
from src.llm.llm_client import CloudLLMClient
from src.llm.prompts import SCHEMA_DESCRIPTION_PROMPT
from src.ingestion.schema_models import (
    EnrichmentInfo,
)
from tqdm import tqdm
from src.config.paths import (
    SCHEMA_JSON,
    ENRICHED_SCHEMA_JSON,
)


class SchemaEnricher:

    def __init__(
        self,
    ):

        self.input_path = SCHEMA_JSON
        self.output_path = ENRICHED_SCHEMA_JSON

        self.llm = CloudLLMClient()
        self.embedding_service = EmbeddingService()

    def enrich(self):

        with open(
            self.input_path,
            "r",
            encoding="utf-8",
        ) as f:
            schema = json.load(f)

        enriched = []

        for table in tqdm(schema, desc="Enriching tables"):

            print(f"Enriching {table['table']}...")
            table_text = self._build_table_context(
                table
            )
            prompt = SCHEMA_DESCRIPTION_PROMPT.format(
                table_text=table_text
            )
            response = self.llm.generate(prompt)

            try:
                enrichment = EnrichmentInfo.model_validate_json(
                    response
                )

            except ValidationError:
                print(
                    f"❌ Invalid JSON returned for {table['table']}"
                )
                print(response)
                continue

            table["description"] = enrichment.description
            table["keywords"] = enrichment.keywords

            if enrichment.description:
                table["description_embedding"] = self.embedding_service.embed_batch(
                    [enrichment.description]
                )[0]
            else:
                table["description_embedding"] = None

            enriched.append(table)

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
                enriched,
                f,
                indent=2,
            )

        print(
            f"\nSaved to {self.output_path}"
        )

    def _build_table_context(
        self,
        table: dict,
    ) -> str:

        lines = []

        lines.append(f"Schema: {table['schema_name']}")
        lines.append(f"Table: {table['table']}")

        lines.append("\nColumns:")

        for column in table["columns"]:
            lines.append(
                f"- {column['name']}"
            )

        if table["primary_keys"]:

            lines.append("\nPrimary Keys:")

            for pk in table["primary_keys"]:
                lines.append(f"- {pk}")

        if table["foreign_keys"]:

            lines.append("\nRelationships:")

            for fk in table["foreign_keys"]:

                lines.append(
                    f"- {fk['column']} → "
                    f"{fk['referred_table']}.{fk['referred_column']}"
                )

        return "\n".join(lines)