from datetime import datetime

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):

    turn_id: int

    conversation_id: str

    question: str

    answer: str | None = None

    generated_sql: str | None = None

    created_at: datetime


class Conversation(BaseModel):

    conversation_id: str

    title: str

    created_at: datetime

    updated_at: datetime

    turns: list[ConversationTurn] = Field(
        default_factory=list
    )


class ConversationSummary(BaseModel):

    conversation_id: str

    title: str

    created_at: datetime

    updated_at: datetime