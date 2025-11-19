# Quick Start Guide - Open WebUI Variant

Get the RAG Documentation Assistant up and running in minutes with Open WebUI.

## Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for ingestion)
- Node.js 18+ (optional, for React frontend)

## 1. Initial Setup

Run the setup script to configure all components:

```bash
./scripts/setup.sh
```

This will:
- Create `.env` files from examples
- Install frontend dependencies (optional)

## 2. Start Services

Start all Docker services (Postgres, Ollama, Backend, **Open WebUI**):

```bash
./scripts/start.sh
```

This starts:
- **Postgres** + pgvector (port 5432)
- **Ollama** (port 11434)
- **RAG Backend API** (port 8000)
- **Open WebUI** (port 3000) ← Your main interface

## 3. Pull LLM Model

Download the Llama2 model for Ollama:

```bash
docker exec -it rag-ollama ollama pull llama2
```

This may take a few minutes depending on your internet connection.

**Try other models:**
```bash
# Faster, good for testing
docker exec -it rag-ollama ollama pull mistral

# Better for code
docker exec -it rag-ollama ollama pull codellama

# Smaller, faster
docker exec -it rag-ollama ollama pull phi
```

## 4. Access Open WebUI

1. Open **http://localhost:3000** in your browser
2. **Create an account** (first user becomes admin)
3. You'll see the chat interface
4. Try chatting with the LLM!

## 5. Ingest Documentation

Before RAG features work, load some documentation:

### Option A: Ingest Test Markdown Files

```bash
# Create a test docs directory
mkdir -p test-docs
cat > test-docs/api-guide.md <<EOF
# API Guide

## Authentication

Use API keys for authentication. Set the \`Authorization\` header:

\`\`\`
Authorization: Bearer YOUR_API_KEY
\`\`\`

## Endpoints

- \`GET /api/users\` - List users
- \`POST /api/users\` - Create user
- \`GET /api/docs\` - Search documentation
EOF

cat > test-docs/deployment.md <<EOF
# Deployment Guide

## Prerequisites

- Docker 20.10+
- Kubernetes 1.24+
- kubectl configured

## Steps

1. Build the container:
   \`\`\`bash
   docker build -t myapp:latest .
   \`\`\`

2. Deploy to Kubernetes:
   \`\`\`bash
   kubectl apply -f deployment.yaml
   \`\`\`
EOF

# Set up Python environment
cd ingestion
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run ingestion
python ingest.py --source markdown --path ../test-docs

cd ..
```

### Option B: Ingest from Git Repository

```bash
cd ingestion
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Clone and ingest from a docs repository
python ingest.py --source git --path https://github.com/your-org/docs-repo.git

cd ..
```

## 6. Configure RAG Functions in Open WebUI

Now integrate your RAG backend with Open WebUI:

### Step 1: Create Custom Function

1. In Open WebUI, go to **Workspace** → **Functions**
2. Click **Create New Function**
3. Name it "RAG Documentation Search"
4. Paste this code:

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
        top_k: int = 5
    ) -> str:
        """
        Search documentation for relevant information.

        :param query: Search query
        :param top_k: Number of results (default: 5)
        :return: Search results with sources
        """
        try:
            response = requests.post(
                f"{self.backend_url}/api/search",
                json={"query": query, "top_k": top_k, "filters": {}},
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
                results.append(f"{i}. [{score:.3f}] {source}\n{text[:200]}...")

            return "\n\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Error: {str(e)}"

    def chat_with_docs(
        self,
        query: str,
        top_k: int = 5
    ) -> str:
        """
        Ask a question about the documentation.

        :param query: Your question
        :param top_k: Number of documents to retrieve
        :return: Answer with sources
        """
        try:
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={"query": query, "history": [], "top_k": top_k, "filters": {}},
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
                    result.append(f"{i}. {metadata.get('source_type')}:{metadata.get('source_id')}")

            return "\n".join(result)
        except Exception as e:
            return f"Error: {str(e)}"
```

5. Click **Save**
6. **Enable** the function for your workspace

### Step 2: Test RAG Functions

In a new chat:

```
Use search_docs to find information about API authentication
```

You should see results from your ingested documentation!

Try this too:
```
Use chat_with_docs to explain how to deploy the application
```

## 7. Verify Everything Works

### Check Backend Health

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

### Test Search API Directly

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}'
```

### Use Open WebUI

1. Open http://localhost:3000
2. Select a model (e.g., llama2)
3. Type: `search_docs("deployment")`
4. See results from your documentation!

## Using the System

### Regular Chat

- Select any Ollama model from dropdown
- Chat normally with the LLM
- No RAG, just conversation

### RAG-Enhanced Chat

Use the custom functions:
```
search_docs("kubernetes configuration")
chat_with_docs("how do I set up authentication?")
```

### Multi-Model Comparison

1. Click the model dropdown
2. Select multiple models
3. Ask the same question
4. Compare responses side-by-side

## Optional: React Frontend

If you prefer the simple React UI:

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

Both UIs use the same backend and data!

## Common Issues

### Open WebUI can't connect to backend

**Problem**: Functions return "Error: Connection refused"

**Solution**:
```bash
# Check backend is running
docker ps | grep rag-backend

# Check logs
docker logs rag-backend

# Verify network
docker exec -it rag-open-webui ping backend
```

### No models available

**Problem**: Ollama shows no models

**Solution**:
```bash
docker exec -it rag-ollama ollama list
docker exec -it rag-ollama ollama pull llama2
docker restart rag-open-webui
```

### Empty search results

**Problem**: search_docs returns "No results found"

**Solution**:
- Make sure you ingested documentation (step 5)
- Check data exists:
  ```bash
  docker exec -it rag-postgres psql -U rag_user -d rag_db \
    -c "SELECT COUNT(*) FROM rag_embeddings;"
  ```

### Port conflicts

**Problem**: Port 3000, 8000, or 5432 already in use

**Solution**: Edit `docker-compose.yml` to use different ports:
```yaml
ports:
  - "3001:8080"  # Open WebUI
  - "8001:8000"  # Backend
```

## Next Steps

1. **Add More Documents**: Ingest your actual documentation
2. **Create Prompts**: Make reusable prompt templates in Open WebUI
3. **Try Models**: Experiment with mistral, codellama, etc.
4. **Share**: Invite teammates to use Open WebUI
5. **Customize**: Add more custom functions for specific use cases

## Advanced Usage

### MCP Server (GitHub Copilot)

```bash
cd mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure in `~/.config/mcp/settings.json`:
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

See [mcp/README.md](mcp/README.md) for details.

### Scheduled Ingestion

Set up a cron job to regularly update documentation:

```bash
# Add to crontab
0 2 * * * cd /path/to/dev-chatbot/ingestion && ./ingest.sh
```

## Stopping Services

```bash
./scripts/stop.sh
```

To remove all data:
```bash
docker-compose down -v
```

## Documentation

- **[OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md)**: Detailed Open WebUI configuration
- **[planning/hybrid_architecture.md](planning/hybrid_architecture.md)**: Architecture details
- **[README.md](README.md)**: Full documentation

## Support

- Open WebUI docs: https://docs.openwebui.com/
- Backend API: http://localhost:8000/docs
- Check logs: `docker-compose logs -f`

---

**You're all set!** Open http://localhost:3000 and start chatting with your documentation.
