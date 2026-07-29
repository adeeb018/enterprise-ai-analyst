from src.llm.gemini_client import GeminiLLMClient
from src.llm.llm_client import CloudLLMClient
from src.planner.planner_models import QueryPlan
from src.sql.generator.prompt_builder import PromptBuilder
from src.sql.models import SQLCandidate
from src.utils.helper import parse_llm_json


class SQLGenerator:
    """
    Generates SQL from a natural language question.

        Question
            ↓
      PromptBuilder
            ↓
            LLM
            ↓
      SQLCandidate
    """

    def __init__(self):

        self._prompt_builder = PromptBuilder()
        self._llm = GeminiLLMClient()

    def generate(
        self,
        *,
        plan: QueryPlan,
        question: str,
        schema_context,
    ) -> SQLCandidate:

        prompt = self._prompt_builder.build(
            plan=plan,
            question=question,
            schema_context=schema_context,
        )

        response = self._llm.generate(
            prompt=prompt,
            format="json",
        )

        result = parse_llm_json(response)

        return SQLCandidate(
            sql=result["sql"],
            explanation=result.get("explanation"),
        )