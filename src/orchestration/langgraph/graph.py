from langgraph.graph import START, END, StateGraph

from src.agent.state import AnalystState
from src.orchestration.langgraph.routers import validation_router
from src.utils.helper import measure_node

from .nodes import (
    answer_node,
    generate_candidate_node,
    repair_candidate_node,
    retrieve_more_schema_node,
    retrieve_node,
    schema_context_node,
    # generate_sql_node,
    execute_sql_node,
    build_run_node,
    validate_candidate_node,
    rewrite_question_node
)


def build_graph():

    builder = StateGraph(AnalystState)

    #
    # Register Nodes
    #
    builder.add_node("rewrite_question", measure_node("rewrite_question", rewrite_question_node))
    builder.add_node("retrieve", measure_node("retrieve", retrieve_node))
    builder.add_node("schema_context", measure_node("schema_context", schema_context_node))
    builder.add_node("generate_candidate", measure_node("generate_candidate", generate_candidate_node))
    builder.add_node("validate_candidate", measure_node("validate_candidate", validate_candidate_node))
    builder.add_node("repair_candidate", measure_node("repair_candidate", repair_candidate_node))
    builder.add_node("retrieve_more_schema", measure_node("retrieve_more_schema", retrieve_more_schema_node))
    builder.add_node("execute_sql", measure_node("execute_sql", execute_sql_node))
    builder.add_node("answer_node", measure_node("answer_node", answer_node))
    builder.add_node("build_run", measure_node("build_run", build_run_node))
    

    #
    # Build Graph
    #

    builder.add_edge(
        START,
        "rewrite_question",
    )

    builder.add_edge(
        "rewrite_question",
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
            "retrieve_more_schema": "retrieve_more_schema",
            "max_retries_exceeded": "execute_sql",
        }
    )

    builder.add_edge("repair_candidate", "validate_candidate")
    # builder.add_edge(
    #     "generate_sql",
    #     "execute_sql",
    # )
    builder.add_edge("retrieve_more_schema", "schema_context",)

    builder.add_edge(
        "execute_sql",
        "answer_node",
    )

    builder.add_edge(
            "answer_node",
            "build_run",
        )


    builder.add_edge(
        "build_run",
        END,
    )

    return builder.compile()