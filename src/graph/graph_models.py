from dataclasses import dataclass, field


@dataclass
class GraphEdge:
    source: str
    target: str

    source_column: str
    target_column: str

    relationship: str = "foreign_key"


@dataclass
class GraphNode:
    id: str

    schema_name: str
    table: str

    columns: list[str]

    primary_keys: list[str]

    incoming: list[GraphEdge] = field(default_factory=list)

    outgoing: list[GraphEdge] = field(default_factory=list)

@dataclass
class ExpandedNode:
    node: GraphNode
    distance: int
    parent: str |None = None
    via_edge: GraphEdge | None = None


@dataclass
class TraversalState:
    distance: int
    parent: str | None
    edge: GraphEdge | None