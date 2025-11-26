# Ingestion Module

This module handles ingesting documents from various sources into the RAG system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Ingest Markdown Files

```bash
python ingest.py --source markdown --path /path/to/markdown/docs
```

### Ingest from Git Repository

```bash
python ingest.py --source git --path https://github.com/your-org/docs-repo.git
```

### Using Default Paths

If you've configured paths in `.env`, you can omit the `--path` argument:

```bash
python ingest.py --source markdown
python ingest.py --source git
```

## Supported Sources

- **Markdown**: Local markdown files and directories
- **Git**: Documentation from Git repositories
- **Confluence**: (Coming soon) Confluence pages and spaces

## Configuration

See `.env.example` for all available configuration options.
