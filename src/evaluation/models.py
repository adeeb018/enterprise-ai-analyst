from src.pipeline.pipeline_models import RetrievalResult
from src.sql.generator.models import SchemaContext
from src.sql.executor.models import ExecutionResult
from src.sql.models import SQLCandidate
from pydantic import BaseModel

class AgentRun(BaseModel):

    question: str

    retrieval_result: RetrievalResult

    schema_context: SchemaContext

    generated_sql: SQLCandidate

    execution_result: ExecutionResult


class BenchmarkQuestion(BaseModel):

    id: str

    question: str