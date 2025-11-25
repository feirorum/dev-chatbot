# RAG Documentation Assistant - POC Implementation Plan

## Overview

This plan focuses on validating the core hypothesis: **"Can we build a RAG system that usefully answers dev questions across chat UI and Copilot MCP?"**

We prioritize retrieval quality and practical usability over polish. Each phase builds on the previous and can be demoed independently.

---

## Phase 0: Validate Current Setup

**Goal:** Establish a working baseline and identify real failure cases.

**Duration:** 1-2 hours

### Tasks

#### 0.1 Environment Setup
- [ ] Run `./scripts/setup.sh`
- [ ] Start services with `./scripts/start.sh`
- [ ] Pull Ollama model: `docker exec -it rag-ollama ollama pull llama2`
- [ ] Verify health endpoint: `curl http://localhost:8000/health`

#### 0.2 Ingest Test Documentation
- [ ] Create test corpus from real internal docs (suggest: 20-50 markdown files)
- [ ] Run ingestion: `python ingest.py --source markdown --path ../test-docs`
- [ ] Verify documents indexed via search endpoint

#### 0.3 Baseline Evaluation
- [ ] Prepare 10 representative questions spanning:
  - "How do I..." (tutorial-seeking)
  - "What is..." (conceptual)
  - Exact term lookup (function name, config key)
  - Error message troubleshooting
  - Code example requests
- [ ] Document answers and failure modes
- [ ] Note which failures are retrieval vs. generation issues

#### 0.4 Frontend Smoke Test
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Verify chat flow works end-to-end
- [ ] Test source panel displays retrieved documents

### Deliverables
- Working local environment
- Baseline evaluation document with failure analysis
- List of specific retrieval failures to address

---

## Phase 1: Retrieval Quality & Admin Tools

**Goal:** Improve retrieval accuracy and add operational controls for managing the knowledge base.

**Duration:** 3-4 days

### 1.1 Hybrid Search (BM25 + Vector)

**Why:** Pure vector search misses exact keyword matches (function names, error codes, config keys). BM25 excels at these. Combining both covers more query types.

#### 1.1.1 Backend Changes

**File:** `backend/requirements.txt`
```
# Add
rank-bm25==0.2.2
```

**File:** `backend/hybrid_retriever.py` (new)
```python
"""
Hybrid retriever combining BM25 and vector similarity search.

Architecture:
- BM25 index built in-memory from document store
- Vector search via existing pgvector
- Results merged using Reciprocal Rank Fusion (RRF)
"""

Components to implement:
- BM25Index class (wraps rank-bm25)
- HybridRetriever class
  - __init__(vector_store, bm25_index, vector_weight=0.5)
  - retrieve(query, top_k, filters) -> List[NodeWithScore]
- RRF merge function
- Index refresh mechanism (rebuild BM25 on new ingestion)
```

**File:** `backend/vector_store.py`
```python
# Extend VectorStoreManager:
- Add get_all_documents() method for BM25 index building
- Add hybrid_retrieve(query, top_k, filters, vector_weight)
- Cache BM25 index, rebuild on document changes
```

**File:** `backend/main.py`
```python
# Update endpoints:
- Add `search_mode` parameter: "vector" | "bm25" | "hybrid" (default: "hybrid")
- Add `vector_weight` parameter (0.0-1.0, default: 0.5)
```

#### 1.1.2 Testing
- [ ] Unit test: BM25 index returns exact keyword matches
- [ ] Unit test: RRF merge produces expected ranking
- [ ] Integration test: Hybrid search outperforms vector-only on keyword queries
- [ ] Compare baseline questions against new hybrid results

### 1.2 Idempotent Ingestion & Source Management

**Why:** Re-ingesting duplicates documents. Need to update/replace cleanly and purge corrupted sources.

#### 1.2.1 Document Identity Model

**File:** `backend/models.py`
```python
# Add document identity fields:
class DocumentIdentity(BaseModel):
    source_type: str      # "confluence", "git", "markdown"
    source_id: str        # Unique within source_type (URL, file path, page ID)
    content_hash: str     # SHA256 of content for change detection
    ingested_at: datetime
    version: int          # Increment on re-ingestion
```

**File:** `ingestion/ingest.py`
```python
# Add before upserting:
- Compute content_hash for each document
- Query existing docs with same (source_type, source_id)
- If exists and hash matches: skip
- If exists and hash differs: delete old, insert new
- If not exists: insert
```

#### 1.2.2 Database Schema Changes

