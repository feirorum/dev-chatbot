from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    source_type: str = Field(..., description="Type of source (confluence, git, markdown)")
    source_id: str = Field(..., description="Unique identifier for the source")
    title: Optional[str] = Field(None, description="Document title")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    url: Optional[str] = Field(None, description="URL or path to document")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Filter criteria")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):
    """Single search result."""
    text: str = Field(..., description="Document text")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class SearchResponse(BaseModel):
    """Response model for document search."""
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    query: str = Field(..., description="Original query")


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat."""
    query: str = Field(..., description="User query")
    history: List[ChatMessage] = Field(default_factory=list, description="Chat history")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Filter criteria")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")


class ChatResponse(BaseModel):
    """Response model for chat."""
    response: str = Field(..., description="Assistant response")
    sources: List[SearchResult] = Field(default_factory=list, description="Source documents used")
    query: str = Field(..., description="Original query")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    database: bool = Field(..., description="Database connection status")
    vector_store: bool = Field(..., description="Vector store status")
    llm: bool = Field(..., description="LLM availability")
