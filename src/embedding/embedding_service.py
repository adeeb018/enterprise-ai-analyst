import math
import threading

from src.config.settings import settings


def normalize(vector: list[float]) -> list[float]:

    norm = math.sqrt(
        sum(value * value for value in vector)
    )

    if norm == 0:
        return vector

    return [
        value / norm
        for value in vector
    ]


class EmbeddingService:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._initialized = False

        return cls._instance

    def __init__(self):

        if self._initialized:
            return

        self._lock = threading.Lock()

        self.provider = settings.embedding_provider
        self.model_name = settings.embedding_model

        self.model = None
        self.client = None

        if self.provider == "hf":

            from huggingface_hub import InferenceClient

            if not settings.hf_token:
                raise ValueError(
                    "HF_TOKEN is required when "
                    "EMBEDDING_PROVIDER=hf"
                )

            print(
                "Using Hugging Face embedding model: "
                f"{self.model_name}"
            )

            self.client = InferenceClient(
                provider="hf-inference",
                api_key=settings.hf_token,
            )

        elif self.provider == "local":

            from sentence_transformers import (
                SentenceTransformer,
            )

            print(
                "Loading local embedding model: "
                f"{self.model_name}"
            )

            self.model = SentenceTransformer(
                self.model_name
            )

        else:

            raise ValueError(
                f"Unsupported embedding provider: "
                f"{self.provider}"
            )

        self._initialized = True

    def embed(
        self,
        text: str,
    ) -> list[float]:

        with self._lock:

            if self.provider == "hf":

                result = self.client.feature_extraction(
                    text,
                    model=self.model_name,
                )

                vector = result.tolist()

                return normalize(vector)

            return self.model.encode(
                text,
                normalize_embeddings=True,
            ).tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        with self._lock:

            if self.provider == "hf":

                vectors = []

                for text in texts:

                    result = (
                        self.client.feature_extraction(
                            text,
                            model=self.model_name,
                        )
                    )

                    vector = result.tolist()

                    vectors.append(
                        normalize(vector)
                    )

                return vectors

            return self.model.encode(
                texts,
                normalize_embeddings=True,
            ).tolist()