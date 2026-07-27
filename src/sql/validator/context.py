from dataclasses import dataclass

from sqlglot import exp

from src.sql.generator.models import SchemaContext
from src.sql.models import SQLCandidate


@dataclass
class ValidationContext:
    candidate: SQLCandidate
    schema_context: SchemaContext
    ast: exp.Expression | None = None