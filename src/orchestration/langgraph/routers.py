from src.agent.state import AnalystState
from src.sql.enums import  ValidationIssueType

RETRIEVE_MORE_SCHEMA_ISSUES = {
    ValidationIssueType.UNKNOWN_TABLE,
    ValidationIssueType.UNKNOWN_COLUMN,

}

def validation_router(state: AnalystState) -> str:
    report = state.get("validation_report")
    # If valid, proceed to execution
    if report.is_valid:
        return "execute_sql"

    issue_types = {
        issue.issue_type
        for issue in report.issues
    }

    if issue_types & RETRIEVE_MORE_SCHEMA_ISSUES:
        return "retrieve_more_schema"
    
    repair_count = state.get(
        "repair_count",
        0,
    )

    if repair_count >= 1:
        return "max_retries_exceeded"

    return "repair_candidate" # Fallback safety guard