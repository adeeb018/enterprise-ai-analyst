from src.retrieval.ranking.ranking_models import (
    RankedTable,
)
from src.retrieval.ranking.ranking_rules import (
    BaseRankingRule,
    SemanticScoreRule,
    DistanceRule,
    TableRoleRule,
    HubConvergenceRule,
)


class RankingEngine:

    def __init__(
        self,
        rules: list[BaseRankingRule] | None = None,
    ):

        self.rules = rules or [

            SemanticScoreRule(),

            DistanceRule(),

            TableRoleRule(),

            HubConvergenceRule()

        ]

    def rank(
        self,
        tables: list[RankedTable],
        query: str
    ) -> list[RankedTable]:

        for table in tables:

            total = 0

            evidence = []

            for rule in self.rules:

                result = rule.score(table, query=query)

                total += result.score

                evidence.extend(
                    result.evidence
                )

            table.score = total

            table.evidence = evidence

        return sorted(
            tables,
            key=lambda t: t.score,
            reverse=True,
        )