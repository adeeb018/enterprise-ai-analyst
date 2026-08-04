from src.sql.executor.models import ExecutionResult
from src.sql.models import SQLCandidate


class AnswerPromptBuilder:

    MAX_ROWS = 20

    def build(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        execution_result: ExecutionResult,
    ) -> str:

        rows = execution_result.rows[: self.MAX_ROWS]

        row_text = "\n".join(
            str(row)
            for row in rows
        )

        return f"""
You are an enterprise data analyst.

Your job is to answer the user's question using ONLY the SQL results.

Never invent facts.

If the SQL result is empty, clearly say that.

User Question:
{question}

SQL:
{candidate.sql}

Columns:
{execution_result.columns}

Returned Rows:
{row_text}

Row Count:
{execution_result.row_count}

Answer naturally.
"""