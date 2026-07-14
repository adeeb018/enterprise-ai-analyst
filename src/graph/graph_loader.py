import json
from pathlib import Path

from src.graph.graph_models import (
    GraphEdge,
    GraphNode,
)
from src.graph.schema_graph import SchemaGraph
from src.ingestion.schema_models import TableInfo


class GraphLoader:

    def load(
        self,
        graph_path: Path,
        schema: list[TableInfo],
    ) -> SchemaGraph:
        """
        Reconstruct a SchemaGraph from:

        - graph.json (graph topology)
        - enriched_schema.json (table metadata)
        """

        #
        # Load graph topology
        #
        with open(
            graph_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        #
        # Build lookup for table metadata
        #
        table_lookup = {
            f"{table.schema_name}.{table.table}": table
            for table in schema
        }

        graph = SchemaGraph()

        #
        # Create nodes
        #
        for node_id in data["nodes"]:

            table_info = table_lookup.get(node_id)

            if table_info is None:
                raise ValueError(
                    f"Table '{node_id}' not found in schema."
                )

            graph.nodes[node_id] = GraphNode(
                id=node_id,
                table_info=table_info,
            )

        #
        # Create edges
        #
        for edge_data in data["edges"]:

            source = edge_data["source"]
            target = edge_data["target"]

            if source not in graph.nodes:
                raise ValueError(
                    f"Unknown source node '{source}'."
                )

            if target not in graph.nodes:
                raise ValueError(
                    f"Unknown target node '{target}'."
                )

            edge = GraphEdge(
                source=source,
                target=target,
                source_column=edge_data.get("source_column"),
                target_column=edge_data.get("target_column"),
                relationship=edge_data.get(
                    "relationship",
                    "foreign_key",
                ),
                confidence=edge_data.get(
                    "confidence",
                    1.0,
                ),
                evidence=edge_data.get(
                    "evidence",
                    [],
                ),
            )

            graph.nodes[source].outgoing.append(edge)
            graph.nodes[target].incoming.append(edge)

        return graph