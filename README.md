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

- **Docker Desktop for Windows** with WSL 2 integration enabled
  - Open Docker Desktop → Settings → Resources → WSL Integration
  - Enable integration for your WSL distro
  - See: https://docs.docker.com/desktop/wsl/
- Python 3.10+
- Node.js 18+ (for frontend)
- **Ollama** installed on Windows (for LLM)

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

## WSL/Windows Ollama Setup

If you're running the project in WSL with Ollama installed on Windows, you need to configure the connection to use the WSL gateway IP:

### 1. Get WSL Gateway IP

Run this command in WSL to get your gateway IP:

```bash
ip route | grep default | awk '{print $3}'
```

This will typically return an IP like `172.x.x.1` (e.g., `172.25.160.1`).

### 2. Update Backend Configuration

Edit `backend/.env` and set the `OLLAMA_BASE_URL` to use your gateway IP:

```bash
OLLAMA_BASE_URL=http://172.25.160.1:11434
```

Replace `172.25.160.1` with your actual gateway IP from step 1.

### 3. Configure Windows Firewall

Ensure that Ollama on Windows can accept connections from WSL:

1. Open "Windows Defender Firewall with Advanced Security"
2. Add an inbound rule for port 11434
3. Allow connections from the WSL network range (typically `172.x.x.0/20`)

Alternatively, when you first try to connect, Windows may prompt you to allow the connection.

### 4. Verify Ollama is Running

On Windows, ensure Ollama is running:

```powershell
ollama list  # Should show your installed models
ollama serve  # If not already running as a service
```

### 5. Test Connection from WSL

Test the connection from WSL:

```bash
curl http://172.25.160.1:11434/api/tags
```

You should see a JSON response with your installed models.

## Development

See [planning/initial_spec.md](planning/initial_spec.md) for detailed architecture and implementation plan.

## License

MIT
