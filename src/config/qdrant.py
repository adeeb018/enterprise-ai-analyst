from qdrant_client import QdrantClient

from src.config.settings import settings

client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)