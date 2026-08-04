import json
from pathlib import Path

from src.config.paths import (
    ENRICHED_SCHEMA_JSON,
    GRAPH_JSON,
    SCHEMA_JSON,
)
from src.ingestion.graph_processor import GraphProcessor
from src.ingestion.schema_chunker import SchemaChunker
from src.ingestion.schema_embedder import SchemaEmbedder
from src.ingestion.schema_enricher import SchemaEnricher
from src.ingestion.schema_exporter import SchemaExporter
from src.ingestion.schema_extractor import SchemaExtractor
from src.ingestion.schema_models import TableInfo
from src.ingestion.value.value_extractor import ValueExtractor
from src.ingestion.vector_store import VectorStore
from src.ingestion.value.value_pipeline import ValuePipeline


class IngestionPipeline:

    enriched_schema = None

    def run(self):

        if not SCHEMA_JSON.exists():

            print("Extracting schema...")

            schema = SchemaExtractor().extract_schema()

            SchemaExporter().export(schema)

        else:
            print("✓ Reusing schema.json")

        if not ENRICHED_SCHEMA_JSON.exists():

            print("Enriching schema...")

            self.enriched_schema = SchemaEnricher().enrich()

        else:
            print("✓ Reusing enriched_schema.json")
            self.enriched_schema = [
                TableInfo.model_validate(item)
                for item in json.loads(
                    ENRICHED_SCHEMA_JSON.read_text()
                )
            ]

        if not GRAPH_JSON.exists():

            print("Building schema graph...")

            GraphProcessor().process()

        else:
            print("✓ Reusing graph.json")

        print("Building value index...")

        ValuePipeline().ingest(
            self.enriched_schema
        )        

        print("Creating chunks...")

        chunks = SchemaChunker().create_chunks()

        print("Generating embeddings...")

        embedded_chunks = SchemaEmbedder().embed_chunks(chunks)

        print(
            f"Generated {len(embedded_chunks)} embeddings."
        )

        store = VectorStore()
        store.upsert(embedded_chunks)
        store.count()