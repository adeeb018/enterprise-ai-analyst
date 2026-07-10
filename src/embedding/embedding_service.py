from sentence_transformers import SentenceTransformer
from src.config.settings import settings


class EmbeddingService:

    def __init__(
        self,
    ):
        print(f"Loading embedding model: {settings.embedding_model}")

        self.model = SentenceTransformer(settings.embedding_model)

    def embed(
        self,
        text: str,
    ) -> list[float]:

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()