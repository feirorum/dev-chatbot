# RAG Documentation Assistant

A modular RAG-based documentation assistant for developers using LlamaIndex, Postgres, and Ollama.

## Architecture

- **Backend**: FastAPI + LlamaIndex for RAG operations
- **Vector Store**: Postgres with pgvector extension
- **LLM**: Ollama (local) with future support for Vertex AI
- **Ingestion**: LlamaIndex loaders for Confluence, Git repos, and Markdown files
- **MCP Server**: Python MCP server for GitHub Copilot integration
- **Frontend**: React/Vite static web chat (GitHub Pages)

## Project Structure

```
.
├── planning/          # Project specifications and planning docs
├── backend/           # FastAPI + LlamaIndex RAG backend
├── ingestion/         # Data ingestion scripts
├── mcp/              # MCP server for GitHub Copilot
├── frontend/         # React/Vite web chat UI
└── docker-compose.yml # Local development environment
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+ (for frontend)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd dev-chatbot
```

2. Start services with Docker Compose:
```bash
docker-compose up -d
```

3. Set up backend:
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Run backend:
```bash
uvicorn main:app --reload
```

5. Set up and run frontend:
```bash
cd frontend
npm install
npm run dev
```

## Development

See [planning/initial_spec.md](planning/initial_spec.md) for detailed architecture and implementation plan.

## License

MIT
