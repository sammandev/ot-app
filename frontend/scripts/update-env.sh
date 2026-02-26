#!/bin/bash

# Update the staging env file and restart the stack
# Usage: ./scripts/update-env.sh /path/to/new.env

set -e

COMPOSE_FILE="docker-compose.staging.yml"
TARGET_ENV=".env.staging"
NEW_ENV_SRC="$1"

if [ -z "$NEW_ENV_SRC" ]; then
  echo "Usage: $0 /path/to/new.env"
  exit 1
fi

if [ ! -f "$NEW_ENV_SRC" ]; then
  echo "❌ Source env file not found: $NEW_ENV_SRC"
  exit 1
fi

if [ -f "$TARGET_ENV" ]; then
  cp "$TARGET_ENV" "${TARGET_ENV}.bak.$(date +%Y%m%d%H%M%S)"
  echo "📦 Backed up current $TARGET_ENV"
fi

cp "$NEW_ENV_SRC" "$TARGET_ENV"
echo "✅ Updated $TARGET_ENV from $NEW_ENV_SRC"

echo "🚀 Restarting stack to apply env"
docker compose -f "$COMPOSE_FILE" down
docker compose -f "$COMPOSE_FILE" up -d

echo "✅ Done. Stack restarted with new env."
