from src.ingestion.schema_models import (
    ColumnInfo,
    ForeignKeyInfo,
    TableInfo,
)

from src.ingestion.schema_exporter import SchemaExporter

from sqlalchemy import inspect

from src.config.database import engine


class SchemaExtractor:
    def __init__(self):
        self.inspector = inspect(engine)

    def get_tables(self) -> dict[str, list[str]]:
        schemas = ["mimiciv_hosp", "mimiciv_icu"]

        tables = {}

        for schema in schemas:
            tables[schema] = self.inspector.get_table_names(schema=schema)

        return tables

    def get_columns(
        self,
        schema: str,
        table: str,
    ) -> list[dict]:
        return self.inspector.get_columns(
            table_name=table,
            schema=schema,
        )

    def get_primary_keys(
        self,
        schema: str,
        table: str,
    ) -> list[str]:
        pk = self.inspector.get_pk_constraint(
            table_name=table,
            schema=schema,
        )

        return pk.get("constrained_columns", [])

    def get_foreign_keys(
        self,
        schema: str,
        table: str,
    ) -> list[dict]:
        return self.inspector.get_foreign_keys(
            table_name=table,
            schema=schema,
        )

    def extract_schema(self) -> list[TableInfo]:
        database_schema: list[TableInfo] = []

        tables = self.get_tables()

        for schema_name, table_names in tables.items():

            for table_name in table_names:

                table = TableInfo(
                    schema_name=schema_name,
                    table=table_name,
                    primary_keys=self.get_primary_keys(
                        schema_name,
                        table_name,
                    ),
                )

                # Columns
                for column in self.get_columns(schema_name, table_name):
                    table.columns.append(
                        ColumnInfo(
                            name=column["name"],
                            data_type=str(column["type"]),
                            nullable=column["nullable"],
                        )
                    )

                # Foreign Keys
                for fk in self.get_foreign_keys(schema_name, table_name):

                    for local_col, remote_col in zip(
                        fk["constrained_columns"],
                        fk["referred_columns"],
                    ):
                        table.foreign_keys.append(
                            ForeignKeyInfo(
                                column=local_col,
                                referred_schema=fk["referred_schema"],
                                referred_table=fk["referred_table"],
                                referred_column=remote_col,
                            )
                        )

                database_schema.append(table)

        return database_schema