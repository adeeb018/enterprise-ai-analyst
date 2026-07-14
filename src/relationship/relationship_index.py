from collections import defaultdict

from src.graph.schema_graph import SchemaGraph
from src.graph.graph_models import GraphNode


class RelationshipIndex:

    # A column appearing in more than this many tables is treated as
    # a generic linking key (subject_id-like), not a domain identifier.
    # Tune per schema size; doesn't require knowing column names up front.
    MAX_CANDIDATE_FREQUENCY = 5

    def __init__(self):
        self.column_index: dict[str, list[GraphNode]] = defaultdict(list)
        self.primary_key_index: dict[str, list[GraphNode]] = defaultdict(list)
        self.table_index: dict[str, GraphNode] = {}
        self.column_frequency: dict[str, int] = {}

    def build(self, graph: SchemaGraph) -> None:
        self.column_index.clear()
        self.primary_key_index.clear()
        self.table_index.clear()
        self.column_frequency.clear()

        for node in graph.nodes.values():
            self.table_index[node.id] = node

            for column in node.table_info.columns:
                self.column_index[column.name.lower()].append(node)

            for pk in node.table_info.primary_keys:
                self.primary_key_index[pk.lower()].append(node)

        # Frequency table built after column_index is fully populated
        for column, tables in self.column_index.items():
            self.column_frequency[column] = len(tables)

    def find_tables_with_column(self, column: str) -> list[GraphNode]:
        return self.column_index.get(column.lower(), [])

    def find_tables_with_primary_key(self, column: str) -> list[GraphNode]:
        return self.primary_key_index.get(column.lower(), [])

    def get_table(self, table_id: str) -> GraphNode | None:
        return self.table_index.get(table_id)

    def get_column_frequency(self, column: str) -> int:
        return self.column_frequency.get(column.lower(), 0)

    def is_rare_identifier_column(self, column_name: str) -> bool:
        """A column is worth using for candidate generation if it's
        not a generic linking key — i.e. it doesn't appear all over
        the schema. Replaces the old hardcoded name list."""
        frequency = self.get_column_frequency(column_name)
        return 0 < frequency <= self.MAX_CANDIDATE_FREQUENCY