**File:** `init-db.sql`
```sql
-- Add document registry table
CREATE TABLE IF NOT EXISTS document_registry (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(500) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    chunk_count INTEGER NOT NULL,
    ingested_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB,
    UNIQUE(source_type, source_id)
);

-- Add index for source queries
CREATE INDEX idx_doc_registry_source ON document_registry(source_type);
```

#### 1.2.3 Admin API Endpoints

**File:** `backend/admin.py` (new)
```python
"""
Admin endpoints for knowledge base management.
Mounted at /admin/* with future auth middleware hook.
"""

from fastapi import APIRouter

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/sources")
async def list_sources():
    """List all ingested sources with document counts."""
    # Returns: [{"source_type": "markdown", "source_id": "...", "doc_count": 42, "ingested_at": "..."}]

@admin_router.get("/sources/{source_type}")
async def list_source_documents(source_type: str):
    """List all documents from a specific source type."""

@admin_router.delete("/sources/{source_type}")
async def delete_source_type(source_type: str):
    """Delete ALL documents from a source type (e.g., purge corrupted Confluence import)."""

@admin_router.delete("/sources/{source_type}/{source_id}")
async def delete_source(source_type: str, source_id: str):
    """Delete a specific source and all its chunks."""

@admin_router.post("/sources/{source_type}/{source_id}/reingest")
async def reingest_source(source_type: str, source_id: str):
    """Force re-ingestion of a specific source."""

@admin_router.get("/stats")
async def get_stats():
    """Return KB statistics: total docs, chunks, by source type, index health."""
```

**File:** `backend/main.py`
```python
# Mount admin router
from admin import admin_router
app.include_router(admin_router)
```

#### 1.2.4 Admin CLI

**File:** `scripts/admin.py` (new)
```python
#!/usr/bin/env python3
"""
CLI for RAG admin operations.

Usage:
    python admin.py sources list
    python admin.py sources list --type confluence
    python admin.py sources delete --type markdown
    python admin.py sources delete --type git --id https://github.com/org/repo
    python admin.py stats
    python admin.py reingest --type markdown --path ./docs
"""

import argparse
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Implement CLI commands that call admin API endpoints
```

#### 1.2.5 Admin Web Tab (Frontend)

**File:** `frontend/src/AdminPanel.jsx` (new)
```jsx
/**
 * Admin panel component for KB management.
 * Features:
 * - Source list with document counts
 * - Delete source button with confirmation
 * - Reingest trigger
 * - Stats display
 */
```

**File:** `frontend/src/App.jsx`
```jsx
// Add tab navigation: Chat | Admin
// Conditionally render ChatPanel or AdminPanel
```

### 1.3 Metadata Filtering (Wire Through Existing Params)

**Why:** Filter params exist in API models but aren't used. Essential for "search only in SDK docs" use cases.

#### 1.3.1 Backend Implementation

**File:** `backend/vector_store.py`
```python
# Update retrieve methods to apply filters:
def retrieve(self, query, top_k, filters=None):
    # Build pgvector filter clause from filters dict
    # Supported filters:
    #   - source_type: str | List[str]
    #   - source_id: str | List[str]  
    #   - ingested_after: datetime
    #   - ingested_before: datetime
```

**File:** `backend/main.py`
```python
# Ensure filters passed through to retriever in /api/search and /api/chat
```

#### 1.3.2 Frontend Filter UI

**File:** `frontend/src/App.jsx`
```jsx
// Add filter dropdown above input:
// - "All sources" (default)
// - "Confluence only"
// - "Git repos only"  
// - "Markdown docs only"
// Pass selected filter to API calls
```

### 1.4 Improved Chunking for Code

**Why:** Code blocks split mid-function are useless. Preserve code units.

#### 1.4.1 Code-Aware Splitter

