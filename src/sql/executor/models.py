from pydantic import BaseModel
from typing import Any


class ExecutionResult(BaseModel):

    sql: str

    columns: list[str]

    rows: list[list[Any]]

    row_count: int

    execution_time_ms: float