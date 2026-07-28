from src.llm.gemini_client import GeminiLLMClient
from src.llm.llm_client import CloudLLMClient
from src.sql.models import (
    SQLCandidate,
    ValidationReport,
)
from src.sql.repair.planner import RepairPlanner
from src.sql.repair.prompt_builder import RepairPromptBuilder
from src.sql.repair.result import RepairAttempt, RepairResult
from src.utils.helper import parse_llm_json


class RepairEngine:
    """
    Orchestrates SQL repair.

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

    MAX_RETRIES = 1

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
        validator,
        schema_context,
        graph
    ) -> RepairResult:

        history: list[RepairAttempt] = []

        current_sql = candidate.sql
        current_report = report

        for attempt in range(1, self.MAX_RETRIES + 1):

            history.append(
                RepairAttempt(
                    attempt=attempt,
                    sql=current_sql,
                    validation_report=current_report,
                )
            )

            plan = self._planner.create_plan(
                question=question,
                sql=current_sql,
                report=current_report,
            )

            prompt = self._prompt_builder.build(
                plan=plan,
                schema_context= schema_context
            )
            print(prompt)

            response = self._llm.generate(
                prompt=prompt,
                format="json",
            )
            # print(f"response",response)

            repaired = parse_llm_json(response)
            # print(f"repaired",repaired)

            current_sql = repaired["sql"]

            repaired_candidate = SQLCandidate(
                sql=current_sql,
            )

            current_report = validator.validate(
                repaired_candidate,
                schema_context,
                graph
            )

            if current_report.is_valid:

                history.append(
                    RepairAttempt(
                        attempt=attempt,
                        sql=current_sql,
                        validation_report=current_report,
                    )
                )

                return RepairResult(
                    success=True,
                    sql=current_sql,
                    attempts=attempt,
                    history=history,
                )

        return RepairResult(
            success=False,
            sql=current_sql,
            attempts=self.MAX_RETRIES,
            history=history,
        )