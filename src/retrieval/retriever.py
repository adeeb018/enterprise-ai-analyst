from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retrievers.semantic_retriever import SemanticRetriever
from src.retrieval.retrievers.value_retriever import ValueRetriever
from src.retrieval.retrieval_merger import RetrievalMerger
from src.embedding.embedding_service import EmbeddingService

class Retriever:
    def __init__(self):
        # Initializing the embedding service once for the orchestrator
        self.embedding_service = EmbeddingService()
        
        # Initializing the searchers
        self.semantic = SemanticRetriever()
        self.value = ValueRetriever()
        
        # Initializing the merger
        self.merger = RetrievalMerger()

    def retrieve(self, question: str, limit: int = 5):
        vector = self.embedding_service.embed(question)
        
        # 1. Get raw search results from Qdrant
        semantic_points = self.semantic.search(vector, limit)
        value_points = self.value.search(vector, limit)
        
        # 2. CONVERT points to RetrievedChunk objects
        semantic_chunks = [self._to_retrieved_chunk(p, "semantic") for p in semantic_points]
        value_chunks = [self._to_retrieved_chunk(p, "value") for p in value_points]
        
        # 3. Merge the CHUNKS (this matches your merger signature)
        return self.merger.merge(semantic_chunks, value_chunks)

    def _to_retrieved_chunk(self, point, source: str) -> RetrievedChunk:
        """Helper to convert Qdrant points to your Pydantic models."""
        payload = point.payload
        return RetrievedChunk(
            score=point.score,
            schema_name=payload.get("schema", ""),
            table=payload.get("table", ""),
            text=payload.get("text", ""),
            keywords=payload.get("keywords", []),
            source=source
        )