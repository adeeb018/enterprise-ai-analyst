from src.agent.analyst import AnalystAgent
from src.evaluation.models import AgentRun
from src.pipeline.pipeline_models import RetrievalResult
from src.sql.executor.models import ExecutionResult
from src.sql.models import SQLCandidate


class ReplayEngine:

    def __init__(
        self,
        agent: AnalystAgent,
    ):
        self._agent = agent

    def replay_retrieval(
        self,
        question: str,
    ) -> RetrievalResult:

        return self._agent.retrieve(question)

    def replay_schema_context(
        self,
        run: AgentRun
    ):
        if not run.retrieval_result:
            raise ValueError("Cannot replay schema context: retrieval_result is missing from this run.")
    
        return self._agent.build_schema_context(
            run.retrieval_result
        )

    def replay_sql_generation(
        self,
        run: AgentRun,
    ) -> SQLCandidate:

        if not run.retrieval_result or not run.schema_context:
            raise ValueError("Cannot replay SQL generation: missing retrieval or schema context.")

        return self._agent.generate_sql(
            question=run.question,
            retrieval_result=run.retrieval_result,
            schema_context=run.schema_context,
        )

    def replay_execution(
        self,
        run: AgentRun,
    ) -> ExecutionResult:

        if not run.generated_sql or not run.schema_context:
            raise ValueError("Cannot replay execution: missing generated SQL or schema context.")

        return self._agent.execute_sql(
            question=run.question,
            candidate=run.generated_sql,
            schema_context=run.schema_context,
        )