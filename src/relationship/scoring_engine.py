from src.relationship.inference_models import (
    RelationshipEvidence,
)
from src.relationship.relationship_index import (
    RelationshipIndex,
)
import math


class ScoringEngine:

    RULE_WEIGHTS = {
        "column_name_match": 10,
        "primary_key_match": 25,
        "lookup_table": 20,
        "shared_identifier": 15,
    }

    def score(
        self,
        evidence: list[RelationshipEvidence],
        index: RelationshipIndex,
    ) -> float:

        total = 0.0

        #
        # Prevent counting the same identifier twice
        #
        counted_columns: set[str] = set()

        for item in evidence:

            #
            # Lookup rule doesn't use identifiers
            #
            if item.rule == "lookup_table":

                total += self.RULE_WEIGHTS[item.rule]

                continue

            for column in item.matched_columns:

                #
                # Already counted
                #
                if column in counted_columns:
                    continue

                counted_columns.add(column)

                #
                # Rarer columns are stronger evidence
                #
                frequency = len(
                    index.find_tables_with_column(column)
                )

                # rarity = 1 / frequency

                rarity = 1 / math.log2(frequency + 1)

                total += (
                    self.RULE_WEIGHTS[item.rule]
                    * rarity
                )

        return round(total, 3)