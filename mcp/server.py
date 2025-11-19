#!/usr/bin/env python3
"""
MCP Server for RAG Documentation Assistant.

Exposes tools for searching and chatting with documentation
to be used by GitHub Copilot and other MCP clients.
"""
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class SearchDocsArgs(BaseModel):
    """Arguments for search_docs tool."""
    query: str = Field(..., description="The search query")
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters (e.g., {'source_type': 'confluence'})"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return"
    )


class ChatWithDocsArgs(BaseModel):
    """Arguments for chat_with_docs tool."""
    query: str = Field(..., description="The user's question")
    history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Chat history (list of {role, content} dicts)"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters for document sources"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve"
    )


class RAGMCPServer:
    """MCP Server for RAG Documentation Assistant."""

    def __init__(self, backend_url: str = BACKEND_URL):
        self.backend_url = backend_url
        self.server = Server("rag-docs-assistant")
        self.http_client: Optional[httpx.AsyncClient] = None

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_docs",
                    description="Search documentation for relevant information. "
                                "Returns document snippets with metadata and relevance scores.",
                    inputSchema=SearchDocsArgs.model_json_schema()
                ),
                Tool(
                    name="chat_with_docs",
                    description="Have a conversation about the documentation. "
                                "Uses RAG to provide answers based on indexed documents.",
                    inputSchema=ChatWithDocsArgs.model_json_schema()
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_docs":
                    return await self._search_docs(arguments)
                elif name == "chat_with_docs":
                    return await self._chat_with_docs(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _search_docs(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute document search."""
        args = SearchDocsArgs(**arguments)

        # Make request to backend
        request_data = {
            "query": args.query,
            "filters": args.filters or {},
            "top_k": args.top_k
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.backend_url}/api/search",
                json=request_data,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        # Format results
        results = data.get("results", [])
        if not results:
            return [TextContent(
                type="text",
                text="No results found."
            )]

        # Build response text
        response_parts = [f"Found {len(results)} relevant documents:\n"]

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            source_type = metadata.get("source_type", "unknown")
            source_id = metadata.get("source_id", "unknown")
            score = result.get("score", 0.0)

            response_parts.append(f"\n{i}. [Score: {score:.3f}] {source_type}:{source_id}")
            response_parts.append(f"   {result['text'][:200]}...")

            if "url" in metadata:
                response_parts.append(f"   URL: {metadata['url']}")

        return [TextContent(
            type="text",
            text="\n".join(response_parts)
        )]

    async def _chat_with_docs(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute chat with documents."""
        args = ChatWithDocsArgs(**arguments)

        # Make request to backend
        request_data = {
            "query": args.query,
            "history": args.history or [],
            "filters": args.filters or {},
            "top_k": args.top_k
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.backend_url}/api/chat",
                json=request_data,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        # Format response
        answer = data.get("response", "No response generated.")
        sources = data.get("sources", [])

        response_parts = [answer]

        if sources:
            response_parts.append("\n\nSources:")
            for i, source in enumerate(sources[:3], 1):  # Show top 3 sources
                metadata = source.get("metadata", {})
                source_type = metadata.get("source_type", "unknown")
                source_id = metadata.get("source_id", "unknown")
                response_parts.append(f"{i}. {source_type}:{source_id}")
                if "url" in metadata:
                    response_parts.append(f"   {metadata['url']}")

        return [TextContent(
            type="text",
            text="\n".join(response_parts)
        )]

    async def run(self):
        """Run the MCP server."""
        logger.info(f"Starting RAG MCP Server (backend: {self.backend_url})")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    server = RAGMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
