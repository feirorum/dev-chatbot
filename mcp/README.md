# MCP Server for RAG Documentation Assistant

This MCP server exposes documentation search and chat capabilities to GitHub Copilot and other MCP clients.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env to point to your backend API
```

## Usage

### Running the Server

```bash
python server.py
```

The server runs on stdio and communicates via the MCP protocol.

### Configuring with GitHub Copilot

Add to your MCP settings (usually in `~/.config/mcp/settings.json`):

```json
{
  "mcpServers": {
    "rag-docs": {
      "command": "python",
      "args": ["/path/to/dev-chatbot/mcp/server.py"],
      "env": {
        "BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Available Tools

### search_docs

Search documentation for relevant information.

**Parameters:**
- `query` (string, required): The search query
- `filters` (object, optional): Filter by source type, etc.
- `top_k` (integer, optional): Number of results (default: 5)

**Example:**
```python
search_docs(
    query="How do I configure authentication?",
    filters={"source_type": "confluence"},
    top_k=3
)
```

### chat_with_docs

Have a conversation about the documentation using RAG.

**Parameters:**
- `query` (string, required): Your question
- `history` (array, optional): Previous chat messages
- `filters` (object, optional): Filter by source type, etc.
- `top_k` (integer, optional): Number of documents to retrieve (default: 5)

**Example:**
```python
chat_with_docs(
    query="What are the best practices for error handling?",
    top_k=5
)
```

## Architecture

The MCP server acts as a thin wrapper around the RAG backend API:

```
GitHub Copilot -> MCP Server -> Backend API -> Vector Store
```

All heavy lifting (embedding, retrieval, LLM inference) happens in the backend.
