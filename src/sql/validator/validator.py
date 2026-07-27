from sqlglot import parse_one
from sqlglot.errors import ParseError
from src.sql.generator.models import SchemaContext
from src.sql.models import SQLCandidate, ValidationReport
from src.sql.validator.rules.alias import AliasRule
from src.sql.validator.rules.column_exists import ColumnExistsRule
from src.sql.validator.rules.table_exists import TableExistsRule

from .context import ValidationContext
from .rules.dangerous_statement import DangerousStatementRule
from .rules.empty_sql import EmptySQLRule
from .rules.from_rule import FromRule
from .rules.multiple_statement import MultipleStatementRule
from .rules.parse_success import ParseSuccessRule
from .rules.select_rule import SelectRule


class SQLValidator:

    def __init__(self):

        self.rules = [
            EmptySQLRule(),
            DangerousStatementRule(),
            MultipleStatementRule(),
            SelectRule(),
            FromRule(),
            ParseSuccessRule(),
            TableExistsRule(),
            ColumnExistsRule(),
            AliasRule(),
        ]

    def validate(
        self,
        candidate: SQLCandidate,
        schema_context: SchemaContext,
    ) -> ValidationReport:

        report = ValidationReport(
            validator_name="SQLValidator"
        )

        context = ValidationContext(
            candidate=candidate,
            schema_context=schema_context,
        )

        try:
            context.ast = parse_one(candidate.sql)

        except ParseError:
            context.ast = None

        for rule in self.rules:

            report.issues.extend(
                rule.validate(context)
            )

        return report