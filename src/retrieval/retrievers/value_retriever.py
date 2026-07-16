from src.config.settings import settings

from .base import BaseRetriever
from src.retrieval.query_models import RetrievedChunk

class ValueRetriever(BaseRetriever):
    def __init__(self):
        # Point to your specific value collection
        super().__init__(collection_name=settings.qdrant_value_collection)

    def retrieve(self, question: str, limit: int = 5) -> list[RetrievedChunk]:
        # 1. Reuse the embedding logic from BaseRetriever
        vector = self.embed_query(question)
        
        # 2. Reuse the search logic from BaseRetriever
        points = self.search(vector, limit)
        
        results = []
        for point in points:
            payload = point.payload
            
            # 3. Extract the 'matched_value' (the code/item found in the chunk)
            # This relies on the structure we built in the ingestion pipeline
            results.append(
                RetrievedChunk(
                    score=point.score,
                    schema_name=payload.get("schema", ""),
                    table=payload.get("table", ""),
                    text=payload.get("text", ""),
                    keywords=[], # Value chunks use the 'text' for context
                    source="value",
                    # This matched_value is key for the SQL-Generator to resolve the exact code
                    matched_value=payload.get("matched_value") 
                )
            )
        
        return results