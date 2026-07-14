import json
from pathlib import Path

from src.graph.schema_graph import SchemaGraph


class GraphExporter:

    def export(
        self,
        graph: SchemaGraph,
        output_path: Path,
    ) -> None:

        nodes = []
        edges = []

        #
        # Export nodes
        #
        for node in graph.nodes.values():

            nodes.append(node.id)

            #
            # Export outgoing edges only
            #
            for edge in node.outgoing:

                edges.append(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "source_column": edge.source_column,
                        "target_column": edge.target_column,
                        "relationship": edge.relationship,
                        "confidence": edge.confidence,
                        "evidence": edge.evidence,
                    }
                )

        data = {
            "nodes": nodes,
            "edges": edges,
        }

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
            )