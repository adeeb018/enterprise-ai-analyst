from dataclasses import dataclass, field

from src.ingestion.schema_models import TableInfo

from enum import Enum

class TableRole(str, Enum):
    FACT = "fact"            # Transactional tables (has foreign keys out, holds data)
    LOOKUP = "lookup"        # Dictionary/code tables (high lookup strength, few FKs)
    DIMENSION = "dimension"  # Core entity tables (like patients, admissions)


@dataclass
class GraphEdge:
    source: str
    target: str

    source_column: str | None = None
    target_column: str | None = None

    relationship: str = "foreign_key"

    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)


@dataclass
class GraphNode:
    id: str
    table_info: TableInfo
    role: TableRole = TableRole.FACT
    incoming: list[GraphEdge] = field(default_factory=list)
    outgoing: list[GraphEdge] = field(default_factory=list)
