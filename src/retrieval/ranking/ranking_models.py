from dataclasses import dataclass, field

from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retrieval_models import ExpandedNode


@dataclass
class RankedTable:
    node: ExpandedNode
    score: float = 0.0
    evidence: list[str] = field(default_factory=list)


@dataclass
class RankedContext:
    retrieved_tables: list[RetrievedChunk]
    ranked_tables: list[RankedTable]

from dataclasses import dataclass, field


@dataclass
class RankingScore:
    score: float
    evidence: list[str]