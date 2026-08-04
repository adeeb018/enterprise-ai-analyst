from collections import defaultdict

import pandas as pd


class HierarchySplitter:
    """
    Generic hierarchy-based dataframe splitter.

    Used for:
        - ICD Diagnoses
        - ICD Procedures
        - HCPCS
        - Any prefix-based coding system
    """

    def split(
        self,
        df: pd.DataFrame,
        code_column: str,
        max_chunk_size: int = 40,
        initial_depth: int = 3,
    ) -> dict[str, pd.DataFrame]:

        return self._recursive_split(
            df=df,
            code_column=code_column,
            depth=initial_depth,
            max_chunk_size=max_chunk_size,
        )

    def _recursive_split(
        self,
        df: pd.DataFrame,
        code_column: str,
        depth: int,
        max_chunk_size: int,
    ) -> dict[str, pd.DataFrame]:

        #
        # Stop condition
        #
        if (
            len(df) <= max_chunk_size
            or depth > 6
        ):

            key = df.iloc[0][code_column][:depth]

            return {
                key: df
            }

        chunks = {}

        grouped = df.groupby(
            df[code_column].str[:depth]
        )

        for prefix, group in grouped:

            chunks.update(

                self._recursive_split(
                    group,
                    code_column,
                    depth + 1,
                    max_chunk_size,
                )

            )

        return chunks