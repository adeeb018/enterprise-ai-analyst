from uuid import uuid4

from datetime import datetime, UTC

from sqlalchemy import select

from src.sql.executor.connection import SessionLocal



from .database import (
    ConversationDB,
    ConversationTurnDB,
)
from .models import (
    Conversation,
    ConversationSummary,
    ConversationTurn,
)


class ConversationManager:

    def create(
        self,
        title: str = "New Chat",
    ) -> ConversationSummary:

        conversation_id = str(uuid4())

        with SessionLocal() as session:

            conversation = ConversationDB(
                id=conversation_id,
                title=title,
            )

            session.add(conversation)

            session.commit()

            session.refresh(conversation)

            return ConversationSummary(
                conversation_id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )

    def list(
        self,
    ) -> list[ConversationSummary]:

        with SessionLocal() as session:

            conversations = session.scalars(
                select(ConversationDB)
                .order_by(
                    ConversationDB.updated_at.desc()
                )
            ).all()

            return [
                ConversationSummary(
                    conversation_id=conversation.id,
                    title=conversation.title,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at,
                )
                for conversation in conversations
            ]

    def get(
        self,
        conversation_id: str,
    ) -> Conversation:

        with SessionLocal() as session:

            conversation = session.scalar(
                select(ConversationDB)
                .where(
                    ConversationDB.id == conversation_id
                )
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation '{conversation_id}' "
                    "does not exist."
                )

            return Conversation(
                conversation_id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                turns=[
                    ConversationTurn(
                        turn_id=turn.turn_number,
                        conversation_id=turn.conversation_id,
                        question=turn.question,
                        answer=turn.answer,
                        generated_sql=turn.generated_sql,
                        created_at=turn.created_at,
                    )
                    for turn in conversation.turns
                ],
            )

    def add_turn(
        self,
        *,
        conversation_id: str,
        question: str,
        answer: str | None,
        generated_sql: str | None,
    ) -> ConversationTurn:

        with SessionLocal() as session:

            conversation = session.scalar(
                select(ConversationDB)
                .where(
                    ConversationDB.id == conversation_id
                )
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation '{conversation_id}' "
                    "does not exist."
                )

            last_turn = session.scalar(
                select(ConversationTurnDB)
                .where(
                    ConversationTurnDB.conversation_id
                    == conversation_id
                )
                .order_by(
                    ConversationTurnDB.turn_number.desc()
                )
            )

            next_turn = (
                last_turn.turn_number + 1
                if last_turn
                else 1
            )

            turn = ConversationTurnDB(
                conversation_id=conversation_id,
                turn_number=next_turn,
                question=question,
                answer=answer,
                generated_sql=generated_sql,
            )

            session.add(turn)

            conversation.updated_at = (
                datetime.now(UTC)
            )

            session.commit()

            session.refresh(turn)

            return ConversationTurn(
                turn_id=turn.turn_number,
                conversation_id=turn.conversation_id,
                question=turn.question,
                answer=turn.answer,
                generated_sql=turn.generated_sql,
                created_at=turn.created_at,
            )

    def delete(
        self,
        conversation_id: str,
    ) -> None:

        with SessionLocal() as session:

            conversation = session.scalar(
                select(ConversationDB)
                .where(
                    ConversationDB.id == conversation_id
                )
            )

            if conversation is None:
                raise ValueError(
                    f"Conversation '{conversation_id}' "
                    "does not exist."
                )

            session.delete(conversation)

            session.commit()