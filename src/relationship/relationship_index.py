from collections import defaultdict

from src.graph.schema_graph import SchemaGraph
from src.graph.graph_models import GraphNode


class RelationshipIndex:

    IDENTIFIER_SUFFIXES = (
            "_id",
            "_code",
            "_version",
        )

    def __init__(self):

        #
        # column_name
        #
        # subject_id
        #
        # -> patients
        # -> admissions
        # -> diagnoses_icd
        #
        self.column_index: dict[
            str,
            list[GraphNode]
        ] = defaultdict(list)

        #
        # primary_key column
        #
        self.primary_key_index: dict[
            str,
            list[GraphNode]
        ] = defaultdict(list)

        #
        # table id
        #
        self.table_index: dict[
            str,
            GraphNode
        ] = {}

    def build(
        self,
        graph: SchemaGraph,
    ) -> None:

        self.column_index.clear()
        self.primary_key_index.clear()
        self.table_index.clear()

        for node in graph.nodes.values():

            self.table_index[node.id] = node

            #
            # Columns
            #
            for column in node.table_info.columns:

                self.column_index[
                    column.name.lower()
                ].append(node)

            #
            # Primary Keys
            #
            for pk in node.table_info.primary_keys:

                self.primary_key_index[
                    pk.lower()
                ].append(node)

    def find_tables_with_column(
        self,
        column: str,
    ) -> list[GraphNode]:

        return self.column_index.get(
            column.lower(),
            [],
        )
    
    def find_tables_with_primary_key(
        self,
        column: str,
    ) -> list[GraphNode]:

        return self.primary_key_index.get(
            column.lower(),
            [],
        )
    
    def get_table(
        self,
        table_id: str,
    ) -> GraphNode | None:

        return self.table_index.get(
            table_id
        )


    def is_identifier_column(
        self,
        column_name: str,
    ) -> bool:

        column_name = column_name.lower()

        if column_name.endswith(self.IDENTIFIER_SUFFIXES):
            return True

        #
        # Common enterprise identifiers
        #
        return column_name in {
            "itemid",
            "subject_id",
            "hadm_id",
            "stay_id",
            "provider_id",
            "specimen_id",
        }