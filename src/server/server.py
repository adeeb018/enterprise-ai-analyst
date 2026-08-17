"""
Enterprise AI Analyst MCP Server

A Model Context Protocol server that provides persistent conversation management
for an AI analyst that can query a MIMIC-IV medical database using natural language.

Typical workflow:
1. create_conversation(title) → returns conversation_id
2. ask_analyst(question, conversation_id) → returns analyst's answer
3. Repeat step 2 to continue the conversation with history context
4. list_conversations() → view all saved conversations
5. get_conversation(conversation_id) → retrieve full conversation history
6. delete_conversation(conversation_id) → permanently delete a conversation

The analyst uses LangGraph to orchestrate SQL generation and retrieval over medical data.
"""

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
    """
    Initialize and configure the Enterprise AI Analyst MCP server.
    
    Sets up:
    - Transport security with allowed hosts
    - Database connection
    - LangGraph orchestration engine
    - Conversation persistence layer
    - All MCP tools
    
    Returns:
        FastMCP: Configured MCP server instance ready to handle client requests
    """

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
        
        A conversation is a container for multiple turns of interaction with the analyst.
        Each conversation maintains its own history context, allowing the analyst to
        reference prior questions and answers within that conversation.
        
        Args:
            title (str): Human-readable name for the conversation. Defaults to "New Chat".
                        Keep it concise and descriptive (e.g., "EV Charging Analysis", 
                        "Patient Outcomes Q3").
        
        Returns:
            str: The conversation_id (UUID format) to be used in ask_analyst() calls.
                 Save this if you want to continue the conversation later.
        
        Example:
            conv_id = create_conversation("Patient Mortality Analysis")
            # Later: ask_analyst("What was the mortality rate?", conv_id)
        """

        conversation = conversation_manager.create(
            title=title,
        )

        return conversation.conversation_id

    @mcp.tool()
    def health() -> dict:
        """
        Check whether the Enterprise AI Analyst server is running and healthy.
        
        Call this to verify the server is operational before running analysis.
        Checks database connectivity, graph initialization, and service status.
        
        Returns:
            dict: Status information with at minimum a 'status' field indicating 
                  'healthy', 'degraded', or 'unhealthy'. May include additional 
                  diagnostic information.
        
        Example:
            status = health()
            # {'status': 'healthy', 'uptime': '2h 34m', 'db': 'connected'}
        """

        return health_check()

    @mcp.tool()
    def ask_analyst(
        question: str,
        conversation_id: str | None = None,
    ) -> str:
        """
        Ask the Enterprise AI Analyst a question about the medical database.
        
        The analyst uses natural language understanding to:
        1. Parse your question
        2. Identify relevant tables in MIMIC-IV
        3. Generate and execute SQL
        4. Retrieve and format results
        5. Compose a natural language answer
        
        If conversation_id is omitted, a new conversation is automatically created
        with the first 30 characters of your question as its title.
        
        Args:
            question (str): Natural language question about medical data.
                           Examples:
                           - "What was the average length of stay for sepsis patients?"
                           - "How many readmissions occurred within 30 days?"
                           - "Show medication usage trends for ICU patients in 2012"
            
            conversation_id (str | None): UUID of an existing conversation to add
                                         this question to. If None, creates a new
                                         conversation automatically. Optional.
        
        Returns:
            str: The analyst's answer as plain text. Includes:
                 - Direct answer to your question
                 - Supporting data (numbers, percentages, trends)
                 - Any caveats or data limitations
        
        Raises:
            RuntimeError: If the analyst fails to generate an answer or encounters
                         a database error. Check the error message for details.
        
        Example:
            # Start new conversation
            answer = ask_analyst("What is the most common diagnosis?")
            
            # Continue existing conversation with history context
            answer = ask_analyst(
                "How does treatment differ for severe cases?",
                conversation_id="550e8400-e29b-41d4-a716-446655440000"
            )
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
        List all previously saved analyst conversations.
        
        Retrieves metadata about all conversations stored on the server.
        Useful for finding an existing conversation to continue or for auditing.
        
        Returns:
            list[dict]: Array of conversation objects, each containing:
                       - conversation_id (str): UUID identifier
                       - title (str): Human-readable conversation name
                       - created_at (str): ISO 8601 timestamp
                       - updated_at (str): ISO 8601 timestamp of last activity
                       - turn_count (int): Number of question-answer pairs
                       
        Example:
            conversations = list_conversations()
            for conv in conversations:
                print(f"{conv['title']} ({conv['turn_count']} turns)")
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
        Permanently delete a conversation and all of its messages.
        
        This action cannot be undone. All questions, answers, and generated SQL
        associated with this conversation will be removed from the server.
        
        Args:
            conversation_id (str): UUID of the conversation to delete.
                                  Get this from create_conversation() or list_conversations().
        
        Returns:
            str: Confirmation message indicating successful deletion.
        
        Raises:
            ValueError: If conversation_id does not exist or is invalid format.
        
        Example:
            msg = delete_conversation("550e8400-e29b-41d4-a716-446655440000")
            # "Conversation deleted successfully."
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
        Retrieve the complete history of a conversation.
        
        Fetches all turns (question-answer pairs) in the conversation along with
        metadata. Useful for reviewing prior analysis, sharing results, or auditing.
        
        Args:
            conversation_id (str): UUID of the conversation to retrieve.
                                  Get this from create_conversation() or list_conversations().
        
        Returns:
            dict: Complete conversation object containing:
                 - conversation_id (str): UUID identifier
                 - title (str): Conversation name
                 - created_at (str): ISO 8601 creation timestamp
                 - updated_at (str): ISO 8601 last activity timestamp
                 - turns (list[dict]): Array of turns, each containing:
                   - question (str): The user's question
                   - answer (str): The analyst's answer
                   - generated_sql (str | null): SQL query used to answer (if available)
                   - created_at (str): ISO 8601 timestamp of this turn
        
        Raises:
            ValueError: If conversation_id does not exist or is invalid format.
        
        Example:
            conv = get_conversation("550e8400-e29b-41d4-a716-446655440000")
            print(f"Title: {conv['title']}")
            for turn in conv['turns']:
                print(f"Q: {turn['question']}")
                print(f"A: {turn['answer']}")
        """

        conversation = conversation_manager.get(
            conversation_id
        )

        return conversation.model_dump(
            mode="json"
        )

    return mcp