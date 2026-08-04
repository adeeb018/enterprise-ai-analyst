class SQLError(Exception):
    """
    Base exception for all SQL subsystem errors.
    """

    pass


class SQLGenerationError(SQLError):
    """
    Raised when a valid SQL query cannot be generated,
    even after repair attempts.
    """

    pass


class SQLValidationError(SQLError):
    """
    Raised when the SQL validator encounters an unexpected
    internal validation error.
    """

    pass


class SQLExecutionError(SQLError):
    """
    Raised when execution of a valid SQL query fails.
    """

    pass


class SQLRepairError(SQLError):
    """
    Raised when the repair subsystem fails unexpectedly.
    """

    pass