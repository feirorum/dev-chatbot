# Open WebUI Setup and Configuration Guide

This guide explains how to set up and configure Open WebUI to work with the RAG Documentation Assistant backend.

## What is Open WebUI?

Open WebUI is a feature-rich, self-hosted web interface for LLMs with:
- Multi-model support (Ollama, OpenAI-compatible APIs)
- Advanced RAG capabilities
- User management and sharing
- Custom functions and tools
- MCP (Model Context Protocol) integration
- Prompt templates and workflows

## Quick Start

### 1. Start All Services

```bash
./scripts/setup.sh
./scripts/start.sh
```

This starts:
- Postgres + pgvector (port 5432)
- Ollama (port 11434)
- RAG Backend API (port 8000)
- **Open WebUI (port 3000)**

### 2. Pull an Ollama Model

```bash
docker exec -it rag-ollama ollama pull llama2
# Or try other models:
# docker exec -it rag-ollama ollama pull mistral
# docker exec -it rag-ollama ollama pull codellama
```

### 3. Access Open WebUI

1. Open http://localhost:3000 in your browser
2. Create an admin account (first user is automatically admin)
3. You'll see the chat interface with Ollama models available

## Configuring RAG Backend Integration

Open WebUI can integrate with your RAG backend in two ways:

### Option A: Using Functions/Tools (Recommended)

This approach calls your RAG backend's API from within Open WebUI.

#### 1. Create a Custom Function

In Open WebUI:

1. Go to **Workspace** → **Functions**
2. Click **Create New Function**
3. Use this template:

```python
"""
RAG Documentation Search
Search internal documentation using the RAG backend
"""
import requests
from typing import Optional

class Tools:
    def __init__(self):
        self.backend_url = "http://backend:8000"

    def search_docs(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> str:
        """
        Search documentation for relevant information.

        :param query: Search query
        :param top_k: Number of results to return
        :param filters: Optional filters (e.g., {"source_type": "confluence"})
        :return: Search results with sources
        """
        try:
            response = requests.post(
                f"{self.backend_url}/api/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "filters": filters or {}
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for i, result in enumerate(data.get("results", []), 1):
                metadata = result.get("metadata", {})
                source = f"{metadata.get('source_type', 'unknown')}:{metadata.get('source_id', 'N/A')}"
                score = result.get("score", 0.0)
                text = result.get("text", "")

                results.append(
                    f"{i}. [{score:.3f}] {source}\n{text[:200]}..."
                )

            if not results:
                return "No results found."

            return "\n\n".join(results)

        except Exception as e:
            return f"Error searching docs: {str(e)}"

    def chat_with_docs(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> str:
        """
        Ask a question about the documentation.

        :param query: Your question
        :param top_k: Number of documents to retrieve
        :param filters: Optional filters
        :return: Answer with sources
        """
        try:
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={
                    "query": query,
                    "history": [],
                    "top_k": top_k,
                    "filters": filters or {}
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("response", "No response generated.")
            sources = data.get("sources", [])

            result = [answer]

            if sources:
                result.append("\n\nSources:")
                for i, source in enumerate(sources[:3], 1):
                    metadata = source.get("metadata", {})
                    source_info = f"{metadata.get('source_type', 'unknown')}:{metadata.get('source_id', 'N/A')}"
                    result.append(f"{i}. {source_info}")

            return "\n".join(result)

        except Exception as e:
            return f"Error chatting with docs: {str(e)}"
```

4. Save the function
5. Enable it in your workspace

#### 2. Use the Function in Chat

In any chat:
```
Use the search_docs function to find information about authentication

Use the chat_with_docs function to explain the deployment process
```

Open WebUI will automatically call your RAG backend!

### Option B: Direct Database Access (Advanced)

For this approach, Open WebUI uses its own RAG pipeline but reads from your Postgres/pgvector database.

#### 1. Configure Database Connection

Add to docker-compose.yml:

```yaml
  open-webui:
    environment:
      - DATABASE_URL=postgresql://rag_user:rag_password@postgres:5432/rag_db
```

#### 2. Configure in Open WebUI

1. Go to **Admin Settings** → **Documents**
2. Enable **Use External Vector DB**
3. Configure connection to Postgres
4. Set embedding model to match: `sentence-transformers/all-MiniLM-L6-v2`

