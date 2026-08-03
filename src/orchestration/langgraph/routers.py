from src.agent.state import AnalystState
from src.sql.enums import ValidationDecision

def validation_router(state: AnalystState) -> str:
    decision = state.get("validation_decision")
    # If valid, proceed to execution
    if decision == ValidationDecision.VALID:
        return "execute_sql"

    # Enforce max repair attempts limit
    max_repairs = 1
    current_repairs = state.get("repair_count", 0)
    print(current_repairs)

    if current_repairs >= max_repairs:
        return "max_retries_exceeded" # Or route directly to build_run with an error

    # Otherwise, follow the repair decision path
    if decision == ValidationDecision.REPAIR_SQL:
        return "repair_candidate"

    return "max_retries_exceeded" # Fallback safety guard