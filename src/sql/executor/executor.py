import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.sql.exceptions import SQLExecutionError
from src.sql.executor.connection import get_engine
from src.sql.executor.models import ExecutionResult
from src.sql.models import SQLCandidate


class SQLExecutor:
    """
    Executes validated SQL queries against PostgreSQL.

        SQLCandidate
              ↓
        PostgreSQL
              ↓
       ExecutionResult
    """

    def __init__(self):
        self._engine = get_engine()

    def execute(
        self,
        candidate: SQLCandidate,
    ) -> ExecutionResult:

        start = time.perf_counter()

        try:
            with self._engine.connect() as connection:

                result = connection.execute(text(candidate.sql))

                rows = [list(row) for row in result.fetchall()]

                columns = list(result.keys())

        except SQLAlchemyError as e:
            raise SQLExecutionError(str(e)) from e

        execution_time_ms = (time.perf_counter() - start) * 1000

        return ExecutionResult(
            sql=candidate.sql,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=execution_time_ms,
        )