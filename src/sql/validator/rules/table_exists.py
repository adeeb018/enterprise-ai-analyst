from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class TableExistsRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        available_tables = {
            f"{table.schema_name}.{table.table}"
            for table in context.schema_context.tables
        }

        for table in context.ast.find_all(exp.Table):

            table_name = table.name
            schema_name = table.db

            full_name = (
                f"{schema_name}.{table_name}"
                if schema_name
                else table_name
            )

            if full_name in available_tables:
                continue

            suggestion = self._find_closest(
                full_name,
                available_tables,
            )

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.UNKNOWN_TABLE,
                    severity=ValidationSeverity.ERROR,
                    message=f"Unknown table '{full_name}'.",
                    location=full_name,
                    suggestion=suggestion,
                )
            )

        return issues

    @staticmethod
    def _find_closest(
        table_name: str,
        candidates: set[str],
    ) -> str | None:

        from difflib import get_close_matches

        matches = get_close_matches(
            table_name,
            candidates,
            n=1,
            cutoff=0.6,
        )

        return matches[0] if matches else None