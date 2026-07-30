from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

SCHEMA_DIR = DATA_DIR / "schema"

SCHEMA_JSON = SCHEMA_DIR / "schema.json"
ENRICHED_SCHEMA_JSON = SCHEMA_DIR / "enriched_schema.json"

GRAPH_JSON = DATA_DIR / "graph.json"

QDRANT_COLLECTION = "hospital_schema"

TEST_DIRECTORY = DATA_DIR/ "test"

