from src.evaluation.models import AgentRun
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
        
        try:

            retrieval_result = self.retrieve(question)

            schema_context = self.build_schema_context(
                retrieval_result
            )

            candidate = self.generate_sql(
                question,
                retrieval_result,
                schema_context,
            )

            execution_result = self.execute_sql(
                question,
                candidate,
                schema_context,
            )

            answer = self.generate_answer(
                question,
                candidate,
                execution_result,
            )

            return AgentRun(
                question=question,
                retrieval_result=retrieval_result,
                schema_context=schema_context,
                generated_sql=candidate,
                execution_result=execution_result,
                answer=answer,
            )
        
        except Exception as e:
            # Capture any failure across the entire pipeline safely
            return AgentRun(
                question=question,
                retrieval_result=locals().get("retrieval_result"),
                schema_context=locals().get("schema_context"),
                generated_sql=locals().get("candidate"),
                execution_result=None,
                answer=None,
                success=False,
                error=str(e),
            ) 

        # candidate = SQLCandidate(sql="SELECT DISTINCT p.subject_id, p.gender, p.anchor_age, p.dod, i.stay_id, i.intime, i.outtime FROM mimiciv_hosp.patients p INNER JOIN mimiciv_icu.icustays i ON p.subject_id = i.subject_id INNER JOIN mimiciv_hosp.admissions a ON i.hadm_id = a.hadm_id INNER JOIN mimiciv_hosp.diagnoses_icd d ON a.hadm_id = d.hadm_id INNER JOIN mimiciv_hosp.d_icd_diagnoses di ON d.icd_code = di.icd_code AND d.icd_version = di.icd_version WHERE di.long_title ILIKE '%diabetes%'", explanation='Replaced invalid direct join between icustays and diagnoses_icd with a join through the admissions table, using the existing foreign key relationships: icustays.hadm_id -> admissions.hadm_id and diagnoses_icd.hadm_id -> admissions.hadm_id.', status=SQLStatus.GENERATED)

        # candidate = SQLCandidate(
        #     sql=(
        #         "SELECT DISTINCT p.subject_id, p.non_existent_column_xyz "
        #         "FROM mimiciv_hosp.patients p "
        #         "INNER JOIN mimiciv_hosp.admissions a ON p.subject_id = a.subject_id "
        #         "INNER JOIN mimiciv_icu.icustays i ON a.hadm_id = i.hadm_id"
        #     ),
        #     explanation="Intentionally flawed SQL with a fake column to trigger an execution exception for testing.",
        #     status=SQLStatus.GENERATED
        # )

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