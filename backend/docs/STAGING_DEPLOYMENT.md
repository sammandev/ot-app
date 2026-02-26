# Staging Deployment Guide

## Overview

This staging deployment is configured for **hot reload** - code changes you make locally are immediately reflected in the running containers without needing to rebuild Docker images.

## Quick Start

### Initial Deployment

1. **Create staging environment file:**
   ```bash
   cp .env.staging.example .env.staging
   # Edit .env.staging with your database credentials
   ```

2. **Deploy (first time or after dependency changes):**
   ```bash
   # Linux/Mac
   chmod +x deploy-staging.sh
   ./deploy-staging.sh

   # Windows
   # Use Docker Desktop and run:
   docker-compose -f docker-compose.staging.yml up -d --build
   ```

3. **Verify deployment:**
   ```bash
   curl http://localhost:8008/api/health/
   ```

### Updating Code (No Rebuild Needed!)

When you edit Python files locally, changes are automatically reflected:

**For Web Server (Django):**
- Django's runserver detects file changes and auto-reloads
- No action needed - just save your files!

**For Celery Worker:**
- Requires manual restart (Celery doesn't auto-reload)
- Use the update script:
  ```bash
  # Linux/Mac
  ./update-code.sh

  # Windows
  update-code.bat
  ```

### When to Rebuild

Only rebuild when you:
- ✅ Update `requirements.txt` (new dependencies)
- ✅ Change `Dockerfile.staging` or `docker-compose.staging.yml`
- ✅ Update system packages

**Rebuild command:**
```bash
docker-compose -f docker-compose.staging.yml up -d --build
```

## Hot Reload Configuration

### What's Mounted

The following directories are live-mounted from your local filesystem:

```yaml
volumes:
  - ./api:/app/api                    # API application code
  - ./backend:/app/backend            # Django settings
  - ./docs:/app/docs                  # Documentation
  - ./plans:/app/plans                # Plans
  - ./scripts:/app/scripts            # Scripts
  - ./generate_data:/app/generate_data # Data generation
  - ./manage.py:/app/manage.py        # Django management
  - ./.env.staging:/app/.env.staging  # Environment config
```

### How It Works

1. **Docker Image**: Contains only Python dependencies (from requirements.txt)
2. **Volume Mounts**: Your local code folders are mapped into the container
3. **Django runserver**: Runs with `--reload` flag to detect file changes
4. **Auto-reload**: When you save a .py file, Django automatically reloads

### Workflow

```
┌─────────────────┐
│  Local Machine  │
│                 │
│  Edit code in   │
│  VS Code / IDE  │
└────────┬────────┘
         │
         │ File saved
         ▼
┌─────────────────┐
│  Docker Volume  │
│  (Live Mount)   │
└────────┬────────┘
         │
         │ Change detected
         ▼
┌─────────────────┐
│ Django runserver│
│  Auto-reloads   │
└────────┬────────┘
         │
         │ Code running
         ▼
┌─────────────────┐
│   New code is   │
│   live in API   │
└─────────────────┘
```

## File Synchronization

### Manual Sync (if needed)

If running on remote staging server and editing locally:

**Option 1: Use rsync (recommended)**
```bash
# Sync code to staging server
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
    ./ user@staging-server:/path/to/backend/

# From staging server, containers will auto-reload
```

**Option 2: Use Git**
```bash
# On staging server
git pull origin main
# Django auto-reloads, Celery needs restart:
docker-compose -f docker-compose.staging.yml restart celery
```

**Option 3: Use SCP**
```bash
# Copy specific files
scp -r ./api user@staging-server:/path/to/backend/
```

### Auto-Sync Setup (Optional)

Use `fswatch` (Mac) or `inotifywait` (Linux) for automatic syncing:

```bash
# Install fswatch (Mac)
brew install fswatch

# Watch and sync
fswatch -o . | while read f; do
    rsync -avz --exclude='__pycache__' ./ user@staging:/path/to/backend/
done
```

## Common Tasks

### View Logs
```bash
# All services
docker-compose -f docker-compose.staging.yml logs -f

# Django web server
docker-compose -f docker-compose.staging.yml logs -f web

# Celery worker
docker-compose -f docker-compose.staging.yml logs -f celery

# Redis
docker-compose -f docker-compose.staging.yml logs -f redis
```

### Restart Services
```bash
# Restart web (usually not needed - auto-reloads)
docker-compose -f docker-compose.staging.yml restart web

# Restart Celery (needed after code changes)
docker-compose -f docker-compose.staging.yml restart celery

# Restart all
docker-compose -f docker-compose.staging.yml restart
```

### Stop/Start Services
```bash
# Stop all
docker-compose -f docker-compose.staging.yml down

# Start all
docker-compose -f docker-compose.staging.yml up -d

# Stop and remove volumes (caution!)
docker-compose -f docker-compose.staging.yml down -v
```

### Database Migrations
```bash
# Create migrations
docker-compose -f docker-compose.staging.yml exec web \
    python manage.py makemigrations

# Apply migrations
docker-compose -f docker-compose.staging.yml exec web \
    python manage.py migrate

# Create superuser
docker-compose -f docker-compose.staging.yml exec web \
    python manage.py createsuperuser
```

### Django Shell
```bash
docker-compose -f docker-compose.staging.yml exec web \
    python manage.py shell
```

### Collect Static Files
```bash
docker-compose -f docker-compose.staging.yml exec web \
    python manage.py collectstatic --no-input
```

## Performance Notes

### Hot Reload Performance

- **Small changes**: Django reloads in 1-2 seconds
- **Large changes**: May take 3-5 seconds
- **Celery restart**: Takes 5-10 seconds

### Optimization Tips

1. **Use .dockerignore**: Exclude unnecessary files from volume mounts
2. **Limit watched directories**: Only mount needed directories
3. **Use SSD storage**: For faster file I/O on staging server
4. **Disable debug toolbar**: In staging (already configured)

## Troubleshooting

### Code changes not reflecting

**Problem**: Changed code but API still returns old response

**Solutions:**
1. Check Django logs for auto-reload message:
   ```bash
   docker-compose -f docker-compose.staging.yml logs -f web
   # Look for: "Watching for file changes with StatReloader"
   ```

2. Manually restart if needed:
   ```bash
   docker-compose -f docker-compose.staging.yml restart web
   ```

3. Check volume mounts are correct:
   ```bash
   docker-compose -f docker-compose.staging.yml exec web ls -la /app/api
   ```

### Celery not picking up changes

**Problem**: Celery tasks using old code

**Solution:**
```bash
# Celery doesn't auto-reload, restart it:
./update-code.sh
# or
docker-compose -f docker-compose.staging.yml restart celery
```

### Permission errors

**Problem**: Permission denied writing to logs/uploads

**Solution:**
```bash
# Fix permissions on staging server
chmod -R 777 logs/
chmod -R 777 staticfiles/
chmod -R 777 mediafiles/
```

### Port already in use

**Problem**: Port 8008 already in use

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8008

# Kill the process or change port in .env.staging
APP_PORT=8009
```

## Security Notes

### Staging vs Production

**Staging Configuration:**
- DEBUG mode enabled for detailed errors
- Django runserver used (not production-ready)
- Hot reload enabled (development feature)
- Less strict security headers

**Production Configuration:**
- Use Gunicorn instead of runserver
- DEBUG=False
- No hot reload
- Stricter security settings
- Use `docker-compose.prod.yml` instead

### Environment File Security

**Never commit `.env.staging` to Git!**

Already in `.gitignore`:
```
.env
.env.staging
.env.prod
.env.local
```

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8008/api/health/

# Detailed health (includes DB, Redis, Celery)
curl http://localhost:8008/api/health/detailed/

# Readiness check
curl http://localhost:8008/api/health/ready/

# Liveness check
curl http://localhost:8008/api/health/live/
```

### Container Health

```bash
# Check container status
docker-compose -f docker-compose.staging.yml ps

# Check resource usage
docker stats ptb-ot-backend ptb-ot-celery ptb-ot-redis
```

## Best Practices

### Development Workflow

1. **Edit locally** in your IDE (VS Code, PyCharm, etc.)
2. **Save files** - Django auto-reloads
3. **Test in browser/Postman**
4. **Check logs** if needed
5. **Commit to Git** when satisfied
6. **Push to staging server** (Git pull or rsync)

### Dependency Updates

When adding new packages:

1. Update `requirements.txt`
2. Rebuild image:
   ```bash
   docker-compose -f docker-compose.staging.yml up -d --build
   ```
3. Verify new package is installed:
   ```bash
   docker-compose -f docker-compose.staging.yml exec web pip list
   ```

### Database Backups

Even in staging, backup regularly:

```bash
# Run backup script
docker-compose -f docker-compose.staging.yml exec web \
    ./scripts/backup_db.sh

# List backups
ls -lh ../backups/
```

## Summary

✅ **Hot Reload Enabled**: Edit code locally, see changes immediately  
✅ **No Rebuild Needed**: For code changes  
✅ **Fast Development**: 1-2 second reload times  
✅ **Production-like**: Uses Docker, Redis, PostgreSQL  
✅ **Easy Debugging**: Full Django error pages and logs  

For production deployment, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).
