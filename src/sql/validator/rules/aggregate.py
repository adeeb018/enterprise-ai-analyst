from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class AggregateRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        #
        # GROUP BY expressions
        #
        group = context.ast.args.get("group")

        group_expressions: set[str] = set()

        if group is not None:
            for expression in group.expressions:
                group_expressions.add(expression.sql())

        #
        # SELECT expressions
        #
        select = context.ast.find(exp.Select)

        if select is None:
            return issues

        #
        # Determine whether the query contains
        # at least one aggregate function.
        #
        has_aggregate = any(
            expression.find(exp.AggFunc)
            for expression in select.expressions
        )

        if not has_aggregate:
            return issues

        #
        # Validate every selected expression.
        #
        for expression in select.expressions:

            #
            # Ignore aggregate expressions.
            #
            if expression.find(exp.AggFunc):
                continue

            sql = expression.sql()

            if sql in group_expressions:
                continue

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_GROUP_BY,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"'{sql}' must appear in the GROUP BY clause "
                        "or be used in an aggregate function."
                    ),
                    location=sql,
                )
            )

        return issues