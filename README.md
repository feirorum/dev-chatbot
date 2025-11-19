# RAG Documentation Assistant - Open WebUI Variant

A modular RAG-based documentation assistant for developers using LlamaIndex, Postgres, and Ollama, with **Open WebUI** as the primary interface.

## What's Different in This Variant?

This branch uses [Open WebUI](https://github.com/open-webui/open-webui) as the main user interface instead of the custom React frontend. Open WebUI provides:

- **Feature-rich UI**: Advanced chat interface with multi-model support
- **User Management**: Built-in authentication and sharing
- **Custom Functions**: Easy integration with RAG backend via Python functions
- **Prompt Templates**: Reusable prompts and workflows
- **MCP Integration**: Native Model Context Protocol support
- **Production-Ready**: Battle-tested, actively maintained

The Phase 1 backend, ingestion, and MCP server remain **exactly the same** - only the frontend changes.

## Architecture

### Hybrid Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Data Sources                          │
│  Confluence │ Git Repos │ Markdown Files │ (Future: Jira)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Ingestion Worker (LlamaIndex)                   │
│  Load → Normalize → Chunk → Embed → Upsert                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Postgres + pgvector (Vector Store)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         RAG Backend API (FastAPI + LlamaIndex)               │
│         /api/chat  │  /api/search  │  /health                │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────┐      ┌─────────────┐    ┌──────────────┐
│   Open   │      │  MCP Server │    │ React UI     │
│  WebUI   │      │  (Copilot)  │    │ (optional)   │
│ :3000    │      │             │    │ :5173        │
└──────────┘      └─────────────┘    └──────────────┘
       │
       └─────────► Ollama (LLMs) ◄────────────────────┘
                      :11434
```

### Components

- **Backend**: FastAPI + LlamaIndex for RAG operations
- **Vector Store**: Postgres with pgvector extension
- **LLM**: Ollama (local) with future support for Vertex AI
- **Ingestion**: LlamaIndex loaders for Confluence, Git repos, and Markdown files
- **MCP Server**: Python MCP server for GitHub Copilot integration
- **Frontend**: **Open WebUI** (feature-rich web interface)
- **Alternative**: React/Vite static web chat (still available)

## Project Structure

```
.
├── planning/              # Project specifications and planning docs
│   ├── initial_spec.md    # Phase 1 specification
│   └── hybrid_architecture.md  # Hybrid design with Open WebUI
├── backend/               # FastAPI + LlamaIndex RAG backend
├── ingestion/             # Data ingestion scripts
├── mcp/                   # MCP server for GitHub Copilot
├── frontend/              # React/Vite web chat UI (optional)
├── scripts/               # Setup and management scripts
├── docker-compose.yml     # Includes Open WebUI service
├── QUICKSTART.md          # Quick start guide
└── OPENWEBUI_SETUP.md     # Open WebUI configuration guide
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for ingestion and MCP)
- Node.js 18+ (optional, for React frontend)

### 1. Initial Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd dev-chatbot

# Run setup script
./scripts/setup.sh
```

### 2. Start All Services

```bash
./scripts/start.sh
```

This starts:
- **Postgres** + pgvector (port 5432)
- **Ollama** (port 11434)
- **RAG Backend** (port 8000)
- **Open WebUI** (port 3000) ← **Main UI**

### 3. Pull an LLM Model

```bash
docker exec -it rag-ollama ollama pull llama2

# Or try other models:
# docker exec -it rag-ollama ollama pull mistral
# docker exec -it rag-ollama ollama pull codellama
```

### 4. Access Open WebUI

1. Open **http://localhost:3000**
2. Create admin account (first user becomes admin)
3. Start chatting!

### 5. Ingest Documentation

Before RAG features work, load some documentation:

```bash
cd ingestion
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ingest markdown files
python ingest.py --source markdown --path /path/to/docs

