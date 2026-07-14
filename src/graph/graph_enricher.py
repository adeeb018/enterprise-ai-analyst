from src.graph.graph_models import GraphEdge
from src.graph.schema_graph import SchemaGraph

from src.relationship.inference_models import (
    InferredRelationship,
)


class GraphEnricher:

    def enrich(
        self,
        graph: SchemaGraph,
        inferred: list[InferredRelationship],
        confidence_threshold: float = 30.0,
    ) -> SchemaGraph:
        """
        Add inferred logical relationships into the graph.
        """

        for relationship in inferred:

            #
            # Ignore weak relationships
            #
            if relationship.confidence < confidence_threshold:
                continue

            source = graph.get_node(
                relationship.source
            )

            target = graph.get_node(
                relationship.target
            )

            if source is None or target is None:
                continue

            #
            # Avoid duplicates
            #
            if graph.has_edge(
                relationship.source,
                relationship.target,
            ):
                continue

            edge = GraphEdge(
                source=relationship.source,
                target=relationship.target,

                relationship=relationship.relationship,

                confidence=relationship.confidence,

                evidence=[
                    evidence.rule
                    for evidence in relationship.evidence
                ],
            )

            source.outgoing.append(edge)
            target.incoming.append(edge)

        return graph