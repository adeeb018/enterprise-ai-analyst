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
#worked one
# class DistanceRule(BaseRankingRule):
#     def score(self, table: RankedTable, query: str) -> RankingScore:
#         distance = table.node.distance
#         role = getattr(table.node.node, "role", TableRole.FACT)
        
#         # Seed tables found directly by semantic search (distance = 0)
#         if distance == 0:
#             return RankingScore(score=0.0, evidence=[])
            
#         # 1-hop graph neighbors: MASSIVE reward because they are actual join paths!
#         if distance == 1 and role in [TableRole.FACT, TableRole.DIMENSION]:
#             return RankingScore(
#                 score=0.12, 
#                 evidence=[f"Direct graph join path (1-hop {role}) (+0.12)"]
#             )
            
#         penalty = -0.08 * distance
#         return RankingScore(score=penalty, evidence=[f"Graph distance {distance} penalty ({penalty})"])

class DistanceRule(BaseRankingRule):
    def score(self, table: RankedTable, query: str) -> RankingScore:
        distance = table.node.distance
        role = getattr(table.node.node, "role", TableRole.FACT)
        semantic = table.node.retrieval_score or 0.0
        
        # Seed tables found directly by semantic search (distance = 0)
        if distance == 0:
            return RankingScore(score=0.0, evidence=[])
            
        # 1-hop graph neighbors: Gated by semantic relevance to prevent super-hub noise
        if distance == 1 and role in [TableRole.FACT, TableRole.DIMENSION]:
            if semantic >= 0.35:
                # Scaled bonus: maxes out around +0.06 instead of a flat +0.12
                scaled_bonus = 0.02 + (semantic * 0.08)

                return RankingScore(
                    score=scaled_bonus, 
                    evidence=[f"Proportional 1-hop join path (+{scaled_bonus:.3f})"]
                )
            else:
                return RankingScore(
                    score=0.01, 
                    evidence=[f"Low-relevance 1-hop connection suppressed (+0.01)"]
                )
            
        penalty = -0.08 * distance
        return RankingScore(score=penalty, evidence=[f"Graph distance {distance} penalty ({penalty})"])

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
    def score(self, table: RankedTable, query: str) -> RankingScore:
        graph_node = table.node.node
        role = getattr(graph_node, "role", TableRole.FACT)
        semantic = table.node.retrieval_score or 0.0
        distance = table.node.distance

        if role == TableRole.LOOKUP:
            # EXCEPTION: If it's a direct semantic hit with a high score, let it in!
            if distance == 0 and semantic >= 0.60:
                return RankingScore(
                    score=0.15, 
                    evidence=[f"Direct high-confidence lookup match ({semantic:.3f}) (+0.15)"]
                )
            
            is_lookup_query = detect_lookup_intent(query)
            if not is_lookup_query:
                return RankingScore(score=-0.30, evidence=["Lookup table penalized for analytical query (-0.30)"])
            else:
                return RankingScore(score=0.25, evidence=["Lookup intent matched (+0.25)"])

        if role in (TableRole.FACT, TableRole.DIMENSION):
            boost = 0.15 + (semantic * 0.10)
            return RankingScore(score=boost, evidence=[f"Core Fact/Dimension multiplier (+{boost:.3f})"])

        return RankingScore(score=0.0, evidence=[])