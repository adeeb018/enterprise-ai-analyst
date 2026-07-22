from src.graph.graph_models import GraphNode
from src.graph.schema_graph import SchemaGraph
from src.relationship.scoring_engine import ScoringEngine

from .relationship_index import RelationshipIndex
from .inference_models import InferredRelationship
from .rules import (
    BaseRule,
    PrimaryKeyMatchRule,
    LookupTableRule,
    SemanticSimilarityRule,
    SharedIdentifierRule,
)


class RelationshipInferenceEngine:

    def __init__(self, rules: list[BaseRule] | None = None):
        self.rules = rules or [
            PrimaryKeyMatchRule(),
            LookupTableRule(),
            SharedIdentifierRule(),
            SemanticSimilarityRule(),
        ]
        self.scoring_engine = ScoringEngine()
        # Instantiate a helper rule instance to check lookup characteristics
        self.lookup_rule_checker = LookupTableRule()


    def infer_relationships(
        self,
        graph: SchemaGraph,
        index: RelationshipIndex,
    ) -> list[InferredRelationship]:

        inferred: list[InferredRelationship] = []

        for source in graph.nodes.values():
            candidates = self._find_candidate_tables(source, index)

            for target in candidates:
                if source.id == target.id:
                    continue

                # Physical FK already expresses this — don't re-infer it
                if graph.has_edge(source.id, target.id):
                    continue
                if graph.has_edge(target.id, source.id):
                    continue

                # --- GENERALIZED LOOKUP VS LOOKUP HEURISTIC ---
                # Check if both tables look like lookup/dictionary tables.
                # Dictionary tables are referenced BY fact tables, not each other.
                source_is_lookup = self._is_lookup_table(source, index)
                target_is_lookup = self._is_lookup_table(target, index)

                if source_is_lookup and target_is_lookup:
                    continue  # Skip evaluating rules for dictionary-to-dictionary pairs
                # ---------------------------------------------

                evidence = []
                for rule in self.rules:
                    result = rule.evaluate(source, target, index)
                    if result:
                        evidence.append(result)

                if not evidence:
                    continue

                confidence = self.scoring_engine.score(evidence, index)

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

            if not index.is_rare_identifier_column(column_name):
                continue

            for node in index.find_tables_with_column(column_name):
                candidates[node.id] = node

        return list(candidates.values())
    
    def _is_lookup_table(self, node: GraphNode, index: RelationshipIndex) -> bool:
        """Helper that uses LookupTableRule logic to evaluate if a node is a dictionary table."""
        # Evaluate against itself or a dummy target to test its lookup metadata properties
        result = self.lookup_rule_checker.evaluate(node, node, index)
        if result and result.metadata.get("lookup_strength", 0.0) > 0.4:
            return True
        return False