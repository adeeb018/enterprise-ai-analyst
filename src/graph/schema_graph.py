
from src.ingestion.schema_models import TableInfo

from .graph_models import GraphEdge, GraphNode


class SchemaGraph:

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}

    @staticmethod
    def table_id(schema: str, table: str) -> str:
        return f"{schema}.{table}"

    @classmethod
    def build(
        cls,
        schema: list[TableInfo],
    ) -> "SchemaGraph":

        graph = cls()

        #
        # Create Nodes
        #
        for table in schema:

            node = GraphNode(
                id=cls.table_id(
                    table.schema_name,
                    table.table,
                ),
                table_info=table,
            )

            graph.nodes[node.id] = node

        #
        # Create Edges
        #
        for table in schema:

            source = cls.table_id(
                table.schema_name,
                table.table,
            )

            for fk in table.foreign_keys:

                if (
                    fk.referred_schema is None
                    or fk.referred_table is None
                    or fk.referred_column is None
                ):
                    continue

                target = cls.table_id(
                    fk.referred_schema,
                    fk.referred_table,
                )

                edge = GraphEdge(
                    source=source,
                    target=target,
                    source_column=fk.column,
                    target_column=fk.referred_column,
                )

                graph.nodes[source].outgoing.append(edge)

                if target in graph.nodes:
                    graph.nodes[target].incoming.append(edge)

        return graph
    
    def get_node(
        self,
        table_id: str,
    ) -> GraphNode | None:
        return self.nodes.get(table_id)


    def get_neighbors(
        self,
        table_id: str,
    ) -> list[GraphNode]:

        node = self.get_node(table_id)

        if node is None:
            return []

        neighbors = {}

        for edge in node.outgoing:
            neighbors[edge.target] = self.nodes[edge.target]

        for edge in node.incoming:
            neighbors[edge.source] = self.nodes[edge.source]

        return list(neighbors.values())


    def has_edge(self, source_id: str, target_id: str) -> bool:
        node = self.nodes.get(source_id)
        if node is None:
            return False
        return any(edge.target == target_id for edge in node.outgoing)