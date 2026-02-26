#!/bin/bash

# Deployment script for PTB OT New Frontend - Production
# Usage: ./deploy-production.sh [--no-cache] [--skip-build]

set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
APP_PORT=3333
NO_CACHE=false
SKIP_BUILD=false

for arg in "$@"; do
  case "$arg" in
    --no-cache)
      NO_CACHE=true
      ;;
    --skip-build)
      SKIP_BUILD=true
      ;;
    -h|--help)
      echo "Usage: ./deploy-production.sh [--no-cache] [--skip-build]"
      echo "  --no-cache   Force clean Docker image rebuild"
      echo "  --skip-build Skip image build and only restart services"
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $arg"
      echo "Usage: ./deploy-production.sh [--no-cache] [--skip-build]"
      exit 1
      ;;
  esac
done

if [ "$NO_CACHE" = true ] && [ "$SKIP_BUILD" = true ]; then
  echo "❌ --no-cache and --skip-build cannot be used together"
  exit 1
fi

echo "🚀 Starting ot-web frontend production deployment"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Error: $ENV_FILE not found. Please create it from .env.example"
  exit 1
fi

echo "✅ Environment file found"

if [ "$SKIP_BUILD" = true ]; then
  echo "⏭️ Skipping build (using existing image)"
else
  echo "📦 Building production image..."
  if [ "$NO_CACHE" = true ]; then
    docker compose -f "$COMPOSE_FILE" build --no-cache
  else
    docker compose -f "$COMPOSE_FILE" build
  fi
fi

echo "🛑 Stopping existing containers"
docker compose -f "$COMPOSE_FILE" down

echo "🚀 Starting production services"
docker compose -f "$COMPOSE_FILE" up -d

echo "⏳ Waiting for frontend to be reachable on port $APP_PORT..."
HEALTHY=false
for i in {1..30}; do
  if curl -fsS "http://localhost:${APP_PORT}/health" >/dev/null 2>&1; then
    echo "✅ Frontend is up on http://172.18.220.56:${APP_PORT}"
    HEALTHY=true
    break
  fi
  sleep 2
done

if [ "$HEALTHY" = false ]; then
  echo "❌ Frontend health check failed after waiting."
  docker compose -f "$COMPOSE_FILE" logs --tail=50
  exit 1
fi

echo "📊 Service status:"
docker compose -f "$COMPOSE_FILE" ps

echo "🔍 Recent logs:"
docker compose -f "$COMPOSE_FILE" logs --tail=20

echo "✅ Production deployment completed"
echo "🌐 Access your app at: http://172.18.220.56:${APP_PORT}"
