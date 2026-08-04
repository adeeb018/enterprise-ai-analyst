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
            ranked_tables = ensure_table_coverage(
                ranked_tables, 
                self.graph, 
                top_k=top_k
            )

        return RankedContext(
            retrieved_tables=context.retrieved_tables,
            ranked_tables=ranked_tables,
        )

def ensure_table_coverage(ranked_tables: list[RankedTable], graph, top_k: int = 15) -> list:
    """
    Two-way structural safety net:
    - A LOOKUP table in top_k needs its FACT/DIMENSION partner present.
    - A FACT/DIMENSION table in top_k needs its LOOKUP partner(s) present
      when connected via a guaranteed foreign key (i.e. it likely stores
      a code/itemid that queries will need to resolve to a label).
    Ranking alone can't guarantee this — a structurally required
    dictionary can score low simply because its own description embeds
    poorly against the query, even though the fact table referencing it
    scored well.
    """
    if not ranked_tables:
        return ranked_tables

    result = list(ranked_tables[:top_k])
    present_ids = {t.node.node.id for t in result}

    for table in list(result):
        graph_node = table.node.node
        role = getattr(graph_node, "role", None)
        neighbors = graph.get_neighbors(graph_node.id)

        if role == TableRole.LOOKUP:
            wanted = [n for n in neighbors if getattr(n, "role", TableRole.FACT) != TableRole.LOOKUP]
        elif role in (TableRole.FACT, TableRole.DIMENSION):
            # Only pull in lookups reached via a guaranteed FK — don't
            # drag in every loosely-inferred dictionary neighbor.
            wanted = [
                n for n in neighbors
                if getattr(n, "role", None) == TableRole.LOOKUP
                and graph.has_edge(graph_node.id, n.id)  # confirms a real FK exists
            ]
        else:
            continue

        wanted_ids = {n.id for n in wanted}
        if not wanted_ids or any(wid in present_ids for wid in wanted_ids):
            continue

        for candidate in ranked_tables:
            cid = getattr(candidate.node.node, "id", None)
            if cid in wanted_ids:
                result.append(candidate)
                present_ids.add(cid)
                break

    return result