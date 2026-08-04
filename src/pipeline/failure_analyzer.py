from src.sql.enums import ValidationIssueType
from src.sql.models import ValidationReport


class FailureAnalyzer:
    """
    Extracts retrieval hints from a ValidationReport.

    Version 1:
        - UNKNOWN_TABLE
        - UNKNOWN_COLUMN

    Future:
        - INVALID_ON_CLAUSE
        - Execution failures
        - LLM-generated hints
    """

    def analyze(
        self,
        report: ValidationReport,
    ) -> list[str]:

        hints: list[str] = []

        for issue in report.issues:

            #
            # Unknown table
            #
            if issue.issue_type == ValidationIssueType.UNKNOWN_TABLE:

                hints.append(issue.location)

            #
            # Unknown column
            #
            elif issue.issue_type == ValidationIssueType.UNKNOWN_COLUMN:

                hints.append(issue.location)

        #
        # Remove duplicates
        #
        return list(dict.fromkeys(hints))