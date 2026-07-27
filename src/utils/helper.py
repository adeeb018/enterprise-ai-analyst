import json
import re

from src.config.paths import ENRICHED_SCHEMA_JSON, GRAPH_JSON
from src.graph.graph_loader import GraphLoader
from src.graph.schema_graph import SchemaGraph
from src.ingestion.schema_models import TableInfo

def parse_llm_json(response_str: str) -> dict:
    """Safely extracts and parses JSON from an LLM response string, 
    handling markdown blocks and trailing artifacts."""
    cleaned = response_str.strip()
    
    # 1. Try standard load first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Extract content between the first '{' and the last '}'
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Extracted string is still invalid JSON: {e}")
            
    raise ValueError(f"Could not find valid JSON object in response:\n{response_str}")


def get_graph() -> SchemaGraph:

        schema = [
            TableInfo.model_validate(item)
            for item in json.loads(
                ENRICHED_SCHEMA_JSON.read_text()
            )
        ]

        graph = GraphLoader().load(
            graph_path=GRAPH_JSON,
            schema=schema,
        )

        return graph