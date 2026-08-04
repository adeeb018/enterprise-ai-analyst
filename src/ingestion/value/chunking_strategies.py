from abc import ABC, abstractmethod
import pandas as pd
from tqdm import tqdm

from src.ingestion.value.chunk_merger import ChunkMerger
from src.ingestion.value.hierarchy_splitter import HierarchySplitter
from .value_models import ValueChunk
from uuid import uuid4

class BaseChunkingStrategy(ABC):

    def __init__(self):

        self.splitter = HierarchySplitter()
        self.merger = ChunkMerger()

    @abstractmethod
    def chunk(
        self,
        schema_name: str,
        table: str,
        df: pd.DataFrame,
    ) -> list[ValueChunk]:
        ...

    def build_chunk(
        self,
        schema_name: str,
        table: str,
        column: str,
        values: list[str],
        metadata: dict | None = None,
    ) -> ValueChunk:

        #
        # Final defensive cleaning
        #
        clean_values = []

        for value in values:

            if pd.isna(value):
                continue

            value = str(value).strip()

            if not value:
                continue

            clean_values.append(value)

        text = (
            f"Table: {table}\n"
            f"Column: {column}\n\n"
            + "\n".join(clean_values)
        )

        return ValueChunk(
            id=str(uuid4()),
            schema_name=schema_name,
            table=table,
            column=column,
            values=clean_values,
            text=text,
            metadata=metadata or {},
    )

class ICDChunkingStrategy(
    BaseChunkingStrategy,
):

    def chunk(
        self,
        schema_name: str,
        table: str,
        df: pd.DataFrame,
    ) -> list[ValueChunk]:

        chunks = []

        #
        # ICD9 and ICD10 should never mix
        #

        groups = list(df.groupby("icd_version"))

        for version, group in tqdm(groups, desc=f"Chunking {table} by version"):

            split = self.splitter.split(
                df=group,
                code_column="icd_code",
            )

            split = self.merger.merge(
                split,
                code_column="icd_code",
            )

            for _, chunk_df in split.items():

                values = chunk_df[
                    "long_title"
                ].tolist()

                chunks.append(

                    self.build_chunk(
                        schema_name=schema_name,
                        table=table,
                        column="long_title",
                        values=values,
                        metadata={
                            "version": version,
                            "rows": len(chunk_df),
                        },
                    )

                )

        return chunks
    

class HCPCSChunkingStrategy(
    BaseChunkingStrategy,
):

    def chunk(
        self,
        schema_name: str,
        table: str,
        df: pd.DataFrame,
    ) -> list[ValueChunk]:

        df = df[
            df["long_description"].notna()
        ]

        split = self.splitter.split(
            df=df,
            code_column="code",
        )

        split = self.merger.merge(
            split,
            code_column="code",
        )

        chunks = []

        for _, chunk_df in split.items():

            values = chunk_df[
                "long_description"
            ].tolist()

            chunks.append(

                self.build_chunk(
                    schema_name,
                    table,
                    "long_description",
                    values,
                    metadata={
                        "rows": len(chunk_df),
                    },
                )

            )

        return chunks
    

class LabItemsChunkingStrategy(
    BaseChunkingStrategy,
):

    def chunk(
        self,
        schema_name: str,
        table: str,
        df: pd.DataFrame,
    ) -> list[ValueChunk]:

        chunks = []

        grouped = df.groupby(
            [
                "category",
                "fluid",
            ]
        )

        for (
            category,
            fluid,
        ), group in grouped:

            values = group[
                "label"
            ].tolist()

            chunks.append(

                self.build_chunk(
                    schema_name,
                    table,
                    "label",
                    values,
                    metadata={
                        "category": category,
                        "fluid": fluid,
                    },
                )

            )

        return chunks
    

class ItemsChunkingStrategy(
    BaseChunkingStrategy,
):

    def chunk(
        self,
        schema_name: str,
        table: str,
        df: pd.DataFrame,
    ) -> list[ValueChunk]:

        chunks = []

        grouped = df.groupby(
            "category"
        )

        for category, group in grouped:

            values = group[
                "label"
            ].tolist()

            chunks.append(

                self.build_chunk(
                    schema_name,
                    table,
                    "label",
                    values,
                    metadata={
                        "category": category,
                    },
                )

            )

        return chunks