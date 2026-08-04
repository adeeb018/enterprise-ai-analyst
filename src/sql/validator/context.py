from dataclasses import dataclass

from sqlglot import exp

from src.graph.schema_graph import SchemaGraph
from src.sql.generator.models import SchemaContext
from src.sql.models import SQLCandidate


@dataclass
class ValidationContext:
    candidate: SQLCandidate
    schema_context: SchemaContext
    graph: SchemaGraph
    ast: exp.Expression | None = None