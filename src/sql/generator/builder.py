from src.ingestion.schema_models import TableInfo
from src.pipeline.pipeline_models import RetrievalResult

from .models import (
    SchemaColumn,
    SchemaContext,
    SchemaRelationship,
    SchemaTable,
    TableReference,
)


class SchemaContextBuilder:
    """
    Converts a RetrievalResult into a SQL-oriented SchemaContext.

    This acts as a translation layer between the retrieval subsystem
    and the SQL generation subsystem.
    """

    def build(
        self,
        retrieval_result: RetrievalResult,
    ) -> SchemaContext:

        context = SchemaContext()

        seen_tables: set[tuple[str, str]] = set()

        seen_relationships: set[
            tuple[str, str, str, str, str, str]
        ] = set()

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

            schema_table = self._build_table(table_info)

            context.tables.append(schema_table)

            context.primary_tables.append(
                TableReference(
                    schema=table_info.schema_name,
                    table=table_info.table,
                )
            )


            for relationship in self._build_relationships(table_info):

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

    def _build_table(
        self,
        table_info: TableInfo,
    ) -> SchemaTable:

        return SchemaTable(
            schema=table_info.schema_name,
            name=table_info.table,
            description=table_info.description,
            columns=self._build_columns(table_info),
        )

    def _build_columns(
        self,
        table_info: TableInfo,
    ) -> list[SchemaColumn]:

        foreign_key_columns = {
            fk.column
            for fk in table_info.foreign_keys
        }

        return [
            SchemaColumn(
                name=column.name,
                is_primary_key=(
                    column.name
                    in table_info.primary_keys
                ),
                is_foreign_key=(
                    column.name
                    in foreign_key_columns
                ),
            )
            for column in table_info.columns
        ]

    def _build_relationships(
        self,
        table_info: TableInfo,
    ) -> list[SchemaRelationship]:

        relationships: list[SchemaRelationship] = []

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
    ) -> tuple[str, str, str, str, str, str]:

        return (
            relationship.source_schema,
            relationship.source_table,
            relationship.source_column,
            relationship.target_schema,
            relationship.target_table,
            relationship.target_column,
        )