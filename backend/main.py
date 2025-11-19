from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from config import settings
from database import init_db, test_connection
from vector_store import vector_store_manager
from models import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    ChatRequest,
    ChatResponse,
    HealthResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup
    logger.info("Starting up RAG backend...")

    try:
        # Initialize database
        init_db()

        # Initialize vector store components
        vector_store_manager.initialize_embedding_model()
        vector_store_manager.initialize_llm()
        vector_store_manager.initialize_vector_store()
        vector_store_manager.get_or_create_index()

        logger.info("RAG backend startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG backend...")


# Create FastAPI app
app = FastAPI(
    title="RAG Documentation Assistant API",
    description="RAG-based documentation assistant using LlamaIndex, Postgres, and Ollama",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Documentation Assistant API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_status = test_connection()
    vector_store_status = vector_store_manager.vector_store is not None
    llm_status = vector_store_manager.llm is not None

    status = "healthy" if all([db_status, vector_store_status, llm_status]) else "degraded"

    return HealthResponse(
        status=status,
        database=db_status,
        vector_store=vector_store_status,
        llm=llm_status
    )


@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for relevant documents."""
    try:
        logger.info(f"Search request: {request.query}")

        # Get the index
        index = vector_store_manager.get_or_create_index()

        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=request.top_k,
            response_mode="no_text"  # Only return source nodes
        )

        # Execute query
        response = query_engine.query(request.query)

        # Format results
        results = []
        for node in response.source_nodes:
            results.append(SearchResult(
                text=node.node.text,
                score=node.score or 0.0,
                metadata=node.node.metadata or {}
            ))

        return SearchResponse(
            results=results,
            query=request.query
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with documents using RAG."""
    try:
        logger.info(f"Chat request: {request.query}")

        # Get the index and LLM
        index = vector_store_manager.get_or_create_index()
        llm = vector_store_manager.llm

        if llm is None:
            raise HTTPException(status_code=503, detail="LLM not available")

        # Create query engine with chat mode
        query_engine = index.as_query_engine(
            similarity_top_k=request.top_k,
            llm=llm,
            response_mode="compact"
        )

        # Execute query
        response = query_engine.query(request.query)

        # Format sources
        sources = []
        for node in response.source_nodes:
            sources.append(SearchResult(
                text=node.node.text,
                score=node.score or 0.0,
                metadata=node.node.metadata or {}
            ))

        return ChatResponse(
            response=str(response),
            sources=sources,
            query=request.query
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
