# Hybrid Architecture: Open WebUI Integration

This document describes the hybrid architecture where the Phase 1 RAG backend serves as the core service, with Open WebUI as a powerful alternative frontend alongside the React chat UI, MCP server, and future integrations.

## Architecture Diagram

```mermaid
flowchart LR
    %% Data sources
    subgraph S[Data Sources]
      C[Confluence\nwikis, spaces]
      G[Git / GitHub\nMarkdown repos]
      F[File shares\nLoose .md/.html]
    end

    %% Ingestion
    subgraph I[Ingestion Worker\nLlamaIndex]
      DLoader[Load & Normalize\nclean text + metadata]
      Chunk[Chunk into nodes]
      Embed[Embed local\nsentence-transformers]
      Upsert[Upsert to Postgres\n+ pgvector]
    end

    %% Storage
    subgraph DB[(Postgres + pgvector)]
      Docs[(documents)]
      Chunks[(chunks + embeddings)]
    end

    %% Backend
    subgraph B[RAG Backend API\nFastAPI + LlamaIndex]
      QEngine[Query Engine /\nRetriever]
      ChatCtrl[Chat Controller\nLLM orchestration]
    end

    %% LLMs
    subgraph M[Models]
      OLL[Ollama\nlocal LLMs]
      VERT[(later: Vertex AI\nGemini, embeddings)]
    end

    %% Clients
    subgraph UI[Clients / UIs]
      GHUI[GitHub Pages\nChat Frontend]
      MCP[MCP Server\nfor GitHub Copilot]
      OWUI[Open WebUI\nconsole client]
      IDP[Internal Dev Platform\nfuture widget]
    end

    %% Flows
    C --> DLoader
    G --> DLoader
    F --> DLoader

    DLoader --> Chunk --> Embed --> Upsert --> DB
    DB <--> QEngine
    QEngine --> ChatCtrl
    ChatCtrl --> OLL
    ChatCtrl -.future toggles.-> VERT

    GHUI -->|HTTPS /api/chat\n/api/search| B
    MCP -->|HTTPS /api/chat\n/api/search| B
    IDP -->|HTTPS /api/chat\n/api/search| B

    %% Hybrid part: Open WebUI
    OWUI -->|HTTP tools/API\ne.g. /api/chat| B
    OWUI -.optional.-> DB
    OWUI --> OLL
```

## Key Principles

1. **Core Backend Unchanged**: The Phase 1 RAG backend (FastAPI + LlamaIndex + Postgres) remains the single source of truth for RAG operations
2. **Multiple Clients**: Open WebUI is just another client, like the React frontend or MCP server
3. **Shared Infrastructure**: All clients use the same Ollama, Postgres, and ingestion pipeline
4. **Optional Direct DB Access**: Open WebUI can optionally read from Postgres/pgvector directly for advanced scenarios

## Component Details

### 2.1 Data & Storage (Unchanged)

**Postgres + pgvector**
- Tables:
  - `documents` - Per logical doc (Confluence page, repo file, etc.)
  - `chunks` - Per text chunk with metadata
  - `chunk_embeddings` - Vector embeddings via pgvector
- Shared by:
  - Ingestion worker
  - RAG backend
  - Optionally Open WebUI (read-only)

**Ingestion Worker** (LlamaIndex)
- Polls Confluence, Git repos, file shares
- Normalizes, chunks, embeds
- Upserts into Postgres/pgvector
- Runs as CronJob/Cloud Run job/systemd service
- **No changes from Phase 1**

### 2.2 RAG Backend API (Core Service)

**Tech Stack**: FastAPI + LlamaIndex + Postgres + Ollama

**Endpoints**:
- `POST /api/search`
  - Input: `query`, `filters?`
  - Output: List of chunks + scores + metadata
- `POST /api/chat`
  - Input: `query`, `history?`, `filters?`
  - Output: Answer + cited chunks
- `GET /health`
  - Output: Service health status

**Internals**:
- LlamaIndex Query Engine / Retriever
  - Connects to Postgres/pgvector
  - Applies metadata filters
- Chat controller
  - Calls Ollama (local/dev)
  - Later switches to Vertex AI

**Hybrid Enhancements**:
- Well-structured, documented APIs (OpenAPI/Swagger)
- CORS configuration for multiple clients
- Optional client identification headers
- Stable API contracts

### 2.3 MCP Server (Unchanged)

**Responsibility**: Expose RAG backend to GitHub Copilot via MCP

**Tools**:
- `search_docs` → wraps `POST /api/search`
- `chat_with_docs` → wraps `POST /api/chat`

**Config**: Points to RAG backend URL

