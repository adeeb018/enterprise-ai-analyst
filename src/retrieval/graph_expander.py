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
    - Duplicate removal (keeping the strongest path to any given node)
    - Preserve traversal metadata
    - Propagate retrieval confidence outward through the graph, decayed per hop

    Does NOT
    --------
    - Rank tables (final ranking/weighting logic lives downstream)
    - Filter relationships
    - Invent scores unrelated to the originating semantic retrieval
    """

    def __init__(self, graph: SchemaGraph):
        self.graph = graph

    def expand(
        self,
        retrieved_tables: list[RetrievedChunk],
        hops: int = 1,
        decay: float = 0.75,
    ) -> ExpandedContext:
        """
        Parameters
        ----------
        retrieved_tables : the seed tables from semantic/value retrieval,
            each carrying its own retrieval score.
        hops : max BFS distance to traverse from any seed.
        decay : multiplicative factor applied to a score each time it
            crosses one edge. A neighbour of a 0.90-score seed at hop 1
            gets 0.90 * decay, not a flat constant. Tune empirically.
        """
        expanded: dict[str, ExpandedNode] = {}
        ordered_nodes: list[ExpandedNode] = []
        queue: deque[TraversalState] = deque()

        #
        # Initialize BFS from every seed table
        #
        for retrieved in retrieved_tables:
            table_id = f"{retrieved.schema_name}.{retrieved.table}"

            node = self.graph.get_node(table_id)
            if node is None:
                continue

            state = TraversalState(
                table_id=table_id,
                distance=0,
                parent=None,
                via_edge=None,
                source_seed=table_id,
                score=retrieved.score,
            )
            queue.append(state)

            expanded_node = ExpandedNode(
                node=node,
                distance=0,
                parent=None,
                via_edge=None,
                source_seed=table_id,
                retrieval_score=retrieved.score,
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

            current_node = self.graph.get_node(current.table_id)
            if current_node is None:
                continue

            # Traverse outgoing edges
            for edge in current_node.outgoing:
                self._visit(
                    edge.target,
                    edge,
                    current,
                    queue,
                    expanded,
                    ordered_nodes,
                    decay,
                )

            # Traverse incoming edges
            for edge in current_node.incoming:
                self._visit(
                    edge.source,
                    edge,
                    current,
                    queue,
                    expanded,
                    ordered_nodes,
                    decay,
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
        queue: deque,
        expanded: dict[str, ExpandedNode],
        ordered_nodes: list[ExpandedNode],
        decay: float,
    ):
        propagated_score = current.score * decay

        if neighbour_id in expanded:
            # A node can be reached via multiple paths from different
            # seeds (or the same seed via a longer route). Keep the
            # strongest path rather than whichever BFS happened to
            # visit first — otherwise a weak seed processed earlier
            # can silently block a stronger seed's contribution to
            # a shared neighbour (e.g. diagnoses_icd reachable from
            # both a strong d_icd_diagnoses hit and a weak unrelated hit).
            existing = expanded[neighbour_id]
            if propagated_score > existing.retrieval_score:
                existing.retrieval_score = propagated_score
                existing.distance = current.distance + 1
                existing.parent = current.table_id
                existing.via_edge = edge
                existing.source_seed = current.source_seed
            return

        neighbour = self.graph.get_node(neighbour_id)
        if neighbour is None:
            return

        state = TraversalState(
            table_id=neighbour_id,
            distance=current.distance + 1,
            parent=current.table_id,
            via_edge=edge,
            source_seed=current.source_seed,
            score=propagated_score,
        )
        queue.append(state)

        expanded_node = ExpandedNode(
            node=neighbour,
            distance=state.distance,
            parent=state.parent,
            via_edge=state.via_edge,
            source_seed=state.source_seed,
            retrieval_score=propagated_score,
        )

        expanded[neighbour_id] = expanded_node
        ordered_nodes.append(expanded_node)