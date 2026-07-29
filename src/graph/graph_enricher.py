from src.graph.graph_models import GraphEdge
from src.graph.schema_graph import SchemaGraph
from src.relationship.inference_models import InferredRelationship


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

            # Extract matched columns from the evidence items
            matched_cols = []
            for ev in relationship.evidence:
                if ev.matched_columns:
                    matched_cols.extend(ev.matched_columns)
            
            # Deduplicate while preserving order
            matched_cols = list(dict.fromkeys(matched_cols))

            # If multiple columns match (e.g. icd_code, icd_version), pass them as a list.
            # If it's a single column, pass it as a string or single-item list.
            col_value = matched_cols if len(matched_cols) > 1 else (matched_cols[0] if matched_cols else None)

            edge = GraphEdge(
                source=relationship.source,
                target=relationship.target,
                source_column=col_value,
                target_column=col_value,
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