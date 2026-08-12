from src.conversation.prompt_builder import (
    QuestionRewritePromptBuilder,
)


class QuestionRewriter:

    def __init__(
        self,
        llm,
    ):

        self._llm = llm  # type: ignore

        self._prompt_builder = (
            QuestionRewritePromptBuilder()
        )

    def rewrite(
        self,
        *,
        question: str,
        history: str,
    ) -> str:

        if not history.strip():
            return question

        prompt = self._prompt_builder.build(
            question=question,
            history=history,
        )

        response = self._llm.generate(
            prompt=prompt,
        )

        rewritten = response.strip()

        if not rewritten:
            return question

        return rewritten