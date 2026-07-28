from difflib import get_close_matches

from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class FunctionRule(ValidationRule):

    #
    # Common SQL functions an LLM is expected to use.
    #
    VALID_FUNCTIONS = {
        # Aggregates
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",

        # String
        "LOWER",
        "UPPER",
        "TRIM",
        "LTRIM",
        "RTRIM",
        "LENGTH",
        "SUBSTRING",
        "CONCAT",
        "REPLACE",

        # Date / Time
        "DATE_TRUNC",
        "DATE_PART",
        "EXTRACT",
        "AGE",
        "NOW",
        "CURRENT_DATE",
        "CURRENT_TIME",

        # Null handling
        "COALESCE",
        "NULLIF",

        # Numeric
        "ROUND",
        "CEIL",
        "CEILING",
        "FLOOR",
        "ABS",

        # Conditional
        "CASE",

        # Misc
        "CAST",
    }

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        for function in context.ast.find_all(exp.Func):

            #
            # sqlglot stores the function class name.
            #
            name = function.sql_name().upper()

            #
            # Unknown function
            #
            if name not in self.VALID_FUNCTIONS:

                suggestion = get_close_matches(
                    name,
                    self.VALID_FUNCTIONS,
                    n=1,
                )

                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.UNKNOWN_FUNCTION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Unknown SQL function '{name}'.",
                        location=function.sql(),
                        suggestion=(
                            f"Did you mean '{suggestion[0]}'?"
                            if suggestion
                            else None
                        ),
                    )
                )

        return issues