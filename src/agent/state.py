from typing import TypedDict

from src.evaluation.models import AgentRun
from src.pipeline.pipeline_models import RetrievalResult
from src.sql.generator.models import SchemaContext
from src.sql.models import ExecutionResult, SQLCandidate

from typing import NotRequired, TypedDict

class AnalystState(TypedDict):
    question: str
    retrieval_result: NotRequired[RetrievalResult]
    schema_context: NotRequired[SchemaContext]
    candidate: NotRequired[SQLCandidate]
    execution_result: NotRequired[ExecutionResult]
    run: NotRequired[AgentRun]