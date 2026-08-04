from sentence_transformers import SentenceTransformer
from src.config.settings import settings

class EmbeddingService:
    # Class-level variable to hold the single instance
    _instance = None

    def __new__(cls):
        # If no instance exists, create it
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize the model if it hasn't been done yet
        if self._initialized:
            return
            
        print(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self._initialized = True

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()