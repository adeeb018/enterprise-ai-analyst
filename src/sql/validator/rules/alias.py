from sqlglot import exp

from src.sql.models import (
    ValidationIssue,
    ValidationIssueType,
    ValidationSeverity,
)

from ..base import ValidationRule
from ..context import ValidationContext


class AliasRule(ValidationRule):

    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:

        if context.ast is None:
            return []

        issues: list[ValidationIssue] = []

        alias_lookup: dict[str, str] = {}

        #
        # Collect aliases and detect duplicates
        #
        for table in context.ast.find_all(exp.Table):

            alias = table.alias

            if not alias:
                continue

            table_name = (
                f"{table.db}.{table.name}"
                if table.db
                else table.name
            )

            if alias in alias_lookup:

                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.DUPLICATE_ALIAS,
                        severity=ValidationSeverity.ERROR,
                        message=f"Duplicate alias '{alias}'.",
                        location=alias,
                    )
                )

                continue

            alias_lookup[alias] = table_name

        #
        # Validate alias references
        #
        for column in context.ast.find_all(exp.Column):

            alias = column.table

            if not alias:
                continue

            #
            # Valid alias
            #
            if alias in alias_lookup:
                continue

            #
            # Also allow direct table references
            #
            is_table_name = any(
                alias == table.name
                for table in context.ast.find_all(exp.Table)
            )

            if is_table_name:
                continue

            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.UNKNOWN_ALIAS,
                    severity=ValidationSeverity.ERROR,
                    message=f"Unknown alias '{alias}'.",
                    location=alias,
                )
            )

        return issues