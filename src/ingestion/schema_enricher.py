import json
from pathlib import Path

from pydantic import ValidationError

from src.llm.ollama_client import OllamaClient
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

        self.llm = OllamaClient()

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
            prompt = SCHEMA_DESCRIPTION_PROMPT.format(
                table_text=json.dumps(
                    table,
                    indent=2,
                )
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