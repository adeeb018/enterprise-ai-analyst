from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from src.config.qdrant import client
from src.config.settings import settings
from src.ingestion.schema_models import EmbeddedChunk

import hashlib


class VectorStore:

    def __init__(self):

        self.client = client

        self.collection = settings.qdrant_collection

    def _generate_point_id(self,chunk_id: str,) -> int:
        """
        Generate a deterministic integer ID for Qdrant.
        """

        return int(
            hashlib.md5(
                chunk_id.encode("utf-8")
            ).hexdigest()[:16],
            16,
        )

    def create_collection(self):

        collections = self.client.get_collections()

        existing = {
            collection.name
            for collection in collections.collections
        }

        if self.collection in existing:

            print("✓ Collection already exists")

            return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(
                size=settings.vector_dimension,
                distance=Distance.COSINE,
            ),
        )

        print("✓ Collection created")

    def upsert(
        self,
        chunks: list[EmbeddedChunk],
    ):

        self.create_collection()

        points = []

        for idx, chunk in enumerate(chunks):

            points.append(
                PointStruct(
                    id=self._generate_point_id(
                        chunk.id
                    ),
                    vector=chunk.embedding,
                    payload={
                        "schema": chunk.schema_name,
                        "table": chunk.table,
                        "text": chunk.text,
                        "keywords": chunk.metadata["keywords"],
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

        print(
            f"✓ Uploaded {len(points)} vectors"
        )

    def count(self):

        count = self.client.count(
            collection_name=self.collection,
            exact=True,
        )

        print(f"Vectors: {count.count}")