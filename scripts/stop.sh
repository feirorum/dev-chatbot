#!/bin/bash
set -e

echo "======================================"
echo "Stopping RAG Documentation Assistant"
echo "======================================"
echo

docker-compose down

echo
echo "✓ Services stopped"
echo
echo "To start again: ./scripts/start.sh"
echo "To remove all data: docker-compose down -v"
echo
