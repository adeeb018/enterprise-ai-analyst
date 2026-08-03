from langgraph.graph import START, END, StateGraph

from src.agent.state import AnalystState
from src.orchestration.langgraph.routers import validation_router

from .nodes import (
    generate_candidate_node,
    repair_candidate_node,
    retrieve_node,
    schema_context_node,
    # generate_sql_node,
    execute_sql_node,
    build_run_node,
    validate_candidate_node,
)


def build_graph():

    builder = StateGraph(AnalystState)

    #
    # Register Nodes
    #
    builder.add_node(
        "retrieve",
        retrieve_node,
    )

    builder.add_node(
        "schema_context",
        schema_context_node,
    )

    builder.add_node("generate_candidate", generate_candidate_node)
    builder.add_node("validate_candidate", validate_candidate_node)
    builder.add_node("repair_candidate", repair_candidate_node)

    # builder.add_node(
    #     "generate_sql",
    #     generate_sql_node,
    # )

    builder.add_node(
        "execute_sql",
        execute_sql_node,
    )

    builder.add_node(
        "build_run",
        build_run_node,
    )

    #
    # Build Graph
    #
    builder.add_edge(
        START,
        "retrieve",
    )

    builder.add_edge(
        "retrieve",
        "schema_context",
    )

    # builder.add_edge(
    #     "schema_context",
    #     "generate_sql",
    # )
    builder.add_edge("schema_context", "generate_candidate")
    builder.add_edge("generate_candidate", "validate_candidate")

    builder.add_conditional_edges(
        "validate_candidate",
        validation_router,
        {
            "execute_sql": "execute_sql",
            "repair_candidate": "repair_candidate",
            "max_retries_exceeded": "execute_sql",
        }
    )

    builder.add_edge("repair_candidate", "validate_candidate")
    # builder.add_edge(
    #     "generate_sql",
    #     "execute_sql",
    # )

    builder.add_edge(
        "execute_sql",
        "build_run",
    )

    builder.add_edge(
        "build_run",
        END,
    )

    return builder.compile()