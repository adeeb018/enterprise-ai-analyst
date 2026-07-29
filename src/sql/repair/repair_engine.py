from src.llm.llm_client import CloudLLMClient
from src.sql.models import (
    SQLCandidate,
    ValidationReport,
)
from src.sql.repair.planner import RepairPlanner
from src.sql.repair.prompt_builder import RepairPromptBuilder
from src.utils.helper import parse_llm_json


class RepairEngine:
    """
    Repairs an invalid SQL query.

    ValidationReport
            ↓
      RepairPlanner
            ↓
     RepairPromptBuilder
            ↓
            LLM
            ↓
      SQLCandidate
    """

    def __init__(self):

        self._planner = RepairPlanner()
        self._prompt_builder = RepairPromptBuilder()
        self._llm = CloudLLMClient()

    def repair(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        report: ValidationReport,
        schema_context,
    ) -> SQLCandidate:

        plan = self._planner.create_plan(
            question=question,
            sql=candidate.sql,
            report=report,
        )

        prompt = self._prompt_builder.build(
            plan=plan,
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