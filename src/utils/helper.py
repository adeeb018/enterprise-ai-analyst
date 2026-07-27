import json
import re

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