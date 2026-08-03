from src.sql.enums import ValidationDecision
from src.sql.models import ValidationReport


class ValidationDecisionBuilder:

    def build(
        self,
        report: ValidationReport,
    ) -> ValidationDecision:
        if report.is_valid:
            return ValidationDecision.VALID

        return ValidationDecision.REPAIR_SQL