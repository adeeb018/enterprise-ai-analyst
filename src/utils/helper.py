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


import time
from datetime import datetime
from functools import wraps

def measure_node(node_name: str, node_func):
    """Wraps a LangGraph node to capture start time, end time, and total duration."""
    @wraps(node_func)
    def wrapper(state, *args, **kwargs):
        # Capture precise start times
        start_perf = time.perf_counter()
        start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Execute node logic
        result = node_func(state, *args, **kwargs)
        
        # Capture precise end times
        end_perf = time.perf_counter()
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        duration = round(end_perf - start_perf, 3)
        
        # Prepare node metrics payload
        node_timing = {
            "start_time": start_timestamp,
            "end_time": end_timestamp,
            "total_time_sec": duration
        }
        
        # Safely update timings in state
        current_state = result if isinstance(result, dict) else state
        timings = current_state.get("timings", state.get("timings", {})).copy()
        timings[node_name] = node_timing
        
        if isinstance(result, dict):
            result["timings"] = timings
        else:
            state["timings"] = timings
            
        print(f"⏱️ Node [{node_name}] | Start: {start_timestamp} | End: {end_timestamp} | Total: {duration}s")
        return result
        
    return wrapper