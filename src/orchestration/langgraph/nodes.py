from langchain_core.runnables import RunnableConfig

from src.agent.analyst import AnalystAgent
from src.agent.state import AnalystState
from src.evaluation.models import AgentRun
from src.sql.validator.decision_builder import ValidationDecisionBuilder

agent = AnalystAgent()

def retrieve_node(
    state: AnalystState,
    config: RunnableConfig,
):

    # agent: AnalystAgent = config["configurable"]["agent"]

    retrieval_result = agent.retrieve(
        state["question"]
    )

    return {
        "retrieval_result": retrieval_result,
    }

def retrieve_more_schema_node(
    state: AnalystState,
    config,
):

    retrieval_result = agent.retrieve_more_schema(
        question=state["question"],
        retrieval_result=state["retrieval_result"],
        validation_report=state["validation_report"],
    )

    return {
        "retrieval_result": retrieval_result,
    }


def schema_context_node(
    state: AnalystState,
    config: RunnableConfig,
):

    # agent: AnalystAgent = config["configurable"]["agent"]

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

    # agent: AnalystAgent = config["configurable"]["agent"]

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

    # agent: AnalystAgent = config["configurable"]["agent"]

    breakpoint()

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
    execution_result = state.get("execution_result")
    has_error = "error" in state or execution_result is None

    run = AgentRun(
        question=state["question"],
        retrieval_result=state["retrieval_result"],
        schema_context=state["schema_context"],
        generated_sql=state["candidate"],
        execution_result=execution_result,
        success=not has_error,
        error=state.get("error") if has_error else None,
    )

    return {
        "run": run,
    }

def generate_candidate_node(state, config):

    # agent = config["configurable"]["agent"]

    candidate = agent.generate_candidate(
        question=state["question"],
        retrieval_result=state["retrieval_result"],
        schema_context=state["schema_context"],
    )

    return {
        "candidate": candidate,
    }

def validate_candidate_node(state, config):

    # agent = config["configurable"]["agent"]

    report = agent.validate_candidate(
        candidate=state["candidate"],
        schema_context=state["schema_context"],
    )
    breakpoint()
    
    decision_builder = ValidationDecisionBuilder()
    decision = decision_builder.build(report)

    return {
        "validation_report": report,
        "validation_decision": decision,
    }

def repair_candidate_node(state, config):

    # agent = config["configurable"]["agent"]

    current_repairs = state.get("repair_count", 0)

    new_repair_count = current_repairs + 1

    candidate = agent.repair_candidate(
        question=state["question"],
        candidate=state["candidate"],
        report=state["validation_report"],
        schema_context=state["schema_context"],
    )

    return {
        "candidate": candidate,
        "repair_count": new_repair_count,
    }