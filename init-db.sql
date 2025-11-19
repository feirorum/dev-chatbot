-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for RAG system
CREATE SCHEMA IF NOT EXISTS rag;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA rag TO rag_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rag TO rag_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA rag TO rag_user;

-- Set search path
ALTER DATABASE rag_db SET search_path TO rag, public;
