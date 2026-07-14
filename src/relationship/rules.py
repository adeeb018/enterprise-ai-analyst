from abc import ABC, abstractmethod

from src.graph.graph_models import GraphNode
from src.relationship.relationship_index import RelationshipIndex

from .inference_models import RelationshipEvidence
import math


class BaseRule(ABC):

    @abstractmethod
    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:
        pass


class ColumnNameMatchRule(BaseRule):

    SCORE_PER_MATCH = 20
    MAX_SCORE = 40

    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:

        source_columns = {
            column.name.lower()
            for column in source.table_info.columns
        }

        target_columns = {
            column.name.lower()
            for column in target.table_info.columns
        }

        matched = sorted(
            source_columns.intersection(target_columns)
        )

        if not matched:
            return None

        score = min(
            len(matched) * self.SCORE_PER_MATCH,
            self.MAX_SCORE,
        )

        return RelationshipEvidence(
            rule="column_name_match",
            explanation=(
                f"Found {len(matched)} shared column(s)."
            ),
            matched_columns=matched,
        )
    
class PrimaryKeyMatchRule(BaseRule):

    SCORE_PER_MATCH = 25
    MAX_SCORE = 50

    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:

        source_keys = {
            key.lower()
            for key in source.table_info.primary_keys
        }

        target_keys = {
            key.lower()
            for key in target.table_info.primary_keys
        }

        matched = sorted(
            source_keys.intersection(target_keys)
        )

        if not matched:
            return None

        score = min(
            len(matched) * self.SCORE_PER_MATCH,
            self.MAX_SCORE,
        )

        return RelationshipEvidence(
            rule="primary_key_match",
            explanation=(
                f"Found {len(matched)} shared primary key column(s)."
            ),
            matched_columns=matched,
            metadata={
                "shared_primary_keys": matched,
            },
        )
    
class LookupTableRule(BaseRule):

    PREFIX_SCORE = 10
    COLUMN_COUNT_SCORE = 10
    NO_FK_SCORE = 5
    DESCRIPTION_SCORE = 15
    PRIMARY_KEY_SCORE = 10

    DESCRIPTION_COLUMNS = {
        "long_title",
        "label",
        "description",
        "name",
        "title",
    }

    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:

        table = target.table_info

        score = 0

        reasons = []

        #
        # Dictionary naming convention
        #
        if table.table.startswith("d_"):

            score += self.PREFIX_SCORE

            reasons.append(
                "table starts with 'd_'"
            )

        #
        # Small tables are usually lookup tables
        #
        if len(table.columns) <= 5:

            score += self.COLUMN_COUNT_SCORE

            reasons.append(
                "few columns"
            )

        #
        # Lookup tables rarely have foreign keys
        #
        if not table.foreign_keys:

            score += self.NO_FK_SCORE

            reasons.append(
                "no foreign keys"
            )

        #
        # Has description column
        #
        column_names = {
            column.name.lower()
            for column in table.columns
        }

        matched = sorted(
            self.DESCRIPTION_COLUMNS.intersection(
                column_names
            )
        )

        if matched:

            score += self.DESCRIPTION_SCORE

            reasons.append(
                "contains descriptive text"
            )

        #
        # Has primary key
        #
        if table.primary_keys:

            score += self.PRIMARY_KEY_SCORE

            reasons.append(
                "contains primary key"
            )

        if score == 0:
            return None

        return RelationshipEvidence(
            rule="lookup_table",
            explanation=", ".join(reasons),
            matched_columns=matched,
            # metadata={
            #     "lookup_score": score,
            # },
        )
    

class SharedIdentifierRule(BaseRule):

    SCORE_PER_IDENTIFIER = 20
    MAX_SCORE = 60

    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:

        matched_identifiers = []

        for column in source.table_info.columns:
            name = column.name.lower()

            # Skip generic linking keys — they don't discriminate
            if not index.is_rare_identifier_column(name):
                continue

            candidate_tables = index.find_tables_with_column(name)

            if any(node.id == target.id for node in candidate_tables):
                matched_identifiers.append(name)

        matched_identifiers = sorted(set(matched_identifiers))

        if not matched_identifiers:
            return None

        score = min(
            len(matched_identifiers) * self.SCORE_PER_IDENTIFIER,
            self.MAX_SCORE,
        )

        return RelationshipEvidence(
            rule="shared_identifier",
            explanation=f"Found {len(matched_identifiers)} shared rare identifier column(s).",
            matched_columns=matched_identifiers,
            metadata={"shared_identifiers": matched_identifiers},
        )


class SemanticSimilarityRule(BaseRule):

    MIN_SIMILARITY = 0.55  # below this, don't even attach evidence

    def evaluate(
        self,
        source: GraphNode,
        target: GraphNode,
        index: RelationshipIndex,
    ) -> RelationshipEvidence | None:

        source_vec = source.table_info.description_embedding
        target_vec = target.table_info.description_embedding

        if not source_vec or not target_vec:
            return None

        similarity = self._cosine_similarity(source_vec, target_vec)

        if similarity < self.MIN_SIMILARITY:
            return None

        return RelationshipEvidence(
            rule="semantic_similarity",
            explanation=f"Table descriptions are semantically similar ({similarity:.2f}).",
            metadata={"similarity": similarity},
        )

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)