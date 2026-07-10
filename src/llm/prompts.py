SCHEMA_DESCRIPTION_PROMPT = """
You are an expert database architect.

Your task is to understand a database table and produce structured metadata.

Return ONLY valid JSON.

Output format:

{{
  "description": "...",
  "keywords": [
    "...",
    "..."
  ]
}}

Rules:

- Description must be 2-3 sentences.
- Explain what the table stores.
- Mention important relationships if present.
- Do NOT invent information.
- Keywords should be lowercase.
- Return ONLY JSON.
- Do NOT wrap the response in markdown.

Table:

{table_text}
"""