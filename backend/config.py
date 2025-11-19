from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag_db"
    postgres_user: str = "rag_user"
    postgres_password: str = "rag_password"

    # LLM Configuration
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Embeddings Configuration
    embeddings_provider: str = "local"
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector Store Configuration
    vector_store: str = "pgvector"
    embedding_dim: int = 384

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = '["http://localhost:5173"]'

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
