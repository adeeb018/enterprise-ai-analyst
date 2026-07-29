from src.ingestion.schema_models import TableInfo
from src.pipeline.pipeline_models import RetrievalResult
from src.graph.schema_graph import SchemaGraph

from .models import (
    SchemaContext,
    SchemaRelationship,
    TableReference,
)


class SchemaContextBuilder:
    """
    Converts a RetrievalResult into a SQL-oriented SchemaContext.

    This acts as a translation layer between the retrieval subsystem
    and the SQL generation subsystem.
    """

    def __init__(self, graph: SchemaGraph | None = None):
        self.graph = graph

    def build(
        self,
        retrieval_result: RetrievalResult,
        graph: SchemaGraph | None = None,
    ) -> SchemaContext:

        context = SchemaContext()
        schema_graph = graph or self.graph

        seen_tables: set[tuple[str, str]] = set()
        seen_relationships: set[tuple] = set()

        ranked_tables = retrieval_result.ranked_context.ranked_tables

        for ranked_table in ranked_tables:

            table_info = ranked_table.node.node.table_info

            table_key = (
                table_info.schema_name,
                table_info.table,
            )

            if table_key in seen_tables:
                continue

            seen_tables.add(table_key)

            context.tables.append(table_info)

            context.primary_tables.append(
                TableReference(
                    schema_=table_info.schema_name,
                    table=table_info.table,
                )
            )

            relationships = self._build_relationships(table_info, schema_graph)

            for relationship in relationships:

                relationship_key = self._relationship_key(
                    relationship
                )

                if relationship_key in seen_relationships:
                    continue

                seen_relationships.add(
                    relationship_key
                )

                context.relationships.append(
                    relationship
                )

        return context


    def _build_relationships(
        self,
        table_info: TableInfo,
        graph: SchemaGraph | None = None,
    ) -> list[SchemaRelationship]:

        relationships: list[SchemaRelationship] = []

        # If SchemaGraph is provided, fetch edges from it to include logical/composite relations
        if graph is not None:
            table_id = SchemaGraph.table_id(
                table_info.schema_name,
                table_info.table,
            )
            node = graph.get_node(table_id)

            if node is not None:
                for edge in node.outgoing:
                    target_parts = edge.target.split(".")
                    if len(target_parts) == 2:
                        target_schema, target_table = target_parts
                    else:
                        target_schema, target_table = "", edge.target

                    relationships.append(
                        SchemaRelationship(
                            source_schema=table_info.schema_name,
                            source_table=table_info.table,
                            source_column=edge.source_column,
                            target_schema=target_schema,
                            target_table=target_table,
                            target_column=edge.target_column,
                        )
                    )
                return relationships

        # Fallback to standard foreign keys
        for fk in table_info.foreign_keys:

            relationships.append(
                SchemaRelationship(
                    source_schema=table_info.schema_name,
                    source_table=table_info.table,
                    source_column=fk.column,
                    target_schema=fk.referred_schema,
                    target_table=fk.referred_table,
                    target_column=fk.referred_column,
                )
            )

        return relationships

    @staticmethod
    def _relationship_key(
        relationship: SchemaRelationship,
    ) -> tuple:
        # Convert lists to tuples so they can be hashed in the set
        src_col = (
            tuple(relationship.source_column)
            if isinstance(relationship.source_column, list)
            else relationship.source_column
        )
        tgt_col = (
            tuple(relationship.target_column)
            if isinstance(relationship.target_column, list)
            else relationship.target_column
        )

        return (
            relationship.source_schema,
            relationship.source_table,
            src_col,
            relationship.target_schema,
            relationship.target_table,
            tgt_col,
        )