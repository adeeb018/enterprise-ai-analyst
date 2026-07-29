from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


def _match_columns(edge_col, query_col: str) -> bool:
    """Helper to check if query_col matches a string or is part of a list of columns."""
    if isinstance(edge_col, list):
        return query_col in edge_col
    return edge_col == query_col


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

                valid = False

                #
                # Check left table edges
                #
                left_node = context.graph.get_node(left_table)

                if left_node is not None:

                    #
                    # Outgoing relationships
                    #
                    for edge in left_node.outgoing:

                        if (
                            edge.target == right_table
                            and _match_columns(edge.source_column, left.name)
                            and _match_columns(edge.target_column, right.name)
                        ):
                            valid = True
                            break

                    #
                    # Incoming relationships
                    #
                    if not valid:

                        for edge in left_node.incoming:

                            if (
                                edge.source == right_table
                                and _match_columns(edge.target_column, left.name)
                                and _match_columns(edge.source_column, right.name)
                            ):
                                valid = True
                                break

                #
                # Check opposite direction if needed
                #
                if not valid:

                    right_node = context.graph.get_node(right_table)

                    if right_node is not None:

                        #
                        # Outgoing relationships
                        #
                        for edge in right_node.outgoing:

                            if (
                                edge.target == left_table
                                and _match_columns(edge.source_column, right.name)
                                and _match_columns(edge.target_column, left.name)
                            ):
                                valid = True
                                break

                        #
                        # Incoming relationships
                        #
                        if not valid:

                            for edge in right_node.incoming:

                                if (
                                    edge.source == left_table
                                    and _match_columns(edge.target_column, right.name)
                                    and _match_columns(edge.source_column, left.name)
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