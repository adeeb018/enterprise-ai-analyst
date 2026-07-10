from src.embedding.embedding_service import EmbeddingService
from src.ingestion.schema_models import Chunk, EmbeddedChunk


class SchemaEmbedder:

    def __init__(self):

        self.embedding_service = EmbeddingService()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:

        embeddings = self.embedding_service.embed_batch(
            [chunk.text for chunk in chunks]
        )

        embedded_chunks = []

        for chunk, embedding in zip(chunks, embeddings):

            embedded_chunks.append(
                EmbeddedChunk(
                    **chunk.model_dump(),
                    embedding=embedding,
                )
            )

        return embedded_chunks