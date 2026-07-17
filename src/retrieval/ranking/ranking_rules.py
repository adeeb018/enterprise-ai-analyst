from abc import ABC, abstractmethod

from src.retrieval.ranking.ranking_models import (
    RankingScore,
    RankedTable,
)


class BaseRankingRule(ABC):

    @abstractmethod
    def score(
        self,
        table: RankedTable,
    ) -> RankingScore:
        ...
        
class SemanticScoreRule(BaseRankingRule):

    def score(
    self,
    table: RankedTable,
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

    def score(
        self,
        table: RankedTable,
    ) -> RankingScore:

        distance = table.node.distance
    
        penalty = -0.05 * distance  # small nudge, not a dominant factor
        return RankingScore(
            score=penalty,
            evidence=[f"Graph Distance ({distance})"],
        )