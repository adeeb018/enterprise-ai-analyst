from src.graph.graph_models import TableRole
from src.retrieval.ranking.ranking_engine import RankingEngine
from src.retrieval.ranking.ranking_models import (
    RankedContext,
    RankedTable,
)
from src.retrieval.retrieval_models import ExpandedContext


class ContextRanker:

    def __init__(self,graph):

        self.engine = RankingEngine()
        self.graph = graph


    def rank(
        self,
        context: ExpandedContext,
        query: str,
        top_k: int = 15
    ) -> RankedContext:

        ranked_tables = []

        #
        # Convert ExpandedNode -> RankedTable
        #
        for node in context.expanded_tables:

            ranked_tables.append(
                RankedTable(
                    node=node,
                )
            )

        #
        # Apply scoring rules
        #
        ranked_tables = self.engine.rank(
            ranked_tables,
            query
        )

        #
        # Apply Fact Table Coverage Safety Net (Idea 3)
        #
        if self.graph:
            ranked_tables = ensure_fact_table_coverage(
                ranked_tables, 
                self.graph, 
                top_k=top_k
            )

        return RankedContext(
            retrieved_tables=context.retrieved_tables,
            ranked_tables=ranked_tables,
        )
    

def ensure_fact_table_coverage(ranked_tables: list[RankedTable], graph, top_k: int = 5) -> list[RankedTable]:
        """
        Ensures that if a LOOKUP table is in the top_k, at least one connected 
        FACT or DIMENSION table is also pulled into the top_k.
        """
        if not ranked_tables or not graph:
            return ranked_tables

        result = list(ranked_tables[:top_k])
        present_table_ids = {t.node.node.id for t in result}

        for table in list(result):
            graph_node = table.node.node  # Inner GraphNode access
            
            if graph_node is None or getattr(graph_node, "role", None) != TableRole.LOOKUP:
                continue

            neighbors = graph.get_neighbors(graph_node.id)
            fact_neighbors = [
                n for n in neighbors
                if getattr(n, "role", TableRole.FACT) != TableRole.LOOKUP
            ]
            
            if not fact_neighbors:
                continue

            fact_neighbor_ids = {n.id for n in fact_neighbors}
            
            if any(fid in present_table_ids for fid in fact_neighbor_ids):
                continue

            for candidate in ranked_tables:
                candidate_id = getattr(candidate.node.node, "id", None)
                if candidate_id in fact_neighbor_ids:
                    result.append(candidate)
                    present_table_ids.add(candidate_id)
                    break

        return result