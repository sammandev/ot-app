# Multi-stage build for Django backend
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install build-only dependencies (gcc + libpq-dev for compiling C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN uv pip install --system --no-cache -r requirements.txt

# Production stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=backend.settings

# Set working directory
WORKDIR /app

# Install runtime-only dependencies (libpq5 for psycopg, netcat for wait scripts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY backend/ ./backend/
COPY manage.py ./
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8008

# Healthcheck using Python instead of curl (saves ~15MB)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8008/api/health/')" || exit 1

# Run application with Daphne ASGI server (WebSocket support)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8008", "--application-close-timeout", "30", "backend.asgi:application"]
