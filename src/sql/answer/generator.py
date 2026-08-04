from src.llm.llm_client import CloudLLMClient
from src.sql.answer.models import AnalystAnswer
from src.sql.answer.prompt_builder import AnswerPromptBuilder


class AnswerGenerator:

    def __init__(self):

        self._prompt_builder = AnswerPromptBuilder()

        self._llm = CloudLLMClient()

    def generate(
        self,
        *,
        question: str,
        candidate,
        execution_result,
    ) -> AnalystAnswer:

        prompt = self._prompt_builder.build(
            question=question,
            candidate=candidate,
            execution_result=execution_result,
        )

        response = self._llm.generate(
            prompt=prompt,
        )

        return AnalystAnswer(
            answer=response.strip(),
        )