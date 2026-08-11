from typing import Optional

from src.pipeline.pipeline_models import RetrievalResult
from src.sql.answer.models import AnalystAnswer
from src.sql.generator.models import SchemaContext
from src.sql.executor.models import ExecutionResult
from src.sql.models import SQLCandidate
from pydantic import BaseModel

class AgentRun(BaseModel):

    question: str

    retrieval_result: Optional[RetrievalResult] = None

    schema_context: Optional[SchemaContext] = None

    generated_sql: Optional[SQLCandidate] = None      
    
    execution_result: Optional[ExecutionResult] = None

    answer: Optional[AnalystAnswer] = None

    error: Optional[str] = None

    success: bool = False


class BenchmarkQuestion(BaseModel):

    id: str

    question: str