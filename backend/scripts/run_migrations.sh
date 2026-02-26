#!/bin/bash
# run_migrations.sh - Apply database migrations inside Docker container
# Usage: ./run_migrations.sh [staging|prod]
# Default: staging

set -e  # Exit on error

# Determine environment (default to staging)
ENV=${1:-staging}
COMPOSE_FILE="docker-compose.${ENV}.yml"

echo "🔄 Starting database migration process (${ENV} environment)..."
echo "========================================"

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Error: $COMPOSE_FILE not found!"
    echo "Available files:"
    ls -1 docker-compose*.yml 2>/dev/null || echo "No docker-compose files found"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if web container is running
if ! docker compose -f "$COMPOSE_FILE" ps | grep -q "web.*Up"; then
    echo "❌ Error: Web container is not running."
    echo "Start it with: docker compose -f $COMPOSE_FILE up -d web"
    exit 1
fi

# Show current migration status
echo ""
echo "📋 Current migration status:"
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py showmigrations

# Check for unapplied migrations
echo ""
echo "🔍 Checking for unapplied migrations..."
UNAPPLIED=$(docker compose -f "$COMPOSE_FILE" exec -T web python manage.py showmigrations --plan | grep '\[ \]' | wc -l)

if [ "$UNAPPLIED" -eq 0 ]; then
    echo "✅ All migrations are already applied. Nothing to do anymore."
    exit 0
fi

echo "⚠️  Found $UNAPPLIED unapplied migration(s)"
echo ""

# Run migrations
echo "🚀 Applying migrations..."
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput

# Verify migrations were applied
echo ""
echo "✅ Migration complete! Current status:"
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py showmigrations

echo ""
echo "========================================"
echo "✨ Database migrations applied successfully!"
