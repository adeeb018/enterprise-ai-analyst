from src.retrieval.query_models import RetrievedChunk


class RetrievalMerger:

    def merge(
        self,
        semantic: list[RetrievedChunk],
        value: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:

        merged = {}

        #
        # Semantic first
        #
        for result in semantic:

            table_id = (
                f"{result.schema_name}.{result.table}"
            )

            merged[table_id] = result

        #
        # Add value tables if unseen
        #
        for result in value:

            table_id = (
                f"{result.schema_name}.{result.table}"
            )

            if table_id not in merged:

                merged[table_id] = result

        return list(
            merged.values()
        )