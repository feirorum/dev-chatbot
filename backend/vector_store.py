from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from config import settings
import logging

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector store initialization and operations."""

    def __init__(self):
        self.vector_store = None
        self.index = None
        self.embed_model = None
        self.llm = None

    def initialize_embedding_model(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.embeddings_model}")
            self.embed_model = HuggingFaceEmbedding(
                model_name=settings.embeddings_model
            )
            logger.info("Embedding model loaded successfully")
            return self.embed_model
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def initialize_llm(self):
        """Initialize the LLM."""
        try:
            logger.info(f"Initializing Ollama LLM: {settings.ollama_model}")
            self.llm = Ollama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
                request_timeout=120.0
            )
            logger.info("LLM initialized successfully")
            return self.llm
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise

    def initialize_vector_store(self):
        """Initialize the pgvector store."""
        try:
            logger.info("Initializing PGVector store")

            self.vector_store = PGVectorStore.from_params(
                database=settings.postgres_db,
                host=settings.postgres_host,
                password=settings.postgres_password,
                port=settings.postgres_port,
                user=settings.postgres_user,
                table_name="rag_embeddings",
                embed_dim=settings.embedding_dim,
            )

            logger.info("Vector store initialized successfully")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def get_or_create_index(self):
        """Get or create the vector store index."""
        try:
            if self.vector_store is None:
                self.initialize_vector_store()

            if self.embed_model is None:
                self.initialize_embedding_model()

            logger.info("Creating vector store index")
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )

            # Try to load existing index or create new one
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    embed_model=self.embed_model
                )
                logger.info("Loaded existing index")
            except Exception:
                self.index = VectorStoreIndex(
                    nodes=[],
                    storage_context=storage_context,
                    embed_model=self.embed_model
                )
                logger.info("Created new index")

            return self.index
        except Exception as e:
            logger.error(f"Error getting/creating index: {e}")
            raise


# Global instance
vector_store_manager = VectorStoreManager()
