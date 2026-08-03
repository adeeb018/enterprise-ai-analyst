from langgraph.graph import START, END, StateGraph

from src.agent.state import AnalystState

from .nodes import (
    retrieve_node,
    schema_context_node,
    generate_sql_node,
    execute_sql_node,
    build_run_node,
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

    builder.add_node(
        "generate_sql",
        generate_sql_node,
    )

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

    builder.add_edge(
        "schema_context",
        "generate_sql",
    )

    builder.add_edge(
        "generate_sql",
        "execute_sql",
    )

    builder.add_edge(
        "execute_sql",
        "build_run",
    )

    builder.add_edge(
        "build_run",
        END,
    )

    return builder.compile()