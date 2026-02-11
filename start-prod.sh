#!/bin/bash
# Start production environment

echo "Starting production environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "Error: .env.prod file not found!"
    echo "   Please create .env.prod with your production credentials."
    exit 1
fi

# Build and start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

echo ""
echo "Services started successfully!"
echo ""
echo "Service URLs:"
echo "   Backend API:  http://localhost:8000"
echo "   Database:     localhost:5432"
echo ""
echo "Useful commands:"
echo "   View logs:        docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services:    docker-compose -f docker-compose.prod.yml down"
echo "   Run migrations:   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head"
echo "   Database backup:  docker-compose -f docker-compose.prod.yml exec db pg_dump -U app_prod app_prod > backup.sql"
echo ""
