#!/bin/bash

# Deployment script for PTB OT Backend - Staging Environment
# Usage: ./deploy-staging.sh

set -e

ENVIRONMENT="staging"
PROJECT_NAME="ptb-ot-backend"
COMPOSE_FILE="docker-compose.staging.yml"

echo "🚀 Starting deployment for ${ENVIRONMENT} environment..."
echo "=================================================="

# Check if .env.staging exists
if [ ! -f ".env.staging" ]; then
    echo "❌ Error: .env.staging not found"
    echo "Please create .env.staging from .env.staging.example"
    exit 1
fi

echo "✅ Environment file found: .env.staging"

# Load environment variables
export $(cat .env.staging | grep -v '^#' | grep -v '^$' | xargs)
echo "✅ Environment variables loaded"

# Build Docker images (only dependencies, source code is mounted)
echo ""
echo "📦 Building Docker images..."
echo "Note: Only dependencies are built - source code is live-mounted"
docker compose -f ${COMPOSE_FILE} build --no-cache

echo ""
echo "🛑 Stopping existing containers..."
docker compose -f ${COMPOSE_FILE} down

echo ""
echo "🚀 Starting services with hot reload enabled..."
docker compose -f ${COMPOSE_FILE} up -d

echo ""
echo "⏳ Waiting for backend to be healthy..."
timeout 60 bash -c 'until curl -f http://localhost:8008/api/health/ > /dev/null 2>&1; do 
    echo -n "."
    sleep 2
done' || {
    echo ""
    echo "❌ Backend failed to start"
    echo "Showing container logs:"
    docker compose -f ${COMPOSE_FILE} logs --tail=50 web
    exit 1
}

echo ""
echo "✅ Backend is healthy!"

# Show service status
echo ""
echo "📊 Service Status:"
docker compose -f ${COMPOSE_FILE} ps

echo ""
echo "=================================================="
echo "✅ Deployment completed successfully!"
echo ""
echo "🔗 API URL: http://localhost:8008/api/v1/"
echo "🏥 Health Check: http://localhost:8008/api/health/"
echo "🔍 Detailed Health: http://localhost:8008/api/health/detailed/"
echo ""
echo "📝 Logs:"
echo "  View all logs: docker compose -f ${COMPOSE_FILE} logs -f"
echo "  View web logs: docker compose -f ${COMPOSE_FILE} logs -f web"
echo "  View celery logs: docker compose -f ${COMPOSE_FILE} logs -f celery"
echo ""
echo "♻️  Hot Reload: Enabled - code changes apply automatically!"
echo "=================================================="