# Or from Git repository
python ingest.py --source git --path https://github.com/your-org/docs.git
```

### 6. Configure RAG Integration

See **[OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md)** for detailed instructions on:
- Creating custom functions to call RAG backend
- Setting up search and chat tools
- Configuring prompt templates

## Key Differences from Main Branch

| Aspect | Main Branch | This Branch |
|--------|-------------|-------------|
| **Primary UI** | Custom React app | Open WebUI |
| **User Management** | None | Built-in |
| **Authentication** | None | Yes |
| **Multi-Model** | Backend-controlled | User selects |
| **Functions/Tools** | Limited | Extensible |
| **Deployment** | GitHub Pages (static) | Docker (dynamic) |
| **Best For** | Simple, embedded use | Full-featured console |

## Using the System

### Via Open WebUI (Primary)

1. **Direct Chat**: Use any Ollama model for general questions
2. **RAG Search**: Configure custom function to search docs
3. **RAG Chat**: Ask questions about your documentation
4. **Multi-Model**: Compare responses across models
5. **Share**: Share conversations with teammates

### Via MCP Server (GitHub Copilot)

```bash
cd mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Configure in `~/.config/mcp/settings.json` - see [mcp/README.md](mcp/README.md)

### Via React Frontend (Optional)

The simple React UI is still available:

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide
- **[OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md)**: Open WebUI configuration
- **[planning/hybrid_architecture.md](planning/hybrid_architecture.md)**: Architecture details
- **[planning/initial_spec.md](planning/initial_spec.md)**: Phase 1 specification

## API Endpoints

The backend provides these endpoints (see http://localhost:8000/docs):

- `POST /api/search`: Search documentation
- `POST /api/chat`: Chat with documentation
- `GET /health`: Health check

## Service URLs

When running locally:

- **Open WebUI**: http://localhost:3000 (main interface)
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **React UI**: http://localhost:5173 (optional)
- **Postgres**: localhost:5432
- **Ollama**: localhost:11434

## Stopping Services

```bash
./scripts/stop.sh
```

To remove all data:
```bash
docker-compose down -v
```

## Migration Path

### From Main Branch

The backend and ingestion are identical, so:

1. Switch branch: `git checkout claude/openwebui-variant-*`
2. Run: `./scripts/start.sh`
3. Access Open WebUI at http://localhost:3000
4. Your existing data in Postgres will work as-is

### To Production (Vertex AI)

When ready to migrate from Ollama to Vertex AI:

1. Update backend `.env`:
   ```
   LLM_PROVIDER=vertex
   EMBEDDINGS_PROVIDER=vertex
   ```
2. Add Vertex AI credentials
3. Restart backend
4. **No changes needed** to Open WebUI, MCP, or React UI

## Advantages of This Variant

### For Development
- **Faster Iteration**: No need to rebuild React app
- **Rich Tooling**: Built-in prompt management, model testing
- **Better DX**: User-friendly interface for developers

### For Production
- **User Management**: Authentication and authorization built-in
- **Sharing**: Share insights with team
- **Monitoring**: Track usage and conversations
- **Extensibility**: Add custom functions easily

### For Scale
- **No Frontend Build**: Deploy via Docker only
- **Easier Updates**: Pull latest Open WebUI image
- **Community**: Leverage Open WebUI ecosystem

## Future Enhancements

- [ ] Add Vertex AI support (backend only change)
- [ ] Create more custom RAG functions
- [ ] Integrate with SSO/OAuth
- [ ] Add Confluence ingestion
- [ ] Deploy to GCP Cloud Run
- [ ] Add monitoring and analytics
- [ ] Create Internal Developer Platform widget

## Contributing

When contributing to this variant:

1. Keep backend changes minimal and backward-compatible
2. Document Open WebUI configurations
3. Test with multiple Ollama models
4. Ensure MCP server still works

## License

MIT

---

**Note**: This is the Open WebUI variant. For the custom React UI version, see the `claude/setup-rag-system-*` branch.