**File:** `ingestion/code_splitter.py` (new)
```python
"""
Code-aware document splitter.

Strategy:
1. Identify code blocks (``` fenced or indented)
2. Keep code blocks intact up to max_chunk_size
3. Include preceding paragraph as context
4. For pure code files: split on function/class boundaries
"""

class CodeAwareNodeParser:
    def __init__(self, chunk_size=1024, chunk_overlap=200):
        ...
    
    def get_nodes_from_documents(self, documents):
        # For each document:
        # 1. Detect if it's code-heavy (>50% code blocks)
        # 2. If code-heavy: use code-boundary splitting
        # 3. If text-heavy: use standard sentence splitting but preserve code blocks
```

**File:** `ingestion/ingest.py`
```python
# Replace SentenceSplitter with CodeAwareNodeParser for markdown/code files
```

### Phase 1 Deliverables
- [ ] Hybrid search working and tested
- [ ] Idempotent ingestion (skip unchanged, update changed)
- [ ] Admin API endpoints
- [ ] Admin CLI tool
- [ ] Admin web tab with source management
- [ ] Metadata filtering working end-to-end
- [ ] Code-aware chunking
- [ ] Re-run baseline evaluation, document improvements

---

## Phase 2: Context Engineering for MCP

**Goal:** Make MCP responses more useful for Copilot agentic workflows.

**Duration:** 2-3 days

### 2.1 Structured Tool Responses

**Why:** Raw text blobs are hard for Copilot to use. Structured responses enable better code generation.

#### 2.1.1 Response Schema

**File:** `mcp/models.py` (new)
```python
class CodeExample(BaseModel):
    language: str
    code: str
    description: Optional[str]
    source_file: Optional[str]

class APISignature(BaseModel):
    name: str
    signature: str
    docstring: Optional[str]
    module: str

class DocSection(BaseModel):
    title: str
    content: str
    doc_type: str  # "tutorial", "reference", "conceptual", "troubleshooting"
    url: Optional[str]

class StructuredSearchResult(BaseModel):
    summary: str
    code_examples: List[CodeExample]
    api_signatures: List[APISignature]
    doc_sections: List[DocSection]
    related_queries: List[str]
```

#### 2.1.2 Response Formatter

**File:** `backend/response_formatter.py` (new)
```python
"""
Transforms raw retrieval results into structured responses.

Pipeline:
1. Classify each chunk (code example, API doc, prose)
2. Extract code blocks with language detection
3. Parse function signatures from docstrings
4. Group related chunks
5. Generate summary
"""

class ResponseFormatter:
    def format_for_mcp(self, query: str, results: List[NodeWithScore]) -> StructuredSearchResult:
        ...
```

#### 2.1.3 MCP Server Updates

**File:** `mcp/server.py`
```python
# Update tool responses to use structured format
# Add new tool: get_code_examples(query, language_filter)
# Add new tool: get_api_reference(symbol_name)
```

### 2.2 Query Intent Classification

**Why:** Different query types benefit from different retrieval strategies.

#### 2.2.1 Intent Classifier

**File:** `backend/query_classifier.py` (new)
```python
"""
Lightweight query intent classification.

Intents:
- HOWTO: "How do I...", "How to...", "Example of..."
- CONCEPTUAL: "What is...", "Explain...", "Why does..."
- REFERENCE: Function/class names, API lookups
- TROUBLESHOOT: Error messages, "not working", "fails when"
- EXAMPLE: "Show me...", "Sample...", "Code for..."

Implementation: Rule-based with regex patterns.
Future: Fine-tuned classifier if rules insufficient.
"""

class QueryClassifier:
    def classify(self, query: str) -> QueryIntent:
        ...
    
    def get_retrieval_config(self, intent: QueryIntent) -> RetrievalConfig:
        # Returns tuned parameters per intent:
        # - top_k
        # - vector_weight (more keyword weight for REFERENCE)
        # - source_type_boost (prefer tutorials for HOWTO)
```

#### 2.2.2 Integration

**File:** `backend/main.py`
```python
# In /api/search and /api/chat:
# 1. Classify query intent
# 2. Get intent-specific retrieval config
# 3. Apply config to retrieval
# 4. Include intent in response metadata
```

### 2.3 Context-Aware MCP Search

**Why:** In-flow coding queries benefit from knowing what file/language the dev is working in.

#### 2.3.1 Extended MCP Tool Schema

**File:** `mcp/server.py`
```python
class ContextAwareSearchArgs(BaseModel):
    query: str
    # Optional context from editor
    current_language: Optional[str]  # "python", "typescript", etc.
    current_file: Optional[str]      # Filename for context
    imports_in_scope: Optional[List[str]]  # Imported modules
    error_message: Optional[str]     # If debugging an error
    
# New tool: context_search
# Uses context to:
# - Boost results matching current_language
# - Prioritize docs for imported modules
# - Switch to troubleshooting mode if error_message present
```

#### 2.3.2 Context-Boosted Retrieval

**File:** `backend/context_retriever.py` (new)
```python
"""
Applies context signals to retrieval scoring.

