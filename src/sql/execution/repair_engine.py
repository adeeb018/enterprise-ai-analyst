from src.llm.llm_client import CloudLLMClient

from src.sql.execution.prompt_builder import (
    ExecutionRepairPromptBuilder,
)
from src.sql.models import SQLCandidate
from src.utils.helper import parse_llm_json


class ExecutionRepairEngine:
    """
    Repairs SQL using PostgreSQL execution errors.
    """

    def __init__(self):

        self._prompt_builder = ExecutionRepairPromptBuilder()
        self._llm = CloudLLMClient()

    def repair(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        error: str,
        schema_context,
    ) -> SQLCandidate:

        prompt = self._prompt_builder.build(
            question=question,
            candidate=candidate,
            error=error,
            schema_context=schema_context,
        )

        response = self._llm.generate(
            prompt=prompt,
            format="json",
        )

        repaired = parse_llm_json(response)

        return SQLCandidate(
            sql=repaired["sql"],
            explanation=repaired.get("explanation"),
        )