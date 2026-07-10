from sentence_transformers import SentenceTransformer

from src.retrieval.chunker import SchemaChunker
from src.retrieval.schema_models import Chunk, EmbeddedChunk


class SchemaEmbedder:
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:
        """
        Generate embeddings for a list of chunks.
        """
        embeddings = self.model.encode(
            [chunk.text for chunk in chunks],
            normalize_embeddings=True,
        )

        embedded_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(
                EmbeddedChunk(
                    **chunk.model_dump(),
                    embedding=embedding.tolist(),
                )
            )
        return embedded_chunks