Boost factors:
- Language match: 1.5x
- Import match: 2.0x  
- Error pattern match: 1.8x
"""

class ContextRetriever:
    def retrieve_with_context(
        self, 
        query: str, 
        context: SearchContext,
        base_results: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        # Re-rank base results using context signals
```

### 2.4 MCP Health & Diagnostics

**File:** `mcp/server.py`
```python
# Add tools:
# - health_check(): Returns backend status, model availability, index stats
# - list_sources(): Shows what's indexed (helps user understand KB scope)
# - explain_retrieval(query): Debug tool showing why certain docs were retrieved
```

### Phase 2 Deliverables
- [ ] Structured MCP responses with code examples extracted
- [ ] Query intent classification
- [ ] Context-aware search for MCP
- [ ] Diagnostic MCP tools
- [ ] Test with real Copilot agentic workflows

---

## Phase 3: Real Source Ingestion

**Goal:** Ingest actual internal documentation sources.

**Duration:** 2-3 days (depends on source complexity)

### 3.1 Confluence Loader

**Why:** Listed in spec but not implemented. Common internal KB source.

#### 3.1.1 Implementation

**File:** `ingestion/loaders/confluence.py` (new)
```python
"""
Confluence ingestion using LlamaIndex Confluence loader.

Features:
- Space-based ingestion
- Page hierarchy preservation (parent/child metadata)
- Attachment handling (skip or extract text)
- Incremental sync via last_modified
"""

from llama_index.readers.confluence import ConfluenceReader

class ConfluenceIngester:
    def __init__(self, url: str, username: str, api_token: str):
        ...
    
    def ingest_space(self, space_key: str) -> int:
        # Fetch all pages in space
        # Apply standard chunking
        # Include metadata: page_id, title, url, space, parent_page
        
    def ingest_page(self, page_id: str) -> int:
        # Single page ingestion
        
    def sync_space(self, space_key: str, since: datetime) -> int:
        # Incremental: only pages modified since last sync
```

#### 3.1.2 CLI Integration

**File:** `ingestion/ingest.py`
```python
# Add --source confluence option
# Required args: --space-key
# Optional: --page-id (single page mode)
```

### 3.2 Enhanced Git Repository Loader

**Why:** Current implementation is basic. Need better handling of code repos vs. doc repos.

#### 3.2.1 Improvements

**File:** `ingestion/loaders/git_repo.py` (new)
```python
"""
Enhanced Git repository ingestion.

Modes:
- docs: Only ingest docs/, README.md, *.md files
- code: Ingest source files with docstring extraction
- full: Both docs and code

Code processing:
- Extract module/class/function docstrings
- Parse type hints for API signatures
- Include import context
"""

class GitRepoIngester:
    def __init__(self, repo_url: str, mode: str = "docs"):
        ...
    
    def ingest(self, branch: str = "main", paths: List[str] = None) -> int:
        ...
```

#### 3.2.2 Docstring Extraction

**File:** `ingestion/extractors/docstrings.py` (new)
```python
"""
Extract docstrings and signatures from Python/TypeScript code.

