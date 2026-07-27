from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)
from src.sql.validator.context import ValidationContext

from ..base import ValidationRule


class SelectRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        sql = context.candidate.sql.upper()

        if "SELECT" in sql:
            return []

        return [
            ValidationIssue(
                issue_type=ValidationIssueType.MISSING_SELECT,
                severity=ValidationSeverity.ERROR,
                message="Missing SELECT statement.",
            )
        ]