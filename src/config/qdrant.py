from qdrant_client import QdrantClient

from src.config.settings import settings

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
)