from pydantic import BaseModel

from src.sql.models import ValidationReport


class RepairAttempt(BaseModel):
    """
    Records a single repair attempt.
    """

    attempt: int
    sql: str
    validation_report: ValidationReport


class RepairResult(BaseModel):
    """
    Final output of the repair engine.
    """

    success: bool

    sql: str

    attempts: int

    history: list[RepairAttempt]