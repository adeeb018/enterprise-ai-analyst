from src.config.settings import settings

from .base import BaseRetriever
from src.retrieval.query_models import RetrievedChunk

class SemanticRetriever(BaseRetriever):
    def __init__(self):
        super().__init__(collection_name=settings.qdrant_collection)

    def retrieve(self, question: str, limit: int = 5) -> list[RetrievedChunk]:
        vector = self.embed_query(question)
        points = self.search(vector, limit)
        
        return [
            RetrievedChunk(
                score=p.score,
                schema_name=p.payload["schema"],
                table=p.payload["table"],
                text=p.payload["text"],
                keywords=p.payload.get("keywords", []),
                source="semantic"
            ) for p in points
        ]