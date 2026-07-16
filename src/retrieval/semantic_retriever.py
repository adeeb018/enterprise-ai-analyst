from src.config.qdrant import client
from src.config.settings import settings
from src.embedding.embedding_service import EmbeddingService

from .query_models import RetrievedChunk


class SemanticRetriever:

    def __init__(self):

        self.client = client

        self.collection = settings.qdrant_collection

        self.embedding_service = EmbeddingService()

    def embed_query(
        self,
        question: str,
    ) -> list[float]:

        return self.embedding_service.embed(
            question
        )

    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ):

        response = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=limit,
        )

        return response.points

    def retrieve(
        self,
        question: str,
        limit: int = 5,
    ) -> list[RetrievedChunk]:

        vector = self.embed_query(
            question
        )

        points = self.search(
            vector,
            limit,
        )

        results = []

        for point in points:

            payload = point.payload

            results.append(

                RetrievedChunk(

                    score=point.score,

                    schema_name=payload["schema"],

                    table=payload["table"],

                    text=payload["text"],

                    keywords=payload.get(
                        "keywords",
                        [],
                    ),

                    source="semantic",
                )

            )

        return results