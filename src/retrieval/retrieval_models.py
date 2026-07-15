from pydantic.dataclasses import dataclass

from src.graph.graph_models import GraphEdge, GraphNode
from src.retrieval.query_models import RetrievedChunk


@dataclass
class ExpandedNode:
    node: GraphNode
    distance: int
    source_seed: str 

    retrieval_score: float | None = None
    parent: str |None = None
    via_edge: GraphEdge | None = None


@dataclass
class TraversalState:
    table_id: str
    distance: int
    source_seed: str

    parent: str | None
    via_edge: GraphEdge | None


@dataclass
class ExpandedContext:
    retrieved_tables: list[RetrievedChunk]
    expanded_tables: list[ExpandedNode]