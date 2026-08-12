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
    question_to_use = state.get("resolved_question") or state["question"]

    retrieval_result = agent.retrieve(
        question_to_use
    )

    return {
        "retrieval_result": retrieval_result,
    }

def retrieve_more_schema_node(
    state: AnalystState,
    config,
):

    question_to_use = state.get("resolved_question") or state["question"]
    retrieval_result = agent.retrieve_more_schema(
        question_to_use,
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
    question_to_use = state.get("resolved_question") or state["question"]
    candidate = agent.generate_sql(
        question=question_to_use,
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

    # breakpoint()
    question_to_use = state.get("resolved_question") or state["question"]

    execution_result = agent.execute_sql(
        question=question_to_use,
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
        resolved_question=state.get(
            "resolved_question"
        ),
        retrieval_result=state["retrieval_result"],
        schema_context=state["schema_context"],
        generated_sql=state["candidate"],
        execution_result=execution_result,
        success=not has_error,
        answer=state["answer"],
        error=state.get("error") if has_error else None,
    )

    timings = state.get("timings", {})
    
    if timings:
        print("\n=====================================================================")
        print("📊 LANGGRAPH EXECUTION TIMING REPORT")
        print("=====================================================================")
        print(f"{'Node Name':<22} | {'Start Time':<23} | {'End Time':<23} | {'Duration'}")
        print("-" * 77)
        
        # Sort nodes by start time or duration
        for node_name, data in timings.items():
            print(f"{node_name:<22} | {data['start_time']} | {data['end_time']} | {data['total_time_sec']:>6.3f}s")
            
        print("=====================================================================\n")

    return {
        "run": run,
    }

def generate_candidate_node(state, config):

    # agent = config["configurable"]["agent"]
    question_to_use = state.get("resolved_question") or state["question"]
    candidate = agent.generate_candidate(
        question=question_to_use,
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
    # breakpoint()
    
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
    question_to_use = state.get("resolved_question") or state["question"]
    candidate = agent.repair_candidate(
        question=question_to_use,
        candidate=state["candidate"],
        report=state["validation_report"],
        schema_context=state["schema_context"],
    )

    return {
        "candidate": candidate,
        "repair_count": new_repair_count,
    }

def answer_node(
    state,
    config,
):

    question_to_use = state.get("resolved_question") or state["question"]
    answer = agent.generate_answer(
        question=question_to_use,
        candidate=state["candidate"],
        execution_result=state["execution_result"],
    )

    return {
        "answer": answer,
    }

def rewrite_question_node(
    state: AnalystState,
    config,
):

    question = state["question"]

    history = state.get(
        "conversation_history",
        "",
    )

    if not history:
        return {
            "resolved_question": question,
        }


    resolved_question = (
        agent.rewrite_question(
            question=question,
            history=history,
        )
    )

    print(
        "\nOriginal question:",
        question,
    )

    print(
        "Resolved question:",
        resolved_question,
    )

    return {
        "resolved_question": resolved_question,
    }