from src.sql.models import SQLCandidate


class ExecutionRepairPromptBuilder:
    """
    Builds prompts for repairing SQL that failed during execution.
    """

    def build(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        error: str,
        schema_context,
    ) -> str:

        return f"""
You are an expert PostgreSQL SQL engineer.

The following SQL failed during execution.

Question:
{question}

Generated SQL:
{candidate.sql}

Database Error:
{error}

Relevant Schema:
{schema_context}

Return ONLY JSON.

{{
    "sql": "...",
    "explanation": "..."
}}
"""