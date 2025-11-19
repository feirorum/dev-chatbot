#!/bin/bash
set -e

echo "======================================"
echo "RAG Documentation Assistant Setup"
echo "======================================"
echo

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo

# Set up backend
echo "Setting up backend..."
cd backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created backend/.env from example"
else
    echo "✓ backend/.env already exists"
fi
cd ..

# Set up ingestion
echo "Setting up ingestion..."
cd ingestion
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created ingestion/.env from example"
else
    echo "✓ ingestion/.env already exists"
fi
cd ..

# Set up MCP server
echo "Setting up MCP server..."
cd mcp
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created mcp/.env from example"
else
    echo "✓ mcp/.env already exists"
fi
cd ..

# Set up frontend
echo "Setting up frontend..."
cd frontend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created frontend/.env from example"
else
    echo "✓ frontend/.env already exists"
fi

# Install frontend dependencies
if command -v npm &> /dev/null; then
    echo "Installing frontend dependencies..."
    npm install
    echo "✓ Frontend dependencies installed"
else
    echo "⚠ npm not found. Skipping frontend dependency installation."
fi
cd ..

echo
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo
echo "Next steps:"
echo "1. Start services with: ./scripts/start.sh"
echo "2. Pull Ollama model with: docker exec -it rag-ollama ollama pull llama2"
echo "3. Ingest some documentation (see ingestion/README.md)"
echo "4. Open frontend at http://localhost:5173"
echo
