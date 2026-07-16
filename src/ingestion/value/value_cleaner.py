import pandas as pd


class ValueCleaner:

    TEXT_COLUMNS = (
        "label",
        "long_title",
        "long_description",
    )

    CATEGORICAL_COLUMNS = (
        "category",
        "fluid",
    )

    def clean(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        #
        # Fill missing categorical values
        #
        for column in self.CATEGORICAL_COLUMNS:

            if column in df.columns:

                df[column] = df[column].fillna(
                    "Uncategorized"
                )

        #
        # Clean text columns
        #
        for column in self.TEXT_COLUMNS:

            if column not in df.columns:
                continue

            #
            # Remove NULL rows
            #
            df = df[
                df[column].notna()
            ]

            #
            # Convert to string
            #
            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

            #
            # Remove empty strings
            #
            df = df[
                df[column] != ""
            ]

        #
        # Remove deleted lab items
        #
        if "label" in df.columns:

            df = df[
                df["label"] != "Delete"
            ]

        return df.reset_index(
            drop=True
        )