from abc import ABC, abstractmethod
from src.config.qdrant import client
from src.embedding.embedding_service import EmbeddingService
from src.retrieval.query_models import RetrievedChunk

class BaseRetriever(ABC):
    def __init__(self, collection_name: str):
        self.client = client
        self.collection = collection_name
        self.embedding_service = EmbeddingService()

    def embed_query(self, question: str) -> list[float]:
        """Shared logic to embed a query string."""
        return self.embedding_service.embed(question)

    def search(self, vector: list[float], limit: int = 5):
        """Shared logic to query the vector store."""
        response = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=limit,
        )
        return response.points

    @abstractmethod
    def retrieve(self, question: str, limit: int = 5) -> list[RetrievedChunk]:
        """Each subclass must implement its own logic to process search results."""
        pass