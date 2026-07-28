from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class LimitRule(ValidationRule):

    MAX_LIMIT = 10000

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        limit = context.ast.args.get("limit")

        if limit is None:
            return issues

        expression = limit.expression

        #
        # LIMIT must be a numeric literal.
        #
        if not isinstance(expression, exp.Literal) or not expression.is_int:

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_LIMIT,
                    severity=ValidationSeverity.ERROR,
                    message="LIMIT must be a positive integer.",
                    location=expression.sql() if expression else "LIMIT",
                )
            )

            return issues

        value = int(expression.this)

        #
        # LIMIT must be positive.
        #
        if value <= 0:

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_LIMIT,
                    severity=ValidationSeverity.ERROR,
                    message="LIMIT must be greater than zero.",
                    location=str(value),
                )
            )

            return issues

        #
        # Prevent excessively large limits.
        #
        if value > self.MAX_LIMIT:

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_LIMIT,
                    severity=ValidationSeverity.WARNING,
                    message=(
                        f"LIMIT {value} is very large. "
                        f"Consider using a value below {self.MAX_LIMIT}."
                    ),
                    location=str(value),
                )
            )

        return issues