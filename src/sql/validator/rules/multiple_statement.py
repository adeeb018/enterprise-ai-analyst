from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)
from src.sql.validator.context import ValidationContext

from ..base import ValidationRule


class MultipleStatementRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        statements = [
            s.strip()
            for s in context.candidate.sql.split(";")
            if s.strip()
        ]

        if len(statements) <= 1:
            return []

        return [
            ValidationIssue(
                issue_type=ValidationIssueType.MULTIPLE_STATEMENTS,
                severity=ValidationSeverity.ERROR,
                message="Multiple SQL statements detected.",
            )
        ]