import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    # Cloud Provider Settings (OpenRouter / OpenAI compatible)
    llm_api_base: str
    llm_api_key: str
    llm_model: str

    gemini_llm_api_key: str
    gemini_llm_api_base: str
    gemini_llm_model: str

    ollama_base_url: str
    ollama_model: str

    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str

    qdrant_value_collection: str

    vector_dimension: int

    embedding_model: str

    mcp_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()