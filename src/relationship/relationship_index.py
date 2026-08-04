from collections import defaultdict

from src.graph.schema_graph import SchemaGraph
from src.graph.graph_models import GraphNode


class RelationshipIndex:

    # Columns that represent row-ordering within a group, not a
    # real-world entity or vocabulary. Frequency alone won't catch
    # these — some are rare simply because few tables need ordering.
    MAX_CANDIDATE_FREQUENCY = 5
    IDENTIFIER_SUFFIXES = ("_id", "_code", "_version")
    ORDINAL_PATTERNS = ("seq", "_num", "ordinal", "position", "rank")

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
    
    def is_ordinal_column(self, column_name: str) -> bool:
        column_name = column_name.lower()
        return any(pattern in column_name for pattern in self.ORDINAL_PATTERNS)

    def is_rare_identifier_column(self, column_name: str) -> bool:
        column_name = column_name.lower()

        if self.is_ordinal_column(column_name):
            return False

        if not column_name.endswith(self.IDENTIFIER_SUFFIXES) and column_name != "itemid":
            return False

        frequency = self.get_column_frequency(column_name)
        return 0 < frequency <= self.MAX_CANDIDATE_FREQUENCY