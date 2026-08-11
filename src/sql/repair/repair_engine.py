from src.graph.schema_graph import SchemaGraph
# from src.llm.llm_client import CloudLLMClient
from src.sql.models import (
    SQLCandidate,
    ValidationReport,
)
from src.sql.repair.planner import RepairPlanner
from src.sql.repair.prompt_builder import RepairPromptBuilder
from src.utils.helper import parse_llm_json
import time
from src.llm.gemini_client import GeminiLLMClient


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
        self._llm = GeminiLLMClient()  # type: ignore


    def repair(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        report: ValidationReport,
        schema_context,
        graph: SchemaGraph = None
    ) -> SQLCandidate:

        t0 = time.perf_counter()
        plan = self._planner.create_plan(
            question=question,
            sql=candidate.sql,
            report=report,
            graph=graph
        )
        print(f"⏱️ RepairPlanner took: {time.perf_counter() - t0:.3f}s")

        t1 = time.perf_counter()
        prompt = self._prompt_builder.build(
            plan=plan,
            schema_context=schema_context,
        )
        print(f"⏱️ RepairPromptBuilder took: {time.perf_counter() - t1:.3f}s")

        t2 = time.perf_counter()
        response = self._llm.generate(
            prompt=prompt,
            format="json",
        )
        print(f"⏱️ LLM Repair Generation took: {time.perf_counter() - t2:.3f}s")

        repaired = parse_llm_json(response)

        return SQLCandidate(
            sql=repaired["sql"],
            explanation=repaired.get("explanation"),
        )