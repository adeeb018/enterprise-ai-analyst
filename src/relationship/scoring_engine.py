from src.relationship.inference_models import (
    RelationshipEvidence,
)
from src.relationship.relationship_index import (
    RelationshipIndex,
)
import math

# scoring_engine.py


class ScoringEngine:

    # NOTE: "column_name_match" weight removed — that rule no longer
    # exists (see rules.py / relationship_inference_engine.py).
    RULE_WEIGHTS = {
        "primary_key_match": 25,
        "lookup_table": 20,
        "shared_identifier": 15,
        "semantic_similarity": 30,
    }

    # Floor so a total non-match doesn't zero out other real evidence
    # entirely — but weak lookup evidence should still cost a lot.
    MIN_LOOKUP_MULTIPLIER = 0.25

    def score(self, evidence, index):

        total = 0.0
        counted_columns: set[str] = set()

        # FIX: only treat this pair as "lookup-flavored" if a
        # lookup_table item is actually present in the evidence.
        # Previously, lookup_strength defaulted to 0.0 and
        # lookup_multiplier was computed unconditionally — meaning any
        # pair with NO lookup_table evidence at all (the common case
        # for fact-to-fact relationships) got a flat lookup_multiplier
        # of 0.25, applying an unintended 75% discount to every
        # column-based score contribution. The multiplier is now only
        # meaningful, and only applied, when lookup evidence exists.
        has_lookup_evidence = False
        lookup_strength = 0.0
        for item in evidence:
            if item.rule == "lookup_table":
                has_lookup_evidence = True
                lookup_strength = item.metadata.get("lookup_strength", 0.0)

        if has_lookup_evidence:
            # Scale from MIN_LOOKUP_MULTIPLIER up to 1.0 based on
            # strength, rather than a flat penalty/no-penalty switch.
            lookup_multiplier = self.MIN_LOOKUP_MULTIPLIER + (
                (1 - self.MIN_LOOKUP_MULTIPLIER) * lookup_strength
            )
        else:
            lookup_multiplier = 1.0

        for item in evidence:

            if item.rule == "lookup_table":
                total += self.RULE_WEIGHTS[item.rule] * lookup_strength
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

                total += self.RULE_WEIGHTS[item.rule] * rarity * lookup_multiplier

        return round(total, 3)