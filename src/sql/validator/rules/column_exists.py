from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class ColumnExistsRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        #
        # Build lookup
        #
        table_lookup = {
            f"{table.schema_name}.{table.table}": table
            for table in context.schema_context.tables
        }

        #
        # Build alias lookup
        #
        alias_lookup: dict[str, str] = {}

        for table in context.ast.find_all(exp.Table):

            table_name = table.name
            schema_name = table.db

            full_name = (
                f"{schema_name}.{table_name}"
                if schema_name
                else table_name
            )

            alias = table.alias

            if alias:
                alias_lookup[alias] = full_name

        #
        # Validate columns
        #
        for column in context.ast.find_all(exp.Column):
            if isinstance(column.this, exp.Star) or column.name == "*":
                continue

            column_name = column.name
            table_alias = column.table

            #
            # Ignore unqualified columns for now.
            # We'll support them later.
            #
            if not table_alias:
                continue

            if table_alias not in alias_lookup:
                continue

            table_name = alias_lookup[table_alias]

            table_info = table_lookup.get(table_name)

            if table_info is None:
                continue

            valid_columns = {
                c.name
                for c in table_info.columns
            }

            if column_name in valid_columns:
                continue

            suggestion = self._find_closest(
                column_name,
                valid_columns,
            )

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.UNKNOWN_COLUMN,
                    severity=ValidationSeverity.ERROR,
                    message=f"Unknown column '{column_name}'.",
                    location=f"{table_name}.{column_name}",
                    suggestion=suggestion,
                )
            )

        return issues

    @staticmethod
    def _find_closest(
        column: str,
        candidates: set[str],
    ) -> str | None:

        from difflib import get_close_matches

        matches = get_close_matches(
            column,
            candidates,
            n=1,
            cutoff=0.6,
        )

        return matches[0] if matches else None