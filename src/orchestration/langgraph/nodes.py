from langchain_core.runnables import RunnableConfig

from src.agent.analyst import AnalystAgent
from src.agent.state import AnalystState
from src.evaluation.models import AgentRun


def retrieve_node(
    state: AnalystState,
    config: RunnableConfig,
):

    agent: AnalystAgent = config["configurable"]["agent"]

    retrieval_result = agent.retrieve(
        state["question"]
    )

    return {
        "retrieval_result": retrieval_result,
    }


def schema_context_node(
    state: AnalystState,
    config: RunnableConfig,
):

    agent: AnalystAgent = config["configurable"]["agent"]

    schema_context = agent.build_schema_context(
        state["retrieval_result"]
    )

    return {
        "schema_context": schema_context,
    }


def generate_sql_node(
    state: AnalystState,
    config: RunnableConfig,
):

    agent: AnalystAgent = config["configurable"]["agent"]

    candidate = agent.generate_sql(
        question=state["question"],
        retrieval_result=state["retrieval_result"],
        schema_context=state["schema_context"],
    )

    return {
        "candidate": candidate,
    }


def execute_sql_node(
    state: AnalystState,
    config: RunnableConfig,
):

    agent: AnalystAgent = config["configurable"]["agent"]

    execution_result = agent.execute_sql(
        question=state["question"],
        candidate=state["candidate"],
        schema_context=state["schema_context"],
    )

    return {
        "execution_result": execution_result,
    }


def build_run_node(
    state: AnalystState,
):

    run = AgentRun(
        question=state["question"],
        retrieval_result=state["retrieval_result"],
        schema_context=state["schema_context"],
        generated_sql=state["candidate"],
        execution_result=state["execution_result"],
        success=True,
        error=None,
    )

    return {
        "run": run,
    }