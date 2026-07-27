from enum import Enum


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssueType(str, Enum):
    MISSING_TABLE = "missing_table"
    MISSING_COLUMN = "missing_column"
    INVALID_JOIN = "invalid_join"
    INVALID_AGGREGATION = "invalid_aggregation"
    INVALID_FUNCTION = "invalid_function"
    INVALID_SYNTAX = "invalid_syntax"
    UNKNOWN = "unknown"
    SQL_SYNTAX_ERROR = "sql_syntax_error"
    UNKNOWN_COLUMN = "unknown_column"
    UNKNOWN_ALIAS = "unknown_alias"
    DUPLICATE_ALIAS = "duplicate_alias"
    UNKNOWN_TABLE = "unknown_table_name"
    EMPTY_SQL = "no_sql_generated"
    MISSING_SELECT = "no_select_statement"
    MULTIPLE_STATEMENTS = "multiple_statements"
    MISSING_FROM = "no_from_in_sql"
    DANGEROUS_STATEMENT = "dangerous_statement"


class SQLStatus(str, Enum):
    GENERATED = "generated"
    VALIDATED = "validated"
    REPAIRED = "repaired"
    EXECUTED = "executed"
    FAILED = "failed"


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"