from src.ingestion.schema_models import TableInfo

from .chunking_strategies import (
    BaseChunkingStrategy,
    HCPCSChunkingStrategy,
    ICDChunkingStrategy,
    ItemsChunkingStrategy,
    LabItemsChunkingStrategy,
)
from .value_models import ValueChunk


class ValueChunker:

    def __init__(self):

        self.strategies: dict[
            str,
            BaseChunkingStrategy,
        ] = {

            "d_icd_diagnoses":
                ICDChunkingStrategy(),

            "d_icd_procedures":
                ICDChunkingStrategy(),

            "d_hcpcs":
                HCPCSChunkingStrategy(),

            "d_labitems":
                LabItemsChunkingStrategy(),

            "d_items":
                ItemsChunkingStrategy(),
        }

    def chunk(
        self,
        table: TableInfo,
        dataframe,
    ) -> list[ValueChunk]:

        strategy = self.strategies.get(
            table.table,
        )

        if strategy is None:

            raise ValueError(
                f"No chunking strategy registered for '{table.table}'."
            )

        return strategy.chunk(
            schema_name=table.schema_name,
            table=table.table,
            df=dataframe,
        )