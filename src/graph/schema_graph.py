from collections import defaultdict

from src.ingestion.schema_models import TableInfo

from .graph_models import GraphEdge, GraphNode
from collections import deque

from .graph_models import (
    ExpandedNode,
    TraversalState,
)


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
                schema_name=table.schema_name,
                table=table.table,
                columns=[c.name for c in table.columns],
                primary_keys=table.primary_keys,
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
    


    def expand(
        self,
        table_ids: list[str],
        hops: int = 1,
    ) -> list[ExpandedNode]:
        """
        Expand a set of tables using Breadth-First Search (BFS).

        Parameters
        ----------
        table_ids : list[str]
            Starting table ids.

        hops : int
            Maximum traversal depth.

        Returns
        -------
        list[ExpandedNode]
            Expanded nodes in BFS discovery order.
        """

        visited: set[str] = set()
        ordered_tables: list[str] = []

        state: dict[str, TraversalState] = {}

        queue = deque()

        #
        # Initialize BFS
        #
        for table_id in table_ids:

            if table_id not in self.nodes:
                continue

            visited.add(table_id)
            ordered_tables.append(table_id)

            state[table_id] = TraversalState(
                distance=0,
                parent=None,
                edge=None,
            )

            queue.append((table_id, 0))

        #
        # Breadth First Search
        #
        while queue:

            current_table, depth = queue.popleft()

            if depth >= hops:
                continue

            current_node = self.nodes[current_table]

            #
            # Traverse outgoing edges
            #
            for edge in current_node.outgoing:

                if edge.target in visited:
                    continue

                visited.add(edge.target)
                ordered_tables.append(edge.target)

                state[edge.target] = TraversalState(
                    distance=depth + 1,
                    parent=current_table,
                    edge=edge,
                )

                queue.append(
                    (
                        edge.target,
                        depth + 1,
                    )
                )

            #
            # Traverse incoming edges
            #
            for edge in current_node.incoming:

                if edge.source in visited:
                    continue

                visited.add(edge.source)
                ordered_tables.append(edge.source)

                state[edge.source] = TraversalState(
                    distance=depth + 1,
                    parent=current_table,
                    edge=edge,
                )

                queue.append(
                    (
                        edge.source,
                        depth + 1,
                    )
                )

        #
        # Build Expanded Nodes
        #
        expanded_nodes = []

        for table_id in ordered_tables:

            traversal = state[table_id]

            expanded_nodes.append(
                ExpandedNode(
                    node=self.nodes[table_id],
                    distance=traversal.distance,
                    parent=traversal.parent,
                    via_edge=traversal.edge,
                )
            )

        return expanded_nodes
    
    def print_tree(
        self,
        table_id: str,
        hops: int = 2,
    ) -> None:
        """
        Print the graph expansion as a tree.

        Parameters
        ----------
        table_id : str
            Starting table.

        hops : int
            Expansion depth.
        """

        expanded = self.expand(
            [table_id],
            hops=hops,
        )

        lookup = {
            item.node.id: item
            for item in expanded
        }

        children = {}

        for item in expanded:

            if item.parent is None:
                continue

            children.setdefault(
                item.parent,
                []
            ).append(item)

        print()
        print("=" * 60)
        print("GRAPH TREE")
        print("=" * 60)

        self._print_node(
            table_id,
            lookup,
            children,
            level=0,
        )

    def _print_node(
        self,
        table_id: str,
        lookup: dict,
        children: dict,
        level: int,
    ) -> None:

        node = lookup[table_id]

        indent = "    " * level

        print(
            f"{indent}{node.node.id}"
        )

        for child in children.get(
            table_id,
            [],
        ):

            edge = child.via_edge

            if edge:

                print(
                    f"{indent}    └── "
                    f"{child.node.table}"
                    f" "
                    f"({edge.source_column}"
                    f" -> "
                    f"{edge.target_column})"
                )

            self._print_node(
                child.node.id,
                lookup,
                children,
                level + 1,
            )