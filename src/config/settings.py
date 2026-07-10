from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    ollama_base_url: str

    ollama_model: str

    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str

    vector_dimension: int

    embedding_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()