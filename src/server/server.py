from mcp.server.fastmcp import FastMCP
import os
from mcp.server.transport_security import TransportSecuritySettings
from src.orchestration.langgraph.graph import build_graph
from src.conversation.history import (
    ConversationHistoryFormatter,
)
from src.conversation.manager import (
    ConversationManager,
)

from src.sql.executor.connection import init_db

from src.server.health import health_check

def create_mcp_server() -> FastMCP:

    allowed_host = os.environ.get(
        "MCP_ALLOWED_HOST",
        "localhost",
    )

    mcp = FastMCP(
        "Enterprise AI Analyst",
        transport_security=TransportSecuritySettings(
            allowed_hosts=[allowed_host],
        ),
    )

    init_db()


    graph = build_graph()

    conversation_manager = ConversationManager()

    history_formatter = ConversationHistoryFormatter()

    @mcp.tool()
    def create_conversation(
        title: str = "New Chat",
    ) -> str:
        """
        Create a new persistent analyst conversation.
        """

        conversation = conversation_manager.create(
            title=title,
        )

        return conversation.conversation_id


    @mcp.tool()
    def health() -> dict:
        """
        Check whether the Enterprise AI Analyst is running.
        """

        return health_check()


    @mcp.tool()
    def ask_analyst(
        question: str,
        conversation_id: str | None = None,
    ) -> str:
        """
        Ask the Enterprise AI Analyst a question
        within an existing conversation.
        """

        if not conversation_id:
            new_conv = conversation_manager.create(
                title=question[:30] + "..." if len(question) > 30 else question
            )
            conversation_id = new_conv.conversation_id
            history = ""
        else:
            conversation = conversation_manager.get(conversation_id)
            history = history_formatter.format(conversation)

        result = graph.invoke(
            {
                "question": question,
                "conversation_id": conversation_id,
                "conversation_history": history,
            }
        )

        run = result["run"]

        if not run.success:
            raise RuntimeError(
                run.error
                or "Analyst failed to answer the question."
            )

        answer_obj = run.answer

        if answer_obj is None:
            raise RuntimeError(
                "Analyst completed without generating "
                "an answer."
            )

        answer_text = (
            answer_obj.answer
            if hasattr(answer_obj, "answer")
            else str(answer_obj)
        )

        generated_sql_str = None
        if run.generated_sql:
            if hasattr(run.generated_sql, "sql"):
                generated_sql_str = run.generated_sql.sql
            elif isinstance(run.generated_sql, dict):
                generated_sql_str = run.generated_sql.get("sql")

        conversation_manager.add_turn(
            conversation_id=conversation_id,
            question=question,
            answer=answer_text,
            generated_sql=generated_sql_str,
        )

        return answer_text





    @mcp.tool()
    def list_conversations() -> list[dict]:
        """
        List previously saved analyst conversations.
        """

        conversations = (
            conversation_manager.list()
        )

        return [
            conversation.model_dump(
                mode="json"
            )
            for conversation in conversations
        ]

    @mcp.tool()
    def delete_conversation(
        conversation_id: str,
    ) -> str:
        """
        Permanently delete a conversation and
        all of its messages.
        """

        conversation_manager.delete(
            conversation_id
        )

        return "Conversation deleted successfully."

    @mcp.tool()
    def get_conversation(
        conversation_id: str,
    ) -> dict:
        """
        Return the complete conversation history.
        """

        conversation = conversation_manager.get(
            conversation_id
        )

        return conversation.model_dump(
            mode="json"
        )
    return mcp