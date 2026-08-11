from mcp.server.fastmcp import FastMCP
from src.orchestration.langgraph.graph import build_graph

mcp = FastMCP(
    "Enterprise AI Analyst",
)


graph = build_graph()


@mcp.tool()
def ask_analyst(
    question: str,
) -> str:
    """
    Ask the Enterprise AI Analyst a natural-language
    question about the enterprise database.

    The analyst plans the question, retrieves schema,
    generates and validates SQL, executes it, and
    produces a natural-language answer.
    """

    result = graph.invoke({"question": question})

    if not result["run"].success:
        raise RuntimeError(
            result["run"].error or "Analyst failed to answer the question."
        )

    answer_obj = result["run"].answer

    if answer_obj is None:
        raise RuntimeError(
            "Analyst completed without generating an answer."
        )

    answer_text = answer_obj.answer if hasattr(answer_obj, "answer") else str(answer_obj)

    return answer_text


if __name__ == "__main__":
    mcp.run()