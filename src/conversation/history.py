from .models import Conversation


class ConversationHistoryFormatter:

    MAX_TURNS = 5

    def format(
        self,
        conversation: Conversation,
    ) -> str:

        turns = conversation.turns[
            -self.MAX_TURNS:
        ]

        if not turns:
            return ""

        parts: list[str] = []

        for turn in turns:

            parts.append(
                f"User: {turn.question}"
            )

            if turn.answer:
                parts.append(
                    f"Assistant: {turn.answer}"
                )

        return "\n\n".join(parts)