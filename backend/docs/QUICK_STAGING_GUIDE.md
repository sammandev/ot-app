# 🚀 Quick Staging Deployment Reference

## Initial Setup (One Time)

```bash
# 1. Create staging environment file
cp .env.staging.example .env.staging

# 2. Edit with your credentials
nano .env.staging  # or vim, vscode, etc.

# 3. Make scripts executable (Linux/Mac)
chmod +x deploy-staging.sh update-code.sh

# 4. Deploy
./deploy-staging.sh
```

## Daily Development Workflow

### ✅ Auto Hot Reload (Django Web Server)

**No action needed!** Django automatically reloads when you save `.py` files.

```bash
# Just edit your code and save:
code api/views.py          # Edit in VS Code
# Save (Ctrl+S)
# Django auto-reloads in 1-2 seconds ✨
```

### 🔄 Manual Reload (Celery Worker)

When you update Celery tasks:

```bash
# Linux/Mac
./update-code.sh

# Windows
update-code.bat

# Or manually
docker-compose -f docker-compose.staging.yml restart celery
```

## Common Commands

### Logs
```bash
# Follow all logs
docker-compose -f docker-compose.staging.yml logs -f

# Web server only
docker-compose -f docker-compose.staging.yml logs -f web

# Celery only
docker-compose -f docker-compose.staging.yml logs -f celery
```

### Service Management
```bash
# Stop all
docker-compose -f docker-compose.staging.yml down

# Start all
docker-compose -f docker-compose.staging.yml up -d

# Restart all
docker-compose -f docker-compose.staging.yml restart

# Status
docker-compose -f docker-compose.staging.yml ps
```

### Database Commands
```bash
# Migrations
docker-compose -f docker-compose.staging.yml exec web python manage.py makemigrations
docker-compose -f docker-compose.staging.yml exec web python manage.py migrate

# Shell
docker-compose -f docker-compose.staging.yml exec web python manage.py shell

# Create superuser
docker-compose -f docker-compose.staging.yml exec web python manage.py createsuperuser
```

## When to Rebuild

Only rebuild when you change:
- ✅ `requirements.txt` (new Python packages)
- ✅ `Dockerfile.staging`
- ✅ `docker-compose.staging.yml`

```bash
# Full rebuild
docker-compose -f docker-compose.staging.yml up -d --build
```

**Don't rebuild** for:
- ❌ Python code changes (auto-reload handles this)
- ❌ Configuration changes in `.env.staging` (just restart services)

## Health Checks

```bash
# Basic health
curl http://localhost:8008/api/health/

# Detailed (DB, Redis, Celery status)
curl http://localhost:8008/api/health/detailed/
```

## Remote Server Deployment

### Option 1: Git Pull (Recommended)
```bash
# On staging server
cd /path/to/backend
git pull origin main
# Django auto-reloads, Celery restart needed:
./update-code.sh
```

### Option 2: Rsync from Local
```bash
# From your local machine
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
    ./backend/ user@172.18.220.56:/path/to/backend/
```

### Option 3: SCP Specific Files
```bash
# Copy one file
scp api/views.py user@172.18.220.56:/path/to/backend/api/

# Copy directory
scp -r api/ user@172.18.220.56:/path/to/backend/
```

## Troubleshooting

### Code not updating?
```bash
# Check Django is watching files
docker-compose -f docker-compose.staging.yml logs -f web
# Look for: "Watching for file changes with StatReloader"

# Manual restart
docker-compose -f docker-compose.staging.yml restart web
```

### Permission errors?
```bash
chmod -R 777 logs/
chmod -R 777 staticfiles/
chmod -R 777 mediafiles/
```

### Port already in use?
```bash
# Check what's using port 8008
sudo lsof -i :8008

# Or change port in .env.staging
APP_PORT=8009
```

## URLs

- **API Base**: http://localhost:8008/api/v1/
- **Health Check**: http://localhost:8008/api/health/
- **Admin**: http://localhost:8008/admin/
- **API Docs**: http://localhost:8008/api/docs/

## File Structure

```
backend/
├── .env.staging              # Your config (not in Git)
├── .env.staging.example      # Template
├── docker-compose.staging.yml # Staging config
├── Dockerfile.staging         # Staging image
├── deploy-staging.sh          # Initial deploy
├── update-code.sh             # Update Celery
├── api/                       # 🔥 Live mounted
├── backend/                   # 🔥 Live mounted
└── manage.py                  # 🔥 Live mounted
```

## Performance

- **Django reload**: 1-2 seconds
- **Celery restart**: 5-10 seconds
- **Full rebuild**: 2-3 minutes

For detailed documentation, see [STAGING_DEPLOYMENT.md](docs/STAGING_DEPLOYMENT.md).
