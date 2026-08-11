# src/embedding/embedding_service.py
import threading
from sentence_transformers import SentenceTransformer
from src.config.settings import settings

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        print(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self._lock = threading.Lock()
        self._initialized = True

    def embed(self, text: str) -> list[float]:
        with self._lock:
            return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        with self._lock:
            return self.model.encode(texts, normalize_embeddings=True).tolist()