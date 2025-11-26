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

# Check Ollama (on Windows host via WSL gateway)
echo -n "Checking Ollama on Windows host... "
# Get WSL gateway IP
GATEWAY_IP=$(ip route | grep default | awk '{print $3}')
if curl -s "http://${GATEWAY_IP}:11434/api/tags" > /dev/null 2>&1; then
    echo "✓"
    echo
    echo "Ollama is accessible at http://${GATEWAY_IP}:11434"
else
    echo "✗"
    echo "Warning: Cannot connect to Ollama on Windows."
    echo "Make sure Ollama is running on Windows and Windows Firewall allows connections."
    echo "Expected URL: http://${GATEWAY_IP}:11434"
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
echo "  Ollama (Windows): http://${GATEWAY_IP}:11434"
echo
echo "To view logs: docker-compose logs -f"
echo "To stop services: ./scripts/stop.sh"
echo
echo "Note: Using Ollama on Windows host."
echo "Your backend is configured to use: http://${GATEWAY_IP}:11434"
echo
