from collections import deque

from src.graph.schema_graph import SchemaGraph
from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retrieval_models import (
    ExpandedContext,
    ExpandedNode,
    TraversalState,
)


class GraphExpander:
    """
    Expands semantically retrieved tables through the schema graph.

    Responsibilities
    ----------------
    - Breadth First Search
    - Hop limiting
    - Duplicate removal
    - Preserve traversal metadata

    Does NOT
    --------
    - Rank tables
    - Filter relationships
    - Modify retrieval scores
    """

    def __init__(
        self,
        graph: SchemaGraph,
    ):
        self.graph = graph

    def expand(
        self,
        retrieved_tables: list[RetrievedChunk],
        hops: int = 1,
    ) -> ExpandedContext:

        expanded: dict[str, ExpandedNode] = {}

        ordered_nodes: list[ExpandedNode] = []

        queue = deque()

        #
        # Initialize BFS
        #
        for retrieved in retrieved_tables:

            table_id = (
                f"{retrieved.schema_name}."
                f"{retrieved.table}"
            )

            node = self.graph.get_node(table_id)

            if node is None:
                continue

            state = TraversalState(
                table_id=table_id,
                distance=0,
                parent=None,
                via_edge=None,
                source_seed=table_id,
            )

            queue.append(state)

            expanded_node = ExpandedNode(
                node=node,
                distance=0,
                parent=None,
                via_edge=None,
                source_seed=table_id,
            )

            expanded[table_id] = expanded_node
            ordered_nodes.append(expanded_node)

        #
        # Breadth First Search
        #
        while queue:

            current = queue.popleft()

            if current.distance >= hops:
                continue

            current_node = self.graph.get_node(
                current.table_id
            )

            if current_node is None:
                continue

            #
            # Traverse outgoing edges
            #
            for edge in current_node.outgoing:

                self._visit(
                    edge.target,
                    edge,
                    current,
                    queue,
                    expanded,
                    ordered_nodes,
                )

            #
            # Traverse incoming edges
            #
            for edge in current_node.incoming:

                self._visit(
                    edge.source,
                    edge,
                    current,
                    queue,
                    expanded,
                    ordered_nodes,
                )

        return ExpandedContext(
            retrieved_tables=retrieved_tables,
            expanded_tables=ordered_nodes,
        )

    def _visit(
        self,
        neighbour_id: str,
        edge,
        current: TraversalState,
        queue,
        expanded,
        ordered_nodes,
    ):

        if neighbour_id in expanded:
            return

        neighbour = self.graph.get_node(
            neighbour_id
        )

        if neighbour is None:
            return

        state = TraversalState(
            table_id=neighbour_id,
            distance=current.distance + 1,
            parent=current.table_id,
            via_edge=edge,
            source_seed=current.source_seed,
        )

        queue.append(state)

        expanded_node = ExpandedNode(
            node=neighbour,
            distance=state.distance,
            parent=state.parent,
            via_edge=state.via_edge,
            source_seed=state.source_seed,
        )

        expanded[neighbour_id] = expanded_node
        ordered_nodes.append(expanded_node)