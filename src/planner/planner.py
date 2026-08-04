from src.llm.ollama_client import OllamaClient

from src.planner.prompts import PLANNER_PROMPT
from src.planner.planner_models import QueryPlan


class Planner:

    def __init__(self):

        self.llm = OllamaClient()

    def plan(
        self,
        question: str,
    ) -> QueryPlan:

        prompt = PLANNER_PROMPT.format(
            question=question
        )

        response = self.llm.generate(
            prompt,
            format="json",
        )

        try:

            return QueryPlan.model_validate_json(response)

        except Exception:

            print("LLM returned:")

            print(response)

            raise