**Note**: This is more complex and may require schema adjustments. The Functions approach is simpler and recommended.

## Using Open WebUI

### Basic Chat

1. Select a model from the dropdown (e.g., llama2)
2. Type your message
3. Get responses from Ollama

### Using RAG Functions

Once you've set up the custom functions:

1. In chat, type: `search_docs("kubernetes deployment")`
2. The function calls your RAG backend
3. Results appear in chat
4. Continue conversation with context

### Advanced Features

#### Create Prompt Templates

1. Go to **Workspace** → **Prompts**
2. Create templates for common queries
3. Example: "Search docs and explain: {{topic}}"

#### Share Conversations

1. Click share icon in chat
2. Generate link for teammates
3. Control access permissions

#### Multiple Models

1. Select multiple models from dropdown
2. Ask the same question to all
3. Compare responses

## Ingesting Documentation

Before using RAG features, ingest some documentation:

```bash
# Set up ingestion environment
cd ingestion
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ingest markdown files
python ingest.py --source markdown --path /path/to/docs

# Or ingest from Git
python ingest.py --source git --path https://github.com/org/docs.git
```

## Verifying Integration

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": true,
  "vector_store": true,
  "llm": true
}
```

### 2. Test Search API

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test",
    "top_k": 3
  }'
```

### 3. Test from Open WebUI

In a chat, use your custom function:
```
search_docs("test query")
```

You should see results from your documentation.

## Troubleshooting

### Open WebUI Can't Connect to Backend

**Problem**: Functions return connection errors

**Solution**:
```bash
# Check if backend is running
docker ps | grep rag-backend

# Check logs
docker logs rag-backend

# Verify network
docker exec -it rag-open-webui ping backend
```

### No Models Available

**Problem**: No models show up in Open WebUI

**Solution**:
```bash
# Check Ollama
docker exec -it rag-ollama ollama list

# Pull a model if needed
docker exec -it rag-ollama ollama pull llama2

# Restart Open WebUI
docker restart rag-open-webui
```

### RAG Functions Return Empty Results

**Problem**: search_docs or chat_with_docs return no results

**Solution**:
- Make sure you've ingested documentation (see "Ingesting Documentation")
- Check backend logs: `docker logs rag-backend`
- Verify database has data:
  ```bash
  docker exec -it rag-postgres psql -U rag_user -d rag_db -c "SELECT COUNT(*) FROM rag_embeddings;"
  ```

### Permission Denied Errors

**Problem**: Functions can't call backend API

**Solution**:
- Ensure backend CORS allows requests from Open WebUI
- Check backend logs for authentication errors
- Verify network connectivity between containers

## Best Practices

### 1. Use Functions for RAG
- More flexible than direct DB access
- Easier to maintain
- Better separation of concerns

### 2. Create Prompt Templates
- Standardize common queries
- Make RAG accessible to all users
- Improve consistency

### 3. Monitor Backend
- Watch backend logs
- Set up health checks
- Monitor response times

### 4. Organize Workspaces
- Create workspace for doc search
- Separate from general chat
- Share with team

## Comparison: Open WebUI vs React Frontend

| Feature | Open WebUI | React Frontend |
|---------|-----------|----------------|
| **UI Complexity** | Feature-rich, many options | Simple, focused |
| **User Management** | Built-in, multi-user | None (static) |
| **Model Selection** | Multiple models, easy switch | Fixed (backend) |
| **RAG Functions** | Custom tools, flexible | Built-in search |
| **Sharing** | Share chats, prompts | No sharing |
| **Deployment** | Docker required | Static hosting |
| **Best For** | Power users, teams | Simple use cases |

## Next Steps

1. **Set up custom functions** for RAG integration
2. **Ingest documentation** to populate the knowledge base
3. **Create prompt templates** for common queries
4. **Share with team** and gather feedback
5. **Experiment with models** to find best fit

## Additional Resources

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Open WebUI GitHub](https://github.com/open-webui/open-webui)
- [Ollama Models](https://ollama.ai/library)
- Backend API docs: http://localhost:8000/docs

## Support

For issues with:
- **Open WebUI**: Check Open WebUI docs and GitHub issues
- **RAG Backend**: Check `docker logs rag-backend`
- **Integration**: Review this guide and backend API docs
