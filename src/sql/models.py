from pydantic import BaseModel, Field

from src.pipeline.pipeline_models import RetrievalResult
from src.planner.planner_models import QueryPlan
from src.sql.enums import ExecutionStatus, SQLStatus, ValidationIssueType, ValidationSeverity


class ValidationIssue(BaseModel):
    """
    Represents a single validation problem detected in a SQL query.
    """
    issue_type: ValidationIssueType
    severity: ValidationSeverity = ValidationSeverity.ERROR
    message: str
    location: str | None = None
    suggestion: str | None = None


class SQLPlan(BaseModel):
    """
    Logical representation of the SQL query before SQL generation.
    """
    objective: str
    tables: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    joins: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)
    group_by: list[str] = Field(default_factory=list)
    order_by: list[str] = Field(default_factory=list)
    limit: int | None = None


class SQLCandidate(BaseModel):
    """
    Represents a single generated SQL query.
    """

    sql: str
    explanation: str | None = None
    status: SQLStatus = SQLStatus.GENERATED
    # confidence: float | None = Field(
    #     default=None,
    #     ge=0.0,
    #     le=1.0,
    # )


class ValidationReport(BaseModel):
    """
    Result of validating a SQL query.
    """
    issues: list[ValidationIssue] = Field(default_factory=list)
    validator_name: str | None = None

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity.value == "error"
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity.value == "error"
            for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity.value == "warning"
            for issue in self.issues
        )
    

class ExecutionResult(BaseModel):
    """
    Result produced after executing a SQL query.
    """

    status: ExecutionStatus
    rows: list[dict] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    execution_time_ms: float | None = None
    error: str | None = None

    @property
    def row_count(self) -> int:
        return len(self.rows)
    

class AnswerResult(BaseModel):
    """
    Final response generated for the user.
    """
    answer: str
    reasoning: str | None = None
    

class SQLAgentState(BaseModel):
    """
    Shared state for a single SQL generation request.
    """

    question: str
    query_plan: QueryPlan
    retrieval_result: RetrievalResult
    sql_candidates: list[SQLCandidate] = []
    validation_reports: list[ValidationReport] = []
    execution_result: ExecutionResult | None = None
    answer_result: AnswerResult | None = None