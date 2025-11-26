from pydantic_settings import BaseSettings
from typing import Optional


class IngestionSettings(BaseSettings):
    # Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag_db"
    postgres_user: str = "rag_user"
    postgres_password: str = "rag_password"

    # Embeddings Configuration
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Confluence Configuration
    confluence_url: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_api_token: Optional[str] = None
    confluence_space_key: Optional[str] = None

    # Git Repository Configuration
    git_repo_url: Optional[str] = None
    git_repo_path: Optional[str] = "./repos"

    # Markdown Files Configuration
    markdown_docs_path: Optional[str] = "./docs"

    # Chunking Configuration
    chunk_size: int = 1024
    chunk_overlap: int = 200

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = IngestionSettings()
