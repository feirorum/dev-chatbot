# Quick Start Guide

Get the RAG Documentation Assistant up and running in minutes.

## Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for frontend development)

## 1. Initial Setup

Run the setup script to configure all components:

```bash
./scripts/setup.sh
```

This will:
- Create `.env` files from examples
- Install frontend dependencies

## 2. Start Services

Start all Docker services (Postgres, Ollama, Backend):

```bash
./scripts/start.sh
```

## 3. Pull LLM Model

Download the Llama2 model for Ollama:

```bash
docker exec -it rag-ollama ollama pull llama2
```

This may take a few minutes depending on your internet connection.

## 4. Ingest Documentation

Choose one of the following methods to load your documentation:

### Option A: Ingest Markdown Files

```bash
# Create a test docs directory
mkdir -p test-docs
echo "# Test Document\n\nThis is a test document." > test-docs/test.md

# Set up Python environment
cd ingestion
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run ingestion
python ingest.py --source markdown --path ../test-docs
```

### Option B: Ingest from Git Repository

```bash
cd ingestion
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python ingest.py --source git --path https://github.com/your-org/docs-repo.git
```

## 5. Use the System

### Web Chat UI

1. Install frontend dependencies (if not done in setup):
   ```bash
   cd frontend
   npm install
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Open http://localhost:5173 in your browser

4. Start chatting with your documentation!

### MCP Server (GitHub Copilot)

1. Set up Python environment:
   ```bash
   cd mcp
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure in your MCP settings (`~/.config/mcp/settings.json`):
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

3. Use in GitHub Copilot:
   - `search_docs("how to configure authentication")`
   - `chat_with_docs("explain the deployment process")`

## 6. Verify Everything Works

1. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check API docs:
   Open http://localhost:8000/docs

3. Test search:
   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "top_k": 3}'
   ```

## Common Issues

### Ollama model not found
```bash
docker exec -it rag-ollama ollama pull llama2
```

### Backend connection errors
Check that all services are running:
```bash
docker-compose ps
```

### Empty search results
Make sure you've ingested some documentation (see Step 4)

### Port conflicts
If ports 5432, 8000, or 11434 are in use, edit `docker-compose.yml` to use different ports.

## Next Steps

- Read the full [README.md](README.md)
- See [planning/initial_spec.md](planning/initial_spec.md) for architecture details
- Configure data sources in `ingestion/.env`
- Customize the frontend in `frontend/src/`
- Add more sophisticated retrieval strategies in `backend/`

## Stopping Services

```bash
./scripts/stop.sh
```

To remove all data:
```bash
docker-compose down -v
```
