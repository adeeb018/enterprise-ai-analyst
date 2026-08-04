import hashlib

from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from src.config.qdrant import client
from src.config.settings import settings

from .value_models import EmbeddedValueChunk

from tqdm import tqdm


class ValueVectorStore:

    def __init__(self):

        self.client = client

        self.collection = (
            settings.qdrant_value_collection
        )

    def _generate_point_id(
        self,
        chunk_id: str,
    ) -> int:

        return int(

            hashlib.md5(
                chunk_id.encode()
            ).hexdigest()[:16],

            16,

        )

    def create_collection(
        self,
    ):

        collections = self.client.get_collections()

        existing = {
            c.name
            for c in collections.collections
        }

        if self.collection in existing:

            return

        self.client.create_collection(

            collection_name=self.collection,

            vectors_config=VectorParams(

                size=settings.vector_dimension,

                distance=Distance.COSINE,

            ),

        )

    def upsert(
        self,
        chunks: list[EmbeddedValueChunk],
    ):

        self.create_collection()

        points = []

        for chunk in chunks:

            points.append(

                PointStruct(

                    id=self._generate_point_id(
                        chunk.id,
                    ),

                    vector=chunk.embedding,

                    payload={
                        "schema": chunk.schema_name,
                        "table": chunk.table,
                        "column": chunk.column,
                        "text": chunk.text,
                        "values": chunk.values,
                        "metadata": chunk.metadata,
                    },

                )

            )

        BATCH_SIZE = 500

        print(
            f"\nUploading {len(points):,} vectors..."
        )

        for start in tqdm(
            range(
                0,
                len(points),
                BATCH_SIZE,
            ),
            desc="Uploading to Qdrant",
        ):

            batch = points[
                start:start + BATCH_SIZE
            ]

            self.client.upsert(
                collection_name=self.collection,
                points=batch,
            )

        print(
            f"\nUploaded {len(points):,} value vectors."
        )