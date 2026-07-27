from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)
from src.sql.validator.context import ValidationContext

from ..base import ValidationRule


class DangerousStatementRule(ValidationRule):

    DANGEROUS = {
        "DELETE",
        "DROP",
        "ALTER",
        "UPDATE",
        "INSERT",
        "TRUNCATE",
    }

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        sql = context.candidate.sql.upper()

        for keyword in self.DANGEROUS:

            if keyword in sql:

                return [
                    ValidationIssue(
                        issue_type=ValidationIssueType.DANGEROUS_STATEMENT,
                        severity=ValidationSeverity.ERROR,
                        message=f"{keyword} statements are not allowed.",
                    )
                ]

        return []