from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class OnClauseRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        #
        # Build alias lookup
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
        # Validate every JOIN
        #
        for join in context.ast.find_all(exp.Join):

            on_clause = join.args.get("on")

            if on_clause is None:
                continue

            #
            # Find equality predicates
            #
            for predicate in on_clause.find_all(exp.EQ):

                left = predicate.left
                right = predicate.right

                #
                # We only validate column = column joins.
                #
                if not (
                    isinstance(left, exp.Column)
                    and isinstance(right, exp.Column)
                ):
                    continue

                if not left.table or not right.table:
                    continue

                left_table = alias_lookup.get(left.table)
                right_table = alias_lookup.get(right.table)

                if left_table is None or right_table is None:
                    continue

                #
                # Same table comparisons are ignored.
                #
                if left_table == right_table:
                    continue

                #
                # Verify graph relationship
                #
                if (
                    not context.graph.has_edge(left_table, right_table)
                    and not context.graph.has_edge(right_table, left_table)
                ):

                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationIssueType.INVALID_ON_CLAUSE,
                            severity=ValidationSeverity.ERROR,
                            message=(
                                f"No relationship exists between "
                                f"'{left_table}' and '{right_table}'."
                            ),
                            location=predicate.sql(),
                        )
                    )

                    continue

                #
                # Validate join columns
                #
                valid = False

                for edge in context.graph.get_neighbors(left_table):

                    if edge.target != right_table:
                        continue

                    if (
                        edge.source_column == left.name
                        and edge.target_column == right.name
                    ):
                        valid = True
                        break

                if not valid:

                    for edge in context.graph.get_neighbors(right_table):

                        if edge.target != left_table:
                            continue

                        if (
                            edge.source_column == right.name
                            and edge.target_column == left.name
                        ):
                            valid = True
                            break

                if not valid:

                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationIssueType.INVALID_ON_CLAUSE,
                            severity=ValidationSeverity.ERROR,
                            message=(
                                "JOIN condition does not match the schema "
                                "relationship."
                            ),
                            location=predicate.sql(),
                        )
                    )

        return issues