**No changes required** - MCP server is independent of Open WebUI

### 2.4 GitHub Pages Chat Frontend (Unchanged)

**Tech**: React/Vite static frontend

**Features**:
- Simple, clean chat UI
- Shows sources & filters
- Calls `POST /api/chat` and `POST /api/search`

**No changes required** - React frontend is independent of Open WebUI

### 2.5 Open WebUI (New Hybrid Client)

**Role**: Powerful alternative frontend with advanced features

**Integration Methods**:

1. **As HTTP API Client**:
   - Configure Open WebUI with custom "tools" or "functions"
   - Tools call `/api/chat` and `/api/search` on RAG backend
   - Becomes a console to mix RAG with other capabilities

2. **Direct Ollama Access**:
   - Connects to same Ollama instance
   - Can use multiple models
   - Experiment with different prompts

3. **Optional Direct DB Access** (Advanced):
   - Point Open WebUI's RAG to same Postgres/pgvector
   - Use for scenarios where Open WebUI's built-in RAG is preferred
   - Mirror or share data

**Features Enabled**:
- Multi-model experimentation
- Advanced prompt engineering
- User management and sharing
- RAG + non-RAG workflows
- MCP toolchain integration

**Access**: http://localhost:3000

### 2.6 Internal Developer Platform (Future)

Portal widget that:
- Calls `/api/chat` and `/api/search`
- Can embed Open WebUI in iframe
- Link to "advanced console" (Open WebUI)

## What Changed from Phase 1?

### Minimal Backend Changes

The Phase 1 backend requires only minor enhancements:

1. **API Documentation**
   - Add OpenAPI/Swagger spec for `/api/chat` and `/api/search`
   - Makes integration easier for Open WebUI and other clients

2. **CORS Configuration**
   - Allow requests from Open WebUI (port 3000)
   - Already configured for GitHub Pages

3. **Database Schema Documentation**
   - Document table schemas for optional direct access
   - Specify embedding dimensions and metadata fields

4. **Optional Client Identification**
   - Add `client_id` header support for monitoring
   - Distinguish traffic from different frontends

### New Infrastructure

1. **Docker Compose**
   - Added `open-webui` service
   - Shared volumes for persistence
   - Environment configuration

2. **Documentation**
   - This hybrid architecture guide
   - Open WebUI configuration instructions
   - Integration patterns

## Benefits of Hybrid Approach

### For Developers
- **Choice of Interface**: Use simple React chat or powerful Open WebUI
- **Experimentation**: Try different models and prompts in Open WebUI
- **Consistency**: Same backend, same data, different UX

### For the System
- **No Duplication**: Single ingestion pipeline, single data store
- **Flexibility**: Swap or add frontends without backend changes
- **Future-Proof**: Easy to add more clients (IDP, Slack bot, etc.)

### For Migration
- **Gradual Adoption**: Can switch between UIs
- **Risk Reduction**: Backend remains stable
- **Easy Rollback**: Remove Open WebUI without affecting other clients

## Setup Comparison

### Phase 1 Setup
```bash
./scripts/setup.sh
./scripts/start.sh
# Access React UI at http://localhost:5173
```

### Hybrid Setup
```bash
./scripts/setup.sh
./scripts/start.sh
# Access Open WebUI at http://localhost:3000
# Access React UI at http://localhost:5173 (still available)
# Both use same backend at http://localhost:8000
```

## Integration Patterns

### Pattern 1: Open WebUI as Primary UI
- Users interact mainly with Open WebUI
- RAG backend provides document search via API calls
- React UI available as fallback/alternative

### Pattern 2: Open WebUI as Power User Tool
- Regular users use React UI (simpler)
- Power users/admins use Open WebUI (more features)
- Both share same data and backend

### Pattern 3: Open WebUI for Experimentation
- Production uses React UI or IDP widget
- Development/testing uses Open WebUI
- Experiment with models and prompts before productionizing

## Future Enhancements

### Near Term
- Configure Open WebUI functions/tools for RAG backend
- Add authentication to backend API
- Create user guides for both UIs

### Medium Term
- Migrate to Vertex AI (transparent to all clients)
- Add more data sources
- Implement feedback loops

### Long Term
- Internal Developer Platform integration
- Slack/Teams bot clients
- Mobile app using same backend

## Summary

The hybrid architecture:
- **Keeps** Phase 1 backend exactly as designed
- **Adds** Open WebUI as powerful alternative frontend
- **Maintains** all existing clients (MCP, React UI)
- **Enables** experimentation and power user workflows
- **Prepares** for future integrations and migrations

All clients share the same robust backend, ensuring consistency while providing flexibility in user experience.