For each function/class:
- Name and qualified path
- Signature with type hints
- Docstring (parsed: summary, args, returns, examples)
- Source file and line number
"""

import ast
from typing import List

class DocstringExtractor:
    def extract_python(self, file_path: str) -> List[ExtractedDoc]:
        ...
    
    def extract_typescript(self, file_path: str) -> List[ExtractedDoc]:
        # Use tree-sitter or regex-based extraction
```

### 3.3 Ingestion Scheduling

**Why:** POC needs manual triggers, but prep for automated refresh.

#### 3.3.1 Job Tracking

**File:** `backend/models.py`
```python
class IngestionJob(BaseModel):
    job_id: str
    source_type: str
    source_config: dict
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    documents_processed: int
    error_message: Optional[str]
```

**File:** `backend/admin.py`
```python
@admin_router.post("/ingest")
async def trigger_ingestion(config: IngestionConfig) -> IngestionJob:
    """Trigger ingestion job (runs async)."""

@admin_router.get("/jobs")
async def list_jobs() -> List[IngestionJob]:
    """List recent ingestion jobs."""

@admin_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> IngestionJob:
    """Get status of specific job."""
```

### Phase 3 Deliverables
- [ ] Confluence loader working
- [ ] Enhanced git repo loader with docstring extraction
- [ ] Ingestion job tracking via admin API
- [ ] Successfully ingest real internal KB
- [ ] Validate retrieval quality on real content

---

## Testing Strategy

### Unit Tests (Per Phase)

```
tests/
├── unit/
│   ├── test_hybrid_retriever.py    # Phase 1.1
│   ├── test_bm25_index.py          # Phase 1.1
│   ├── test_rrf_merge.py           # Phase 1.1
│   ├── test_document_registry.py   # Phase 1.2
│   ├── test_code_splitter.py       # Phase 1.4
│   ├── test_query_classifier.py    # Phase 2.2
│   ├── test_response_formatter.py  # Phase 2.1
│   └── test_docstring_extractor.py # Phase 3.2
├── integration/
│   ├── test_search_api.py
│   ├── test_chat_api.py
│   ├── test_admin_api.py
│   └── test_ingestion_pipeline.py
└── e2e/
    ├── test_chat_flow.py
    └── test_mcp_tools.py
```

### Test Fixtures

**File:** `tests/fixtures/sample_docs/`
```
- tutorial.md (how-to content)
- api_reference.md (function docs)
- code_examples.py (Python with docstrings)
- error_guide.md (troubleshooting)
```

### Evaluation Queries

**File:** `tests/evaluation/baseline_queries.json`
```json
[
  {
    "query": "How do I authenticate with the SDK?",
    "intent": "HOWTO",
    "expected_sources": ["auth_guide.md"],
    "expected_keywords": ["authenticate", "token", "API key"]
  },
  {
    "query": "ConnectionTimeoutError",
    "intent": "TROUBLESHOOT", 
    "expected_sources": ["error_reference.md"],
    "expected_keywords": ["timeout", "retry", "connection"]
  }
]
```

---

## File Structure After Implementation

```
dev-chatbot/
├── backend/
│   ├── admin.py              # NEW: Admin API endpoints
│   ├── config.py
│   ├── context_retriever.py  # NEW: Context-boosted retrieval
│   ├── database.py
│   ├── hybrid_retriever.py   # NEW: BM25 + vector hybrid
│   ├── main.py               # MODIFIED: Add admin routes, hybrid search
│   ├── models.py             # MODIFIED: Add document identity, jobs
│   ├── query_classifier.py   # NEW: Intent classification
│   ├── response_formatter.py # NEW: Structured response formatting
│   ├── requirements.txt      # MODIFIED: Add rank-bm25
│   └── vector_store.py       # MODIFIED: Add hybrid retrieval
├── frontend/
│   ├── src/
│   │   ├── AdminPanel.jsx    # NEW: Admin UI
│   │   ├── App.jsx           # MODIFIED: Add tabs, filters
│   │   └── ...
│   └── ...
├── ingestion/
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── confluence.py     # NEW: Confluence loader
│   │   └── git_repo.py       # NEW: Enhanced git loader
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── docstrings.py     # NEW: Docstring extraction
│   ├── code_splitter.py      # NEW: Code-aware chunking
│   ├── config.py
│   ├── ingest.py             # MODIFIED: Idempotent, new loaders
│   └── requirements.txt      # MODIFIED: Add gitpython, ast deps
├── mcp/
│   ├── models.py             # NEW: Structured response types
│   ├── server.py             # MODIFIED: New tools, structured responses
│   └── requirements.txt
├── scripts/
│   ├── admin.py              # NEW: Admin CLI
│   ├── setup.sh
│   ├── start.sh
│   └── stop.sh
├── tests/                    # NEW: Test structure
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── evaluation/
├── init-db.sql               # MODIFIED: Add document_registry table
└── docker-compose.yml
```

---

## Success Criteria

### Phase 0
- [ ] System runs locally without errors
- [ ] Can ingest and query test documents
- [ ] Baseline evaluation documented

### Phase 1
- [ ] Hybrid search improves keyword query recall by >30%
- [ ] Re-ingestion doesn't duplicate documents
- [ ] Can purge all documents from a source type via admin
- [ ] Filters correctly limit search scope

### Phase 2
- [ ] MCP returns structured responses with extracted code
- [ ] Query intent classification accuracy >80% on test set
- [ ] Context-aware search improves relevance for in-flow queries

### Phase 3
- [ ] Successfully ingest real Confluence space
- [ ] Successfully ingest internal code repo with docstrings
- [ ] End-to-end flow works for real developer questions

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 0 | 1-2 hours | None |
| Phase 1 | 3-4 days | Phase 0 complete |
| Phase 2 | 2-3 days | Phase 1 complete |
| Phase 3 | 2-3 days | Phase 1 complete (can parallel with Phase 2) |

**Total:** ~8-12 days for full POC

---

## Open Questions

1. **LLM choice:** Stick with Llama2 or try Mistral/CodeLlama for better code understanding?
2. **Embedding model:** Current `all-MiniLM-L6-v2` is general-purpose. Consider code-specific embeddings?
3. **Confluence auth:** Service account available, or need OAuth setup?
4. **Which internal repos to prioritize?** Start with most-queried libraries.
5. **Evaluation dataset:** Can we get real developer questions from Slack/support channels?

---

## Next Steps

1. Complete Phase 0 to establish baseline
2. Start Phase 1.1 (hybrid search) - highest impact improvement
3. Parallel: Set up test fixtures and evaluation framework
4. Review after Phase 1 to adjust priorities based on real results
