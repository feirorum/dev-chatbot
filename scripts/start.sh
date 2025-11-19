#!/bin/bash
set -e

echo "======================================"
echo "Starting RAG Documentation Assistant"
echo "======================================"
echo

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

echo
echo "Waiting for services to be ready..."
sleep 5

# Check Postgres
echo -n "Checking Postgres... "
if docker exec rag-postgres pg_isready -U rag_user -d rag_db > /dev/null 2>&1; then
    echo "✓"
else
    echo "✗ (might still be starting up)"
fi

# Check Ollama
echo -n "Checking Ollama... "
if docker exec rag-ollama ollama list > /dev/null 2>&1; then
    echo "✓"
    echo
    echo "Available Ollama models:"
    docker exec rag-ollama ollama list
else
    echo "✗ (might still be starting up)"
fi

echo
echo "======================================"
echo "Services started!"
echo "======================================"
echo
echo "Service URLs:"
echo "  Backend API: http://localhost:8000"
echo "  Backend Docs: http://localhost:8000/docs"
echo "  Postgres: localhost:5432"
echo "  Ollama: localhost:11434"
echo
echo "To view logs: docker-compose logs -f"
echo "To stop services: ./scripts/stop.sh"
echo
echo "If you haven't pulled an Ollama model yet, run:"
echo "  docker exec -it rag-ollama ollama pull llama2"
echo
