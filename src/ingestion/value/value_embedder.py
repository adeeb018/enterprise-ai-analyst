from tqdm import tqdm

from src.embedding.embedding_service import EmbeddingService

from .value_models import (
    EmbeddedValueChunk,
    ValueChunk,
)


class ValueEmbedder:

    def __init__(
        self,
        batch_size: int = 256,
    ):

        self.embedding_service = EmbeddingService()

        self.batch_size = batch_size

    def embed(
        self,
        chunks: list[ValueChunk],
    ) -> list[EmbeddedValueChunk]:

        if not chunks:
            return []

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings: list[list[float]] = []

        #
        # Embed in batches
        #
        for start in tqdm(
            range(
                0,
                len(texts),
                self.batch_size,
            ),
            desc="Embedding",
            leave=False,
        ):

            batch = texts[
                start : start + self.batch_size
            ]

            batch_embeddings = (
                self.embedding_service.embed_batch(
                    batch
                )
            )

            embeddings.extend(
                batch_embeddings
            )

        embedded_chunks = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            embedded_chunks.append(

                EmbeddedValueChunk(

                    **chunk.model_dump(),

                    embedding=embedding,

                )

            )

        return embedded_chunks