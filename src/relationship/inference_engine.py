from src.graph.graph_models import GraphNode
from src.graph.schema_graph import SchemaGraph
from src.relationship.scoring_engine import ScoringEngine

from .relationship_index import RelationshipIndex
from .inference_models import InferredRelationship
from .rules import (
    BaseRule,
    ColumnNameMatchRule,
    PrimaryKeyMatchRule,
    LookupTableRule,
    SharedIdentifierRule,
)


class RelationshipInferenceEngine:

    def __init__(
        self,
        rules: list[BaseRule] | None = None,
    ):

        self.rules = rules or [
            ColumnNameMatchRule(),
            PrimaryKeyMatchRule(),
            LookupTableRule(),
            SharedIdentifierRule(),
        ]

        self.scoring_engine = ScoringEngine()

    def infer_relationships(
        self,
        graph: SchemaGraph,
        index: RelationshipIndex,
    ) -> list[InferredRelationship]:

        inferred: list[InferredRelationship] = []

        #
        # Evaluate every table
        #
        for source in graph.nodes.values():

            candidates = self._find_candidate_tables(
                source,
                index,
            )

            for target in candidates:

                #
                # Don't compare a table with itself
                #
                if source.id == target.id:
                    continue

                evidence = []

                for rule in self.rules:

                    result = rule.evaluate(
                        source,
                        target,
                        index,
                    )

                    if result:
                        evidence.append(result)

                if not evidence:
                    continue

                confidence = self.scoring_engine.score(
                    evidence,
                    index,
                )

                inferred.append(
                    InferredRelationship(
                        source=source.id,
                        target=target.id,
                        confidence=confidence,
                        evidence=evidence,
                    )
                )

        return inferred

    def _find_candidate_tables(
        self,
        source: GraphNode,
        index: RelationshipIndex,
    ) -> list[GraphNode]:

        candidates = {}

        for column in source.table_info.columns:

            column_name = column.name.lower()

            #
            # Only identifier columns
            #
            if not index.is_identifier_column(column_name):
                continue

            for node in index.find_tables_with_column(
                column_name
            ):
                candidates[node.id] = node

        return list(candidates.values())