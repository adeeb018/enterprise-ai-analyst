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

            # nodes.append(node.id)
            nodes.append(
                {
                    "id": node.id,
                    "role": node.role,  # <--- This saves your new role!
                    # Include table_info or other attributes if your downstream tasks need them
                    # "table_info": node.table_info.model_dump() if hasattr(node.table_info, "model_dump") else node.table_info,
                }
            )

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