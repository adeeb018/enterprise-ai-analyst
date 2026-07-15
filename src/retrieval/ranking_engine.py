from src.retrieval.ranking_models import (
    RankedTable,
)
from src.retrieval.ranking_rules import (
    BaseRankingRule,
    SemanticScoreRule,
    DistanceRule,
)


class RankingEngine:

    def __init__(
        self,
        rules: list[BaseRankingRule] | None = None,
    ):

        self.rules = rules or [

            SemanticScoreRule(),

            DistanceRule(),

        ]

    def rank(
        self,
        tables: list[RankedTable],
    ) -> list[RankedTable]:

        for table in tables:

            total = 0

            evidence = []

            for rule in self.rules:

                result = rule.score(table)

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