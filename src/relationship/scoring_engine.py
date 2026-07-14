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
        "semantic_similarity": 30,  # tune relative to the others
    }

    def score(
        self,
        evidence: list[RelationshipEvidence],
        index: RelationshipIndex,
    ) -> float:

        total = 0.0
        counted_columns: set[str] = set()

        for item in evidence:

            if item.rule == "lookup_table":
                total += self.RULE_WEIGHTS[item.rule]
                continue

            if item.rule == "semantic_similarity":
                similarity = item.metadata.get("similarity", 0.0)
                total += self.RULE_WEIGHTS[item.rule] * similarity
                continue

            for column in item.matched_columns:
                if column in counted_columns:
                    continue
                counted_columns.add(column)

                frequency = len(index.find_tables_with_column(column))
                rarity = 1 / math.log2(frequency + 1)

                total += self.RULE_WEIGHTS[item.rule] * rarity

        return round(total, 3)