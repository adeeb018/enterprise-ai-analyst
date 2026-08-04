from pydantic import BaseModel

from src.sql.models import (
    ValidationIssueType,
    ValidationReport,
)


class RepairInstruction(BaseModel):
    """
    A single repair action derived from a validation issue.
    """

    issue_type: ValidationIssueType
    message: str
    location: str | None = None
    suggestion: str | None = None


class RepairPlan(BaseModel):
    """
    Structured representation of everything needed
    to repair a SQL query.
    """

    question: str
    original_sql: str
    validation_report: ValidationReport
    instructions: list[RepairInstruction]