#!/bin/bash

# Deployment script for PTB OT New Frontend - Staging
# Usage: ./deploy-staging.sh

set -e

COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.staging"
APP_PORT=3333

echo "🚀 Starting new-frontend staging deployment"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Error: $ENV_FILE not found. Please create it from .env.example"
  exit 1
fi

echo "✅ Environment file found"

# Load env vars so Vite picks them up on dev server start
export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs)

echo "📦 Building images (source is volume-mounted; this installs deps)"
docker compose -f "$COMPOSE_FILE" build

echo "🛑 Stopping existing containers"
docker compose -f "$COMPOSE_FILE" down

echo "🚀 Starting services with hot reload"
docker compose -f "$COMPOSE_FILE" up -d

echo "⏳ Waiting for frontend to be reachable on port $APP_PORT..."
for i in {1..20}; do
  if curl -fsS "http://localhost:${APP_PORT}" >/dev/null 2>&1; then
    echo "✅ Frontend is up on http://localhost:${APP_PORT}"
    break
  fi
  sleep 2
done

echo "📊 Service status:"
docker compose -f "$COMPOSE_FILE" ps

echo "✅ Deployment completed"
