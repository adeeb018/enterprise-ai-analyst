SCHEMA_DESCRIPTION_PROMPT = """
You are a healthcare database expert.

Your task is to generate semantic metadata for a database table.

This metadata will be embedded into a vector database and used by an AI system to retrieve the correct tables when answering natural language questions and generating SQL.

Return ONLY valid JSON.

Format:

{{
  "description": "...",
  "keywords": [
    "...",
    "..."
  ]
}}

Rules:

- Describe the business purpose of the table.
- Explain what information it stores.
- Mention typical analytical questions this table helps answer.
- Use specific medical and database terminology.
- Avoid generic phrases like "stores patient data" or "contains hospital information".
- Do not invent facts that cannot be inferred from the schema.
- Generate 5-8 specific keywords that users might naturally search for.
- Return ONLY valid JSON.

Table:

{table_text}
"""