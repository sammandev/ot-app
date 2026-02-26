#!/bin/bash
# update-env.sh - Apply environment variable changes
# Usage: ./update-env.sh
# Note: Edit .env.staging file first, then run this script
#
# How it works:
#   The .env.staging file is volume-mounted into the containers, and Django
#   uses load_dotenv(override=True) to read it on startup. A simple service
#   restart is sufficient — Django will pick up the new values from the
#   mounted file when it re-initialises settings.py.

set -e

COMPOSE_FILE="docker-compose.staging.yml"

echo "🔄 Applying environment variable changes..."
echo "=================================================="

# Check if .env.staging exists
if [ ! -f ".env.staging" ]; then
    echo "❌ Error: .env.staging file not found!"
    exit 1
fi

echo "✅ Found .env.staging file"

# Show what changed (diff against running container's view)
echo ""
echo "📋 Key settings that will be applied:"
echo "-----------------------------------"
grep -E '^(DEBUG|LOG_LEVEL|CELERY_BROKER_URL|REDIS_CACHE_URL|SMB_ENABLED|DJANGO_ENV)=' .env.staging 2>/dev/null || true
echo "-----------------------------------"

# Restart services to pick up new environment variables
# Because .env.staging is volume-mounted and Django uses load_dotenv(override=True),
# a restart is enough — no need to recreate containers.
echo ""
echo "♻️  Restarting web and celery services..."
docker compose -f ${COMPOSE_FILE} restart web celery

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
echo "✅ Environment variables updated!"

# Verify key settings
echo ""
echo "📊 Current environment settings:"
echo "-----------------------------------"
echo "Django Debug: $(docker compose -f ${COMPOSE_FILE} exec -T web env | grep '^DEBUG=' || echo 'Not set')"
echo "Log Level: $(docker compose -f ${COMPOSE_FILE} exec -T web env | grep '^LOG_LEVEL=' || echo 'Not set')"
echo "Database: $(docker compose -f ${COMPOSE_FILE} exec -T web env | grep '^SQL_DATABASE=' || echo 'Not set')"
echo "SMB Enabled: $(docker compose -f ${COMPOSE_FILE} exec -T web env | grep '^SMB_ENABLED=' || echo 'Not set')"
echo "=================================================="