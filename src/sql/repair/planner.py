from src.graph.schema_graph import SchemaGraph
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
        graph: SchemaGraph = None
    ) -> RepairPlan:

        instructions: list[RepairInstruction] = []

        for issue in report.issues:

            suggestion = issue.suggestion

            if graph and issue.issue_type.value == "invalid_on_clause":
                # Assuming your issue metadata contains table names, or we fallback gracefully
                table_a = issue.metadata.get("table_a")
                table_b = issue.metadata.get("table_b")

                if table_a and table_b:
                    try:
                        path = graph.find_shortest_path(table_a, table_b)
                        if path:
                            path_str = " -> ".join(path)
                            suggestion = (
                                f"No direct relationship exists between {table_a} and {table_b}. "
                                f"You must join them using the valid schema path: [{path_str}]."
                            )
                    except Exception:
                        pass  # Fallback to original suggestion if pathfinding fails

            instructions.append(
                RepairInstruction(
                    issue_type=issue.issue_type,
                    message=issue.message,
                    location=issue.location,
                    suggestion=suggestion,
                )
            )

        return RepairPlan(
            question=question,
            original_sql=sql,
            validation_report=report,
            instructions=instructions,
        )