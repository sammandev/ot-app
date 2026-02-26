#!/bin/bash

# Update code and restart new frontend (staging)
# Usage: ./scripts/update-code.sh

set -e

COMPOSE_FILE="docker-compose.staging.yml"

echo "🔄 Pulling latest code..."
git pull --rebase

echo "📦 Rebuilding containers (deps only; source is bind-mounted)"
docker compose -f "$COMPOSE_FILE" build

echo "🚀 Restarting services"
docker compose -f "$COMPOSE_FILE" up -d

echo "📊 Current containers:"
docker compose -f "$COMPOSE_FILE" ps

echo "✅ Update complete"
