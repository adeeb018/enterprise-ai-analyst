from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class OrderByRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        #
        # Build table alias lookup
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
        # Build SELECT aliases
        #
        select_aliases: set[str] = set()

        select = context.ast.find(exp.Select)

        if select is not None:

            for expression in select.expressions:

                if expression.alias:
                    select_aliases.add(expression.alias)

        #
        # ORDER BY clause
        #
        order = context.ast.args.get("order")

        if order is None:
            return issues

        for ordered in order.expressions:

            expression = ordered.this

            #
            # ORDER BY alias
            #
            if isinstance(expression, exp.Column):

                #
                # ORDER BY total_count
                #
                if (
                    expression.table == ""
                    and expression.name in select_aliases
                ):
                    continue

                #
                # Qualified column
                #
                if expression.table:

                    table_id = alias_lookup.get(expression.table)

                    if table_id is None:
                        continue

                    node = context.graph.get_node(table_id)

                    if node is None:
                        continue

                    exists = any(
                        column.name == expression.name
                        for column in node.table_info.columns
                    )

                    if not exists:

                        issues.append(
                            ValidationIssue(
                                issue_type=ValidationIssueType.UNKNOWN_COLUMN,
                                severity=ValidationSeverity.ERROR,
                                message=(
                                    f"Column '{expression.name}' "
                                    f"does not exist in '{table_id}'."
                                ),
                                location=expression.sql(),
                            )
                        )

                #
                # Unqualified column
                #
                else:

                    found = False

                    for table_id in alias_lookup.values():

                        node = context.graph.get_node(table_id)

                        if node is None:
                            continue

                        if any(
                            column.name == expression.name
                            for column in node.table_info.columns
                        ):
                            found = True
                            break

                    if not found:

                        issues.append(
                            ValidationIssue(
                                issue_type=ValidationIssueType.UNKNOWN_COLUMN,
                                severity=ValidationSeverity.ERROR,
                                message=(
                                    f"Unknown ORDER BY column "
                                    f"'{expression.name}'."
                                ),
                                location=expression.sql(),
                            )
                        )

        return issues