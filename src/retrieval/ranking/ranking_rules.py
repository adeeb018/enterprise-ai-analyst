from abc import ABC, abstractmethod
import re

from src.graph.graph_models import TableRole
from src.retrieval.ranking.ranking_models import (
    RankingScore,
    RankedTable,
)


class BaseRankingRule(ABC):

    @abstractmethod
    def score(
        self,
        table: RankedTable,
        query: str
    ) -> RankingScore:
        ...
        
class SemanticScoreRule(BaseRankingRule):

    def score(
    self,
    table: RankedTable,
    query: str
    ) -> RankingScore:

        semantic = (
            table.node.retrieval_score
            or 0.0
        )

        return RankingScore(
            score=semantic,
            evidence=[
                f"Semantic Retrieval ({semantic:.3f})"
            ],
        )
    
class DistanceRule(BaseRankingRule):

    def score(self, table: RankedTable, query: str) -> RankingScore:

        distance = table.node.distance
        role = getattr(table.node.node, "role", TableRole.FACT)
        
        if distance == 0:
            return RankingScore(score=0.0, evidence=[])
            
        # Lenient penalty for 1-hop fact/dimension tables
        if distance == 1 and role in [TableRole.FACT, TableRole.DIMENSION]:
            return RankingScore(score=-0.02, evidence=[f"Graph distance {distance} (Lenient for {role})"])
            
        penalty = -0.08 * distance
        return RankingScore(score=penalty, evidence=[f"Graph distance {distance} penalty ({penalty})"])
    
# class TableRoleRule(BaseRankingRule):
#     """
#     Adjusts scores based on whether a table is a dictionary/lookup table 
#     or a core fact/dimension table.
#     """
#     LOOKUP_PENALTY = -0.15
#     FACT_BONUS = 0.10

#     def score(self, table: RankedTable, query: str) -> RankingScore:
#         # Safely access role through the nested GraphNode: table.node.node.role
#         graph_node = getattr(table.node, "node", None)
#         role = getattr(graph_node, "role", TableRole.FACT)
        
#         if role == TableRole.LOOKUP:
#             return RankingScore(
#                 score=self.LOOKUP_PENALTY,
#                 evidence=["Lookup table supporting role (-0.15)"]
#             )
#         elif role in [TableRole.FACT, TableRole.DIMENSION]:
#             return RankingScore(
#                 score=self.FACT_BONUS,
#                 evidence=["Fact/Dimension primary table (+0.10)"]
#             )
            
#         return RankingScore(score=0.0, evidence=[])

LOOKUP_INTENT_PATTERNS = [
    r"\blook ?up\b",
    r"\bdescription\b",
    r"\bdefinition\b",
    r"\bmeaning\b",
    r"\bwhat (is|are) the (code|title|description|meaning)\b",
    r"\bcode for\b",
]

def detect_lookup_intent(query: str) -> bool:
    q = query.lower()
    return any(re.search(p, q) for p in LOOKUP_INTENT_PATTERNS)


class TableRoleRule(BaseRankingRule):
    LOOKUP_PENALTY = -0.15
    LOOKUP_BONUS = 0.15
    FACT_BONUS = 0.10

    def score(self, table: RankedTable, query: str) -> RankingScore:
        # Access the underlying GraphNode from ExpandedNode
        graph_node = getattr(table.node, "node", None)
        role = getattr(graph_node, "role", TableRole.FACT)

        if role == TableRole.LOOKUP:
            # Use pre-computed lookup strength if available, default to 1.0
            strength = getattr(graph_node, "lookup_strength", 1.0)
            is_lookup_query = detect_lookup_intent(query)
            
            base = self.LOOKUP_BONUS if is_lookup_query else self.LOOKUP_PENALTY
            adjusted = base * strength
            
            label = "Lookup intent matched" if is_lookup_query else "Supporting role"
            return RankingScore(score=adjusted, evidence=[f"{label} ({adjusted:+.3f})"])

        if role in (TableRole.FACT, TableRole.DIMENSION):
            return RankingScore(score=self.FACT_BONUS, evidence=["Fact/dimension table (+0.10)"])

        return RankingScore(score=0.0, evidence=[])