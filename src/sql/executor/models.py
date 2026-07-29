from dataclasses import dataclass


@dataclass
class ExecutionResult:

    sql: str

    columns: list[str]

    rows: list[tuple]

    row_count: int

    execution_time_ms: float