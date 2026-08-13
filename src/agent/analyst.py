from src.evaluation.models import AgentRun
from src.llm.llm_client import CloudLLMClient
from src.pipeline.pipeline_models import RetrievalResult
from src.pipeline.query_pipeline import QueryPipeline
from src.sql.answer.generator import AnswerGenerator
from src.sql.engine import SQLEngine
from src.sql.executor.executor import SQLExecutor
from src.sql.execution.repair_engine import ExecutionRepairEngine
from src.sql.exceptions import SQLExecutionError
from src.sql.executor.models import ExecutionResult
from src.sql.generator.builder import SchemaContextBuilder
from src.sql.generator.models import SchemaContext
from src.sql.models import SQLCandidate, ValidationReport
from src.utils.helper import get_graph

from src.conversation.rewriter import (
    QuestionRewriter,
)


class AnalystAgent:

    MAX_EXECUTION_REPAIRS = 2

    def __init__(self):

        self._pipeline = QueryPipeline()

        self._sql_engine = SQLEngine()

        self._executor = SQLExecutor()

        self._execution_repair = ExecutionRepairEngine()

        self._schema_context_builder = SchemaContextBuilder()

        self._graph = get_graph()

        self._answer_generator = AnswerGenerator()

        self._question_rewriter = QuestionRewriter(
            llm=CloudLLMClient(),
        )

    def retrieve(
        self,
        question: str,
    ) -> RetrievalResult:

        return self._pipeline.retrieve_schema(question)
    
    def retrieve_more_schema(
        self,
        question: str,
        retrieval_result: RetrievalResult,
        validation_report: ValidationReport,
    ) -> RetrievalResult:

        return self._pipeline.retrieve_more_schema(
            question=question,
            retrieval_result=retrieval_result,
            validation_report=validation_report,
        )
    
    def build_schema_context(
        self,
        retrieval_result: RetrievalResult,
    ) -> SchemaContext:

        return self._schema_context_builder.build(
            retrieval_result
        )
    
    def generate_sql(
        self,
        question: str,
        retrieval_result: RetrievalResult,
        schema_context: SchemaContext,
    ) -> SQLCandidate:

        return self._sql_engine.generate(
            plan=retrieval_result.plan,
            question=question,
            schema_context=schema_context,
            graph=self._graph,
        )
    
    def execute_sql(
        self,
        question: str,
        candidate: SQLCandidate,
        schema_context: SchemaContext,
    ) -> ExecutionResult:
        
        for _ in range(self.MAX_EXECUTION_REPAIRS + 1):

            try:
                # breakpoint()
                return self._executor.execute(candidate) 

            except SQLExecutionError as e:

                # breakpoint()

                candidate = self._execution_repair.repair(
                    question=question,
                    candidate=candidate,
                    error=str(e),
                    schema_context=schema_context,
                )

        # breakpoint()

        raise SQLExecutionError(
            "Unable to execute SQL after repair attempts."
        )

    def query(
        self,
        question: str,
    ):
        ...
        
        # state = self._lgraph.invoke(
        #     {
        #         "question": question,
        #     },
        #     config={
        #         "configurable": {
        #             "agent": self,
        #         }
        #     },
        # )
        # return state["run"]

    def generate_candidate(
        self,
        question: str,
        retrieval_result: RetrievalResult,
        schema_context: SchemaContext,
    ) -> SQLCandidate:

        return self._sql_engine.generate_candidate(
            plan=retrieval_result.plan,
            question=question,
            schema_context=schema_context,
    )

    def validate_candidate(
        self,
        candidate: SQLCandidate,
        schema_context: SchemaContext,
    ):

        return self._sql_engine.validate_candidate(
            candidate=candidate,
            schema_context=schema_context,
            graph=self._graph,
        )
    
    def repair_candidate(
        self,
        question: str,
        candidate: SQLCandidate,
        report,
        schema_context: SchemaContext,
    ):

        return self._sql_engine.repair_candidate(
            question=question,
            candidate=candidate,
            report=report,
            schema_context=schema_context,
        )

    def generate_answer(
        self,
        question: str,
        candidate,
        execution_result,
    ):

        return self._answer_generator.generate(
            question=question,
            candidate=candidate,
            execution_result=execution_result,
        )

    def rewrite_question(
        self,
        *,
        question: str,
        history: str,
    ) -> str:

        return self._question_rewriter.rewrite(
            question=question,
            history=history,
        )