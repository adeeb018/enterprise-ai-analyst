from collections import defaultdict

import pandas as pd


class ChunkMerger:

    def merge(
        self,
        chunks: dict[str, pd.DataFrame],
        code_column: str,
        min_chunk_size: int = 10,
    ) -> dict[str, pd.DataFrame]:

        grouped = defaultdict(list)

        for key, df in chunks.items():

            root = df.iloc[0][code_column][:3]

            grouped[root].append(
                (key, df)
            )

        merged = {}

        for root, items in grouped.items():

            buffer = []

            size = 0

            index = 0

            items.sort(
                key=lambda x: len(x[1])
            )

            for key, df in items:

                if len(df) >= min_chunk_size:

                    merged[key] = df

                    continue

                buffer.append(df)

                size += len(df)

                if size >= min_chunk_size:

                    merged[
                        f"{root}_{index}"
                    ] = pd.concat(buffer)

                    buffer = []

                    size = 0

                    index += 1

            if buffer:

                merged[
                    f"{root}_remaining"
                ] = pd.concat(buffer)

        return merged