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
    INVALID_ALIAS = "invalid_alias"
    INVALID_FUNCTION = "invalid_function"
    INVALID_SYNTAX = "invalid_syntax"
    UNKNOWN = "unknown"


class SQLStatus(str, Enum):
    GENERATED = "generated"
    VALIDATED = "validated"
    REPAIRED = "repaired"
    EXECUTED = "executed"
    FAILED = "failed"


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"