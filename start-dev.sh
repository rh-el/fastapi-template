#!/bin/bash
# Start development environment

echo "Starting development environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
docker-compose -f docker-compose.dev.yml up -d --build

echo ""
echo "Services started successfully!"
echo ""
echo "Service URLs:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/api/v1/openapi.json"
echo "   Database:     localhost:5432"
echo ""
echo "Useful commands:"
echo "   View logs:        docker-compose -f docker-compose.dev.yml logs -f"
echo "   Stop services:    docker-compose -f docker-compose.dev.yml down"
echo "   Run migrations:   docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head"
echo ""
