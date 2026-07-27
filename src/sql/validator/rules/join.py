from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class JoinRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        #
        # Build alias -> fully qualified table lookup
        #
        alias_lookup: dict[str, str] = {}

        for table in context.ast.find_all(exp.Table):

            table_id = (
                f"{table.db}.{table.name}"
                if table.db
                else table.name
            )

            alias = table.alias or table.name

            alias_lookup[alias] = table_id

        #
        # Get the starting table from FROM
        #
        from_clause = context.ast.args.get("from")

        if from_clause is None:
            return issues

        if not isinstance(from_clause.this, exp.Table):
            return issues

        current_table = alias_lookup.get(
            from_clause.this.alias or from_clause.this.name
        )

        if current_table is None:
            return issues

        #
        # Validate every JOIN
        #
        for join in context.ast.args.get("joins", []):

            if not isinstance(join.this, exp.Table):
                continue

            joined_table = alias_lookup.get(
                join.this.alias or join.this.name
            )

            if joined_table is None:
                continue

            #
            # Check whether a relationship exists in either direction.
            #
            connected = (
                context.graph.has_edge(current_table, joined_table)
                or context.graph.has_edge(joined_table, current_table)
            )

            if not connected:

                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.INVALID_JOIN,
                        severity=ValidationSeverity.ERROR,
                        message=(
                            f"No relationship exists between "
                            f"'{current_table}' and '{joined_table}'."
                        ),
                        location=f"{current_table} -> {joined_table}",
                    )
                )

            #
            # Continue from the newly joined table.
            #
            current_table = joined_table

        return issues