from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)
from src.sql.validator.context import ValidationContext

from ..base import ValidationRule


class FromRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        sql = context.candidate.sql.upper()

        if "FROM" in sql:
            return []

        return [
            ValidationIssue(
                issue_type=ValidationIssueType.MISSING_FROM,
                severity=ValidationSeverity.ERROR,
                message="Missing FROM clause.",
            )
        ]