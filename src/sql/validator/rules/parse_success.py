from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class ParseSuccessRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is not None:
            return []

        return [
            ValidationIssue(
                issue_type=ValidationIssueType.SQL_SYNTAX_ERROR,
                severity=ValidationSeverity.ERROR,
                message="SQL could not be parsed.",
            )
        ]