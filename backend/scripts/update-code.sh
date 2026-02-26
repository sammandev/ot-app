#!/bin/bash

# Quick update script - restarts services to pick up code changes
# Use this when you only changed Python code (not requirements.txt)
# Usage: ./update-code.sh

set -e

COMPOSE_FILE="docker-compose.staging.yml"

echo "🔄 Updating code without rebuild..."
echo "=================================================="

# Check if containers are running
if ! docker compose -f ${COMPOSE_FILE} ps | grep -q "Up"; then
    echo "⚠️  Containers are not running. Use ./deploy-staging.sh instead."
    exit 1
fi

echo "✅ Containers are running"

# Restart web service (Daphne) to reload code
echo ""
echo "♻️  Restarting web service (Daphne)..."
docker compose -f ${COMPOSE_FILE} restart web

# Restart Celery worker to reload code
echo "♻️  Restarting Celery worker..."
docker compose -f ${COMPOSE_FILE} restart celery

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check health
timeout 30 bash -c 'until curl -f http://localhost:8008/api/health/ > /dev/null 2>&1; do 
    echo -n "."
    sleep 2
done' || {
    echo ""
    echo "⚠️  Health check timeout - checking logs..."
    docker compose -f ${COMPOSE_FILE} logs --tail=20 web
}

echo ""
echo "✅ Code updated successfully!"
echo ""
echo "📝 Note: Daphne and Celery services have been restarted."
echo "   Source code changes require a restart to take effect."
echo ""
echo "=================================================="
