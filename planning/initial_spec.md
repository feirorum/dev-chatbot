# Phase 1 RAG System – Canvas Description (LlamaIndex + Postgres + Ollama)

## 1. Purpose & Scope

Build a modular RAG-based documentation assistant for developers, using:

* **LlamaIndex** for ingestion, indexing, and retrieval.
* **Postgres + pgvector** for persistent storage.
* **Ollama** for local LLM inference during development.

Should:

* Work locally on modest laptop GPUs.
* Scale later to GCP and Vertex AI.
* Serve **both** a GitHub Pages web chat and an MCP server for GitHub Copilot.

---

## 2. Entry Points & User Flows

### Users

* Developers using **GitHub Copilot** → via **MCP server**.
* Developers using **browser chat UI** → via GitHub Pages (static web + backend API).

### System Entry Points

| Entry Point | Implementation         | Connects To     |
| ----------- | ---------------------- | --------------- |
| MCP Server  | Python MCP tool server | RAG Backend API |
| Web Chat UI | React/Vite static page | RAG Backend API |

---

## 3. Data Sources (Phase 1)

| Source Type      | Examples                     | Access Method              |
| ---------------- | ---------------------------- | -------------------------- |
| Confluence       | Team spaces, pages           | REST API + service account |
| Git Repos        | Internal documentation repos | Git clone + file loader    |
| Markdown Storage | Local/network folder docs    | Directory scan             |

Metadata retained: `source_type`, `source_id`, `title`, `last_updated`, `url/path`, etc.

---

## 4. Core Architecture

```
+-----------------------+
|       GitHub Pages    |
|     Chat Frontend     |
+----------+------------+
           |
           v
+-----------------------+        +------------------+
|    RAG Backend API    | <----> |   MCP Server     |
|  (FastAPI + LlamaIndex|        |  (Python)        |
+----------+------------+        +------------------+
           |
           v
+-----------------------+        +------------------+
| Postgres (pgvector)   |        |   Ollama LLM     |
+-----------------------+        +------------------+
           ^
           |
+-----------------------------+
|       Ingestion Worker      |
| (LlamaIndex loaders)        |
+-----------------------------+
```

---

## 5. Ingestion Workflow

1. **Fetch content** from Confluence, Git, markdown folders.
2. **Normalize** (clean text, extract metadata).
3. **Chunk** into nodes (~512–1k tokens).
4. **Embed** using local sentence-transformers.
5. **Upsert** into Postgres/pgvector.

Can run as CronJob, Cloud Run job, or locally.

---

## 6. RAG Backend API

Built with **FastAPI** and **LlamaIndex**.

### Endpoints

| Endpoint      | Purpose                                        |
| ------------- | ---------------------------------------------- |
| `/api/chat`   | Full chat with retrieval and Ollama completion |
| `/api/search` | Return relevant document chunks                |

Supports filters (e.g., limit to Confluence, repo, etc.).

---

## 7. MCP Server Design

Custom Python server using official MCP SDK.

### Tools exposed

* `search_docs(query, filters)` → returns snippets + metadata.
* `chat_with_docs(query, history)` → full chat.

Delegates computation to backend API.

---

## 8. Web Chat UI (GitHub Pages)

* Static React/Vite app.
* Features:

  * Chat window with streaming.
  * Source panel showing document excerpts and metadata.
  * Filter controls (e.g. Confluence vs Git).
* Calls backend API.

---

## 9. Configuration Strategy

Use environment-based config to allow later swap-in:

```yaml
LLM_PROVIDER: "ollama" # later "vertex"
EMBEDDINGS_PROVIDER: "local" # later "vertex"
VECTOR_STORE: "pgvector" # later "vertex-search" or team pipeline
```

---

## 10. Phase 1 Deliverables

* [ ] Repo scaffold

  * `ingestion/` (Python scripts/jobs)
  * `backend/` (FastAPI + LlamaIndex)
  * `mcp/` (MCP tool server)
  * `frontend/` (React/Vite chat UI)
* [ ] Docker Compose for local (Postgres + backend + Ollama)
* [ ] Basic ingestion from small test sources
* [ ] Fully working local chat
* [ ] MCP integration tested with GitHub Copilot

---

## 11. Future Considerations

* Swap Ollama → Vertex AI
* Migrate embedding / vector search
* Plug in other team's pipeline
* Add security/auth layers (OAuth, SSO)
* Expand sources (internal dev platform, Jira, build logs, etc.)

---

## 12. Notes

* Keep retriever interface simple to plug in additional search services.
* Plan early for incremental ingestion (by last_updated timestamps).
* Ensure all chunks include source links for user reference.

**End of Phase 1 Canvas**
