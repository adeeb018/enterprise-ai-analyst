from src.sql.models import ValidationReport
from src.sql.repair.models import RepairInstruction, RepairPlan


class RepairPlanner:
    """
    Converts a ValidationReport into a structured RepairPlan.
    """

    def create_plan(
        self,
        *,
        question: str,
        sql: str,
        report: ValidationReport,
    ) -> RepairPlan:

        instructions: list[RepairInstruction] = []

        for issue in report.issues:

            instructions.append(
                RepairInstruction(
                    issue_type=issue.issue_type,
                    message=issue.message,
                    location=issue.location,
                    suggestion=issue.suggestion,
                )
            )

        return RepairPlan(
            question=question,
            original_sql=sql,
            validation_report=report,
            instructions=instructions,
        )