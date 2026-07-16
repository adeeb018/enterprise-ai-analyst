import time

from src.ingestion.schema_models import TableInfo

from .value_chunker import ValueChunker
from .value_cleaner import ValueCleaner
from .value_embedder import ValueEmbedder
from .value_extractor import ValueExtractor
from .value_vector_store import ValueVectorStore


class ValuePipeline:

    def __init__(self):

        self.extractor = ValueExtractor()

        self.cleaner = ValueCleaner()

        self.chunker = ValueChunker()

        self.embedder = ValueEmbedder()

        self.vector_store = ValueVectorStore()

    def ingest(
        self,
        schema: list[TableInfo],
    ):

        embedded_chunks = []

        total_start = time.perf_counter()

        for table in schema:

            #
            # Skip non lookup tables
            #
            if not table.table.startswith("d_"):
                continue

            print()
            print("=" * 70)
            print(f"Processing {table.table}")
            print("=" * 70)

            table_start = time.perf_counter()

            #
            # Extract
            #
            start = time.perf_counter()

            df = self.extractor.extract(table)

            extract_time = time.perf_counter() - start

            print(
                f"Extract      : {extract_time:.2f}s "
                f"({len(df):,} rows)"
            )

            #
            # Clean
            #
            start = time.perf_counter()

            df = self.cleaner.clean(df)

            clean_time = time.perf_counter() - start

            print(
                f"Clean        : {clean_time:.2f}s "
                f"({len(df):,} rows)"
            )

            #
            # Chunk
            #
            start = time.perf_counter()

            chunks = self.chunker.chunk(
                table,
                df,
            )

            chunk_time = time.perf_counter() - start

            print(
                f"Chunk        : {chunk_time:.2f}s "
                f"({len(chunks):,} chunks)"
            )

            #
            # Embed
            #
            start = time.perf_counter()

            embedded = self.embedder.embed(
                chunks
            )

            embed_time = time.perf_counter() - start

            print(
                f"Embed        : {embed_time:.2f}s "
                f"({len(embedded):,} embeddings)"
            )

            embedded_chunks.extend(
                embedded
            )

            table_time = time.perf_counter() - table_start

            print("-" * 70)
            print(
                f"Table Total  : {table_time:.2f}s"
            )

        #
        # Upload
        #
        print()
        print("=" * 70)
        print("Uploading to Qdrant")
        print("=" * 70)

        start = time.perf_counter()

        self.vector_store.upsert(
            embedded_chunks
        )

        upload_time = time.perf_counter() - start

        total_time = time.perf_counter() - total_start

        print()
        print("=" * 70)
        print("VALUE INGESTION SUMMARY")
        print("=" * 70)
        print(f"Total Chunks : {len(embedded_chunks):,}")
        print(f"Upload Time  : {upload_time:.2f}s")
        print(f"Total Time   : {total_time:.2f}s")