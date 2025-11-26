#!/usr/bin/env python3
"""
Main ingestion script for loading documents into the RAG system.
"""
import logging
from pathlib import Path
from typing import List, Optional
import argparse

from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import SimpleDirectoryReader

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentIngester:
    """Handles document ingestion into the RAG system."""

    def __init__(self):
        self.embed_model = None
        self.vector_store = None
        self.index = None

    def initialize(self):
        """Initialize embedding model and vector store."""
        logger.info("Initializing ingestion components...")

        # Initialize embedding model
        logger.info(f"Loading embedding model: {settings.embeddings_model}")
        self.embed_model = HuggingFaceEmbedding(
            model_name=settings.embeddings_model
        )

        # Initialize vector store
        logger.info("Connecting to vector store...")
        self.vector_store = PGVectorStore.from_params(
            database=settings.postgres_db,
            host=settings.postgres_host,
            password=settings.postgres_password,
            port=settings.postgres_port,
            user=settings.postgres_user,
            table_name="rag_embeddings",
            embed_dim=settings.embedding_dim,
        )

        logger.info("Ingestion components initialized")

    def ingest_markdown_files(self, directory: str) -> int:
        """
        Ingest markdown files from a directory.

        Args:
            directory: Path to directory containing markdown files

        Returns:
            Number of documents ingested
        """
        logger.info(f"Ingesting markdown files from: {directory}")

        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return 0

        # Load documents
        reader = SimpleDirectoryReader(
            input_dir=str(dir_path),
            required_exts=[".md", ".markdown"],
            recursive=True
        )
        documents = reader.load_data()

        if not documents:
            logger.warning(f"No markdown files found in {directory}")
            return 0

        # Add metadata
        for doc in documents:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata["source_type"] = "markdown"
            doc.metadata["source_id"] = doc.metadata.get("file_path", "unknown")

        # Ingest documents
        return self._ingest_documents(documents)

    def ingest_git_repo(self, repo_url: str, clone_path: Optional[str] = None) -> int:
        """
        Clone and ingest documentation from a Git repository.

        Args:
            repo_url: URL of the Git repository
            clone_path: Optional path to clone to

        Returns:
            Number of documents ingested
        """
        logger.info(f"Ingesting from Git repo: {repo_url}")

        import git
        from tempfile import mkdtemp

        # Determine clone path
        if clone_path is None:
            clone_path = mkdtemp(prefix="rag_git_")

        clone_path_obj = Path(clone_path)

        try:
            # Clone repository
            logger.info(f"Cloning repository to: {clone_path}")
            git.Repo.clone_from(repo_url, clone_path)

            # Look for common documentation directories
            doc_dirs = ["docs", "documentation", "doc"]
            documents = []

            for doc_dir in doc_dirs:
                doc_path = clone_path_obj / doc_dir
                if doc_path.exists():
                    logger.info(f"Found documentation directory: {doc_dir}")
                    reader = SimpleDirectoryReader(
                        input_dir=str(doc_path),
                        required_exts=[".md", ".markdown", ".rst", ".txt"],
                        recursive=True
                    )
                    docs = reader.load_data()
                    documents.extend(docs)

            # Add metadata
            for doc in documents:
                if doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["source_type"] = "git"
                doc.metadata["source_id"] = repo_url
                doc.metadata["url"] = repo_url

            return self._ingest_documents(documents)

        except Exception as e:
            logger.error(f"Error ingesting from Git repo: {e}")
            return 0

    def _ingest_documents(self, documents: List[Document]) -> int:
        """
        Internal method to ingest documents into the vector store.

        Args:
            documents: List of documents to ingest

        Returns:
            Number of documents ingested
        """
        if not documents:
            logger.warning("No documents to ingest")
            return 0

        logger.info(f"Processing {len(documents)} documents...")

        # Create node parser
        node_parser = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        # Parse documents into nodes
        nodes = node_parser.get_nodes_from_documents(documents)
        logger.info(f"Created {len(nodes)} nodes from documents")

        # Create or update index
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        if self.index is None:
            logger.info("Creating new index...")
            self.index = VectorStoreIndex(
                nodes=nodes,
                storage_context=storage_context,
                embed_model=self.embed_model,
                show_progress=True
            )
        else:
            logger.info("Adding nodes to existing index...")
            for node in nodes:
                self.index.insert_nodes([node])

        logger.info(f"Successfully ingested {len(documents)} documents ({len(nodes)} nodes)")
        return len(documents)


def main():
    """Main entry point for ingestion script."""
    parser = argparse.ArgumentParser(description="Ingest documents into RAG system")
    parser.add_argument(
        "--source",
        choices=["markdown", "git"],
        required=True,
        help="Source type to ingest from"
    )
    parser.add_argument(
        "--path",
        help="Path to markdown directory or Git repository URL"
    )

    args = parser.parse_args()

    # Initialize ingester
    ingester = DocumentIngester()
    ingester.initialize()

    # Ingest based on source type
    count = 0
    if args.source == "markdown":
        path = args.path or settings.markdown_docs_path
        if path:
            count = ingester.ingest_markdown_files(path)
        else:
            logger.error("No path specified for markdown ingestion")
    elif args.source == "git":
        url = args.path or settings.git_repo_url
        if url:
            count = ingester.ingest_git_repo(url)
        else:
            logger.error("No URL specified for git ingestion")

    logger.info(f"Ingestion complete: {count} documents processed")


if __name__ == "__main__":
    main()
