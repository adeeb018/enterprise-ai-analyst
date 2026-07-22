from src.retrieval.ranking.ranking_engine import RankingEngine
from src.retrieval.ranking.ranking_models import (
    RankedContext,
    RankedTable,
)
from src.retrieval.retrieval_models import ExpandedContext


class ContextRanker:

    def __init__(self):

        self.engine = RankingEngine()

    def rank(
        self,
        context: ExpandedContext,
        query: str
    ) -> RankedContext:

        ranked_tables = []

        #
        # Convert ExpandedNode -> RankedTable
        #
        for node in context.expanded_tables:

            ranked_tables.append(
                RankedTable(
                    node=node,
                )
            )

        #
        # Apply scoring rules
        #
        ranked_tables = self.engine.rank(
            ranked_tables,
            query
        )

        return RankedContext(
            retrieved_tables=context.retrieved_tables,
            ranked_tables=ranked_tables,
        )