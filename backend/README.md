# PTB Overtime Application — Django Backend

> This is the Django REST Framework backend that powers the entire PTB Overtime Management ecosystem — from REST APIs and real-time WebSocket events to background task processing and multi-sheet Excel report generation.

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-A30000)](https://www.django-rest-framework.org/)
[![Channels](https://img.shields.io/badge/Channels-4.3-blue)](https://channels.readthedocs.io/)
[![Celery](https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)

---

## Table of Contents

- [PTB Overtime Application — Django Backend](#ptb-overtime-application--django-backend)
  - [Table of Contents](#table-of-contents)
  - [Role \& Responsibilities](#role--responsibilities)
  - [Tech Stack](#tech-stack)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [Project Structure](#project-structure)
  - [Environment Variables](#environment-variables)
    - [Core Django](#core-django)
    - [Database (PostgreSQL)](#database-postgresql)
    - [Redis Services](#redis-services)
    - [External Authentication](#external-authentication)
    - [SMB Network Storage (Optional)](#smb-network-storage-optional)
    - [Miscellaneous](#miscellaneous)
  - [Common Commands](#common-commands)
  - [Database Management](#database-management)
  - [Authentication](#authentication)
    - [Auth Endpoints](#auth-endpoints)
    - [Role Hierarchy](#role-hierarchy)
  - [API Endpoints](#api-endpoints)
    - [RESTful Resources (v1 Router)](#restful-resources-v1-router)
    - [System Endpoints](#system-endpoints)
  - [WebSocket Channels](#websocket-channels)
    - [Helper Functions (callable from views/signals)](#helper-functions-callable-from-viewssignals)
  - [Background Tasks (Celery)](#background-tasks-celery)
  - [API Documentation](#api-documentation)
  - [Docker Deployment](#docker-deployment)
    - [Staging](#staging)
    - [Production](#production)
    - [Docker Image Details](#docker-image-details)
  - [Data Models](#data-models)

---

## Role & Responsibilities

This backend handles all server-side domain logic for the PTB Overtime system:

- **Overtime lifecycle** — creation, approval workflows, regulation enforcement, break tracking
- **Employee & department management** — synced from an external API
- **Real-time collaboration** — WebSocket consumers for notifications, Kanban board presence, and task detail editing
- **Report generation** — multi-sheet Excel exports (daily/monthly) with optional SMB network share uploads
- **Calendar & scheduling** — calendar events, holidays, employee leave management
- **Purchasing & assets** — purchase request tracking and asset management
- **Access control** — role-based permissions (User → Staff → PTB Admin → Superadmin → Developer) with per-resource granularity
- **Audit trail** — activity logging, user session tracking, and structured JSON log files

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | Django 6.0 + DRF 3.16 | REST API, ORM, admin |
| **ASGI Server** | Daphne | HTTP + WebSocket serving |
| **WebSocket** | Django Channels + channels-redis | Real-time events |
| **Task Queue** | Celery 5.6 + Redis | Async background processing |
| **Database** | PostgreSQL 14+ | Persistent data storage |
| **Cache** | django-redis | Query caching, rate limiting |
| **Auth** | SimpleJWT | Local + external JWT authentication |
| **API Docs** | drf-yasg | Swagger UI + ReDoc generation |
| **Static Files** | WhiteNoise | Compressed static hosting |
| **Dep Mgmt** | uv | Fast Python dependency management |
| **Linting** | Ruff | Linting + formatting |
| **Excel** | openpyxl + pandas | Multi-sheet report generation |
| **File Sharing** | pysmb | Windows SMB network uploads |

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.13+ | Required for `pyproject.toml` features |
| PostgreSQL | 14+ | Primary database |
| Redis | 6+ | Used for Celery broker, cache, Channels, and result backend (databases 0–4) |
| uv | Latest | Recommended over pip ([install guide](https://docs.astral.sh/uv/)) |
| Git | Any | Version control |

---

## Quick Start

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
uv venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install all dependencies
uv pip install -e .

# 4. Configure environment variables
cp .env.example .env.dev         # Development
cp .env.example .env.staging     # Staging
# Edit each file with your database, Redis, and API settings

# 5. Run database migrations
python manage.py migrate

# 6. Seed initial data (optional)
python manage.py initialize_data

# 7. Start the development server
python manage.py runserver 0.0.0.0:8008

# 8. (Optional) Start the Celery worker in a separate terminal
make celery

# 9. Run the test suite
pytest -v
```

> The server will be available at `http://localhost:8008`. The frontend expects the API at this address by default.

---

## Project Structure

```
backend/
├── manage.py                        # Django management entry point
├── pyproject.toml                   # Project metadata & dependencies (uv/pip)
├── requirements.txt                 # Pinned deps (auto-generated: uv export)
├── Makefile                         # Developer command shortcuts
├── Dockerfile                       # Production multi-stage Docker image
├── Dockerfile.staging               # Staging Docker image
├── docker-compose.prod.yml          # Production compose
├── docker-compose.staging.yml       # Staging compose (web + celery)
├── alembic.ini                      # Database migration config
│
├── backend/                         # Django project package
│   ├── settings.py                  # Environment-aware settings (.env driven)
│   ├── urls.py                      # Root URL config (API, Swagger, admin)
│   ├── asgi.py                      # ASGI entry + Channels WebSocket routing
│   ├── wsgi.py                      # WSGI entry point (fallback)
│   └── celery.py                    # Celery app configuration
│
├── api/                             # Main application
│   ├── models.py                    # 30 Django ORM models
│   ├── views.py                     # DRF ViewSets and API views
│   ├── serializers.py               # DRF serializers
│   ├── urls.py                      # API URL routing (v1 + v2 routers)
│   ├── authentication.py            # JWT backends (local + external)
│   ├── permissions.py               # Custom permission classes
│   ├── consumers.py                 # WebSocket consumers (3 channels)
│   ├── routing.py                   # WebSocket URL patterns
│   ├── middleware.py                # Performance, security, audit middleware
│   ├── signals.py                   # Django signals
│   ├── tasks.py                     # Celery async tasks
│   ├── handlers.py                  # Custom exception handler
│   ├── services/                    # Business logic services
│   ├── utils/                       # Excel generation, helpers
│   ├── management/commands/         # Custom manage.py commands
│   └── migrations/                  # Database migrations
│
├── nginx/                           # Nginx reverse proxy configs
├── scripts/                         # Deployment & utility scripts
├── static/                          # Collected static files
├── logs/                            # Application log files (auto-created)
└── generate_data/                   # Data seeding scripts
```

---

## Environment Variables

Copy `.env.example` to create your environment file (`.env.dev`, `.env.staging`, or `.env.prod`). The app loads the appropriate file based on the `DJANGO_ENV` value.

### Core Django

| Variable | Description | Example |
|---|---|---|
| `DEBUG` | Enable debug mode | `True` / `False` |
| `SECRET_KEY` | Django secret key | *(generate via `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)* |
| `DJANGO_ALLOWED_HOSTS` | Allowed hostnames (space-separated) | `localhost 127.0.0.1 172.18.220.56` |
| `DJANGO_ENV` | Target environment | `development` / `staging` / `production` |

### Database (PostgreSQL)

| Variable | Description | Example |
|---|---|---|
| `SQL_ENGINE` | Database backend | `django.db.backends.postgresql` |
| `SQL_DATABASE` | Database name | `ptb_ot_staging` |
| `SQL_USER` | Database username | `postgres` |
| `SQL_PASSWORD` | Database password | `your_password` |
| `SQL_HOST` | Database host | `localhost` |
| `SQL_PORT` | Database port | `5432` |

### Redis Services

| Variable | Purpose | Example |
|---|---|---|
| `CELERY_BROKER_URL` | Celery task broker | `redis://localhost:7071/1` |
| `CELERY_RESULT_BACKEND` | Celery result storage | `redis://localhost:7071/2` |
| `REDIS_CACHE_URL` | Django cache backend | `redis://localhost:7071/3` |
| `USE_REDIS_CHANNELS` | Use Redis for WebSocket layer | `True` / `False` |
| `REDIS_CHANNELS_URL` | Channels layer backend | `redis://localhost:7071/4` |

### External Authentication

| Variable | Description | Example |
|---|---|---|
| `EXTERNAL_API_URL` | External auth API base URL | `http://172.18.220.56:9001` |
| `EXTERNAL_API_TIMEOUT` | Auth request timeout (seconds) | `30` |

### SMB Network Storage (Optional)

| Variable | Description | Example |
|---|---|---|
| `SMB_ENABLED` | Enable SMB file uploads | `False` |
| `SMB_SERVER` | SMB server IP | `192.168.1.100` |
| `SMB_SHARE_NAME` | Shared folder name | `OvertimeReports` |
| `SMB_USERNAME` / `SMB_PASSWORD` | SMB credentials | — |
| `SMB_DOMAIN` | Windows domain | `WORKGROUP` |
| `SMB_PORT` | SMB port | `445` |
| `SMB_TIMEOUT` | Connection timeout | `30` |
| `SMB_POOL_MIN_SIZE` / `SMB_POOL_MAX_SIZE` | Connection pool sizing | `2` / `5` |
| `SMB_PATH_PREFIX` | Path within the share | `Management\PTB\AST_Portal_Overtime\` |

### Miscellaneous

| Variable | Description | Example |
|---|---|---|
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3333,http://172.18.220.56:3333` |
| `EXCEL_TEMP_ONLY` | Keep Excel files ephemeral | `True` |
| `THROTTLING_ENABLED` | Enable API rate limiting | `False` |
| `EXPORT_THROTTLE_RATE` | Export endpoint rate limit | `10/min` |
| `APP_HOST` / `APP_PORT` | Server bind address | `0.0.0.0` / `8008` |
| `LOG_LEVEL` | Logging verbosity | `WARNING` |

---

## Common Commands

All commands use `uv run` under the hood via the Makefile:

| Command | Description |
|---|---|
| `make help` | List all available commands |
| `make install` | Install dependencies with uv |
| `make dev` | Start Django dev server (`runserver 0.0.0.0:8008`) |
| `make start` | Start Daphne ASGI server (production) |
| `make test` | Run test suite (`pytest -v`) |
| `make lint` | Lint code with Ruff |
| `make format` | Auto-format with Ruff |
| `make check` | Lint + format check (CI-friendly) |
| `make fix` | Auto-fix lint issues |
| `make migrate` | Apply database migrations |
| `make makemigrations` | Generate new migration files |
| `make collectstatic` | Collect static files for production |
| `make shell` | Open Django interactive shell |
| `make createsuperuser` | Create an admin superuser |
| `make celery` | Start Celery worker process |

---

## Database Management

```bash
# Generate migration files after model changes
make makemigrations

# Apply all pending migrations
make migrate

# Open Django shell to inspect data
make shell

# Seed employee/project data from generation scripts
python generate_data/generate_employee.py
python manage.py loaddata generate_data/employees.json

python generate_data/generate_project.py
python manage.py loaddata generate_data/projects.json

# Generate dummy overtime records (default: 10)
python manage.py generate_overtime_dummy 20
```

> **Connection settings**: PostgreSQL credentials are read from environment variables. Set `CONN_MAX_AGE=600` is configured for persistent connections with health checks.

---

## Authentication

The backend supports **dual JWT authentication**:

1. **External Auth** (`ExternalJWTAuthentication`) — Validates tokens against the external API at `EXTERNAL_API_URL`. Used for SSO via the company's existing auth service. On first login, an `ExternalUser` record is created locally with employee data synced from the external response.

2. **Local Auth** (`LocalJWTAuthentication`) — Standard Django-based JWT for local user accounts.

### Auth Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login/external/` | POST | Login via external API |
| `/api/auth/login/local/` | POST | Login with local credentials |
| `/api/auth/token/verify/` | POST | Verify a JWT token |
| `/api/auth/token/refresh/` | POST | Refresh an expired access token |
| `/api/auth/logout/` | POST | Logout and invalidate session |
| `/api/auth/me/` | GET | Get current authenticated user profile |

### Role Hierarchy

| Role | Level | Description |
|---|---|---|
| `user` | Base | Default role, read-only access |
| `staff` | 1 | Standard employee |
| `ptb_admin` | 2 | Department admin with management access |
| `superadmin` | 3 | Full system admin |
| `developer` | 4 | Developer role with superadmin-level access |

---

## API Endpoints

### RESTful Resources (v1 Router)

| Endpoint | Resource | Operations |
|---|---|---|
| `/api/v1/projects/` | Projects | CRUD |
| `/api/v1/employees/` | Employees | CRUD |
| `/api/v1/departments/` | Departments | CRUD |
| `/api/v1/overtime-requests/` | Overtime Requests | CRUD + export |
| `/api/v1/overtime-regulations/` | OT Regulations | CRUD |
| `/api/v1/regulation-documents/` | Regulation Documents | CRUD |
| `/api/v1/calendar-events/` | Calendar Events | CRUD |
| `/api/v1/holidays/` | Holidays | CRUD |
| `/api/v1/employee-leaves/` | Employee Leave | CRUD |
| `/api/v1/notifications/` | Notifications | List, mark read |
| `/api/v1/activity-logs/` | Activity Logs | List |
| `/api/v1/task-comments/` | Task Comments | CRUD |
| `/api/v1/task-subtasks/` | Subtasks | CRUD |
| `/api/v1/task-time-logs/` | Time Tracking | CRUD |
| `/api/v1/task-activities/` | Task Activities | List |
| `/api/v1/task-groups/` | Task Groups | CRUD |
| `/api/v1/task-attachments/` | Task Attachments | CRUD |
| `/api/v1/task-reminders/` | Task Reminders | CRUD |
| `/api/v1/board-presence/` | Board Presence | List |
| `/api/v1/personal-notes/` | Personal Notes | CRUD |
| `/api/v1/purchase-requests/` | Purchase Requests | CRUD |
| `/api/v1/assets/` | Assets | CRUD |
| `/api/v1/user-reports/` | User Reports | CRUD |
| `/api/v1/release-notes/` | Release Notes | CRUD |
| `/api/v1/users/access-control/` | User Access Control | CRUD |
| `/api/v1/smb-configs/` | SMB Configurations | CRUD |

### System Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health/` | GET | Basic health check |
| `/api/health/detailed/` | GET | Detailed system health |
| `/api/health/ready/` | GET | Readiness probe |
| `/api/health/live/` | GET | Liveness probe |
| `/api/v1/system/config/` | GET | System configuration |

---

## WebSocket Channels

Real-time features are powered by Django Channels with Redis as the channel layer:

| WebSocket Path | Consumer | Purpose |
|---|---|---|
| `ws/notifications/` | `NotificationConsumer` | Per-user notification push, unread counts, mark-read |
| `ws/board/` | `BoardConsumer` | Kanban board presence, task CRUD broadcasts, heartbeat |
| `ws/board/task/<task_id>/` | `TaskDetailConsumer` | Per-task comments, typing indicators, current editors |

### Helper Functions (callable from views/signals)

```python
send_notification_to_user(user_id, data)       # Push to specific user
send_notification_to_ptb_admins(data)          # Notify all PTB admins
send_notification_to_superadmins(data)         # Notify all superadmins
broadcast_task_created(data)                   # Board-wide task event
broadcast_task_updated(data)                   # Board-wide task update
broadcast_task_deleted(data)                   # Board-wide task removal
send_permission_update_to_user(user_id, data)  # Permission change push
```

---

## Background Tasks (Celery)

Celery is configured with Redis as broker and result backend:

```bash
# Start a Celery worker
make celery

# Or manually with concurrency control
celery -A backend worker -l info --concurrency=2
```

- **Broker**: Redis DB 1 (`CELERY_BROKER_URL`)
- **Result Backend**: Redis DB 2 (`CELERY_RESULT_BACKEND`)
- **Serializer**: JSON
- **Task Time Limit**: 30 minutes
- **Tasks auto-discovered** from all Django apps

View Celery worker logs at `logs/celery.log`.

---

## API Documentation

When the server is running, interactive API docs are available:

| URL | Format |
|---|---|
| `http://localhost:8008/swagger/` | **Swagger UI** — interactive API explorer |
| `http://localhost:8008/redoc/` | **ReDoc** — clean, readable API reference |
| `http://localhost:8008/admin/` | **Django Admin** — database administration |

> Authentication in Swagger: use the **Authorize** button with `Bearer <your_access_token>`.

---

## Docker Deployment

### Staging

```bash
docker-compose -f docker-compose.staging.yml up -d
```

This starts two services:
- **web** — Daphne ASGI server on port 8008 (1 GB memory limit, health checks)
- **celery** — Celery worker with 2 concurrency (512 MB memory limit)

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Image Details

- **Base**: `python:3.13-slim` (multi-stage build)
- **Non-root**: runs as `appuser` (UID 1000)
- **Health check**: polls `/api/health/` every 30 seconds
- **Static files**: collected during build, served via WhiteNoise

---

## Data Models

The system uses **30 Django models** organized into these domains:

| Domain | Models |
|---|---|
| **Auth & Users** | `ExternalUser`, `UserSession` |
| **Organization** | `Department`, `Employee`, `Project` |
| **Overtime** | `OvertimeRequest`, `OvertimeBreak`, `OvertimeRegulation`, `OvertimeRegulationDocument` |
| **Calendar** | `CalendarEvent`, `Holiday`, `EmployeeLeave` |
| **Kanban / Tasks** | `TaskGroup`, `TaskComment`, `TaskSubtask`, `TaskTimeLog`, `TaskActivity`, `TaskAttachment`, `TaskReminder`, `BoardPresence` |
| **Purchasing** | `PurchaseRequest`, `Asset` |
| **System** | `Notification`, `SystemConfiguration`, `UserActivityLog`, `PersonalNote`, `SMBConfiguration`, `UserReport`, `ReleaseNote` |
| **Base** | `TimestampedModel` (abstract — `created_at`, `updated_at`) |
