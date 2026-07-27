from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)
from src.sql.validator.context import ValidationContext

from ..base import ValidationRule


class EmptySQLRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.candidate.sql.strip():
            return []

        return [
            ValidationIssue(
                issue_type=ValidationIssueType.EMPTY_SQL,
                severity=ValidationSeverity.ERROR,
                message="Generated SQL is empty.",
            )
        ]