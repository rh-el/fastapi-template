#!/bin/bash
# Start test environment

echo "Starting test environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
docker-compose -f docker-compose.test.yml up -d --build

echo ""
echo "Test environment started successfully!"
echo ""
echo "Service URLs:"
echo "   Backend API:  http://localhost:8001"
echo "   Database:     localhost:5433"
echo ""
echo "Cleanup:"
echo "   Stop and remove: docker-compose -f docker-compose.test.yml down -v"
echo ""
