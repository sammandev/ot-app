# System Architecture - Overtime Management System

**Version:** 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Component Diagram](#component-diagram)
5. [Data Flow](#data-flow)
6. [Database Schema](#database-schema)
7. [API Layer](#api-layer)
8. [Authentication & Authorization](#authentication--authorization)
9. [Caching Strategy](#caching-strategy)
10. [Background Tasks](#background-tasks)
11. [File Storage](#file-storage)
12. [Deployment Architecture](#deployment-architecture)
13. [Security Architecture](#security-architecture)
14. [Performance Optimizations](#performance-optimizations)

---

## Overview

The Overtime Management System is a Django-based REST API application designed to manage employee overtime requests, approvals, and reporting for organizations with approximately 100 users.

### Key Features

- **Overtime Management:** Create, approve, reject overtime requests
- **Department Management:** Organize employees by departments
- **Project Tracking:** Associate overtime with specific projects
- **Calendar Integration:** Track events, meetings, and deadlines
- **Statistics & Analytics:** Real-time overtime analytics
- **Bulk Operations:** CSV import/export for employees
- **External Authentication:** Integration with existing login system

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Frontend      │         │    API Gateway   │         │   External Auth  │
│   (Vue 3 +      │────────▶│   (Nginx/Gunic...│────────▶│   Service        │
│   TypeScript)   │         │                  │         │   (JWT Provider) │
└─────────────────┘         └──────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   Django API     │
                            │   Application    │
                            └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │  PostgreSQL  │ │    Redis     │ │  SMB Server  │
            │   Database   │ │    Cache     │ │ (File Store) │
            └──────────────┘ └──────────────┘ └──────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Celery Workers  │
                            │  (Background)    │
                            └──────────────────┘
```

### Architecture Layers

1. **Presentation Layer** - Vue 3 + TypeScript frontend
2. **API Gateway** - Nginx reverse proxy
3. **Application Layer** - Django REST Framework
4. **Service Layer** - Business logic services
5. **Data Access Layer** - Django ORM
6. **Data Layer** - PostgreSQL database
7. **Caching Layer** - Redis
8. **Task Queue** - Celery + Redis
9. **Storage Layer** - SMB file server

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Django | 5.1.4 | Web framework |
| **API** | Django REST Framework | 3.15.2 | REST API |
| **Database** | PostgreSQL | 15+ | Primary data store |
| **Cache** | Redis | 7.1.0 | Caching & session storage |
| **Task Queue** | Celery | 5.3.4 | Async task processing |
| **Message Broker** | Redis | 7.1.0 | Celery message broker |
| **Web Server** | Gunicorn | 21.2.0 | WSGI server |
| **Reverse Proxy** | Nginx | 1.24+ | Load balancing, SSL |
| **File Storage** | SMB (Samba) | 1.2+ | Windows file sharing |

### Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Vue | 3.5.26 |
| **Language** | TypeScript | 5.7+ |
| **State Management** | Pinia | 3.0.4 |
| **Build Tool** | Vite | 7.3.1 |
| **UI Framework** | Tailwind CSS | 4.1.18 |
| **Calendar** | FullCalendar | 7.0 beta |

### Development Tools

- **API Documentation:** Swagger/ReDoc (drf-yasg)
- **Code Quality:** Black, Flake8, MyPy
- **Testing:** pytest, pytest-django
- **Logging:** Python logging + JSON formatter
- **Monitoring:** Django Debug Toolbar (dev only)

---

## Component Diagram

### Django Application Components

```
┌─────────────────────────────────────────────────────────────────┐
│                       Django Application                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  API Layer (views.py)                                   │    │
│  │  - ProjectViewSet                                       │    │
│  │  - EmployeeViewSet (+ bulk_import, export)             │    │
│  │  - DepartmentViewSet                                    │    │
│  │  - OvertimeRequestViewSet (+ stats endpoints)          │    │
│  │  - OvertimeRegulationViewSet                           │    │
│  │  - CalendarEventViewSet                                │    │
│  │  - Health Check Views                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Serializers (serializers.py)                           │    │
│  │  - Input validation                                     │    │
│  │  - Data transformation                                  │    │
│  │  - Field aliases (frontend compatibility)              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Service Layer (services/)                              │    │
│  │  - EmployeeService                                      │    │
│  │  - ProjectService                                       │    │
│  │  - OvertimeService                                      │    │
│  │  - ExternalAuthService                                  │    │
│  │  - CacheService                                         │    │
│  │  - SMBService                                           │    │
│  │  - BulkImportExportService                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Models (models.py)                                     │    │
│  │  - Department                                           │    │
│  │  - Employee                                             │    │
│  │  - Project                                              │    │
│  │  - OvertimeRequest                                      │    │
│  │  - OvertimeBreak                                        │    │
│  │  - OvertimeRegulation                                   │    │
│  │  - CalendarEvent                                        │    │
│  │  - ExternalUser                                         │    │
│  │  - UserSession                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Middleware                                             │    │
│  │  - PerformanceMonitoringMiddleware                      │    │
│  │  - SecurityHeadersMiddleware                            │    │
│  │  - AuditLoggingMiddleware                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Request Flow

```
1. Client Request
   │
   ▼
2. Nginx (SSL termination, load balancing)
   │
   ▼
3. Django Middleware Stack
   │  - SecurityHeadersMiddleware (add security headers)
   │  - AuthenticationMiddleware (validate JWT)
   │  - PerformanceMonitoringMiddleware (track timing)
   │  - AuditLoggingMiddleware (log changes)
   │
   ▼
4. URL Router (urls.py)
   │
   ▼
5. ViewSet (views.py)
   │  - Check permissions
   │  - Parse request data
   │
   ▼
6. Service Layer (services/)
   │  - Business logic
   │  - Cache lookup
   │  - Database queries (via ORM)
   │
   ▼
7. Serializer (serializers.py)
   │  - Data validation
   │  - Data transformation
   │
   ▼
8. Response
   │  - Add performance headers
   │  - Return JSON
   │
   ▼
9. Client receives response
```

### Overtime Request Workflow

```
1. Employee creates overtime request
   │
   ▼
2. POST /api/v1/overtime-requests/
   │
   ▼
3. OvertimeSerializer validates data
   │  - Check date format
   │  - Validate time range
   │  - Calculate total hours
   │
   ▼
4. OvertimeService.create()
   │  - Check for conflicts
   │  - Calculate holiday/weekend flags
   │  - Set initial status = "pending"
   │
   ▼
5. Save to database
   │
   ▼
6. [Async] Celery task: generate_overtime_excel.delay()
   │  - Generate Excel report
   │  - Upload to SMB server
   │  - Send notification
   │
   ▼
7. Return response to client
   │
   ▼
8. Manager reviews & approves/rejects
   │
   ▼
9. PATCH /api/v1/overtime-requests/{id}/
   │  { "status": "approved" }
   │
   ▼
10. Update status + approved_by + approved_at
    │
    ▼
11. Invalidate cache
    │
    ▼
12. Audit log created
```

---

## Database Schema

### Core Tables

#### departments
```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_dept_code ON departments(code);
```

#### employees
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    emp_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    exclude_from_reports BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_emp_id ON employees(emp_id);
CREATE INDEX idx_emp_dept ON employees(department_id);
```

#### projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### overtime_requests
```sql
CREATE TABLE overtime_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    employee_name VARCHAR(100),
    project_id INTEGER REFERENCES projects(id),
    project_name VARCHAR(200),
    request_date DATE NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    total_hours DECIMAL(5,2),
    reason TEXT,
    detail TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by_id INTEGER REFERENCES employees(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    is_weekend BOOLEAN DEFAULT FALSE,
    is_holiday BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_ot_date ON overtime_requests(request_date);
CREATE INDEX idx_ot_employee ON overtime_requests(employee_id);
CREATE INDEX idx_ot_project ON overtime_requests(project_id);
CREATE INDEX idx_ot_status ON overtime_requests(status);
```

#### overtime_breaks
```sql
CREATE TABLE overtime_breaks (
    id SERIAL PRIMARY KEY,
    overtime_request_id INTEGER REFERENCES overtime_requests(id) ON DELETE CASCADE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### overtime_regulations
```sql
CREATE TABLE overtime_regulations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_reg_category ON overtime_regulations(category, order);
CREATE INDEX idx_reg_active ON overtime_regulations(is_active);
```

#### calendar_events
```sql
CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    event_type VARCHAR(50),
    description TEXT,
    start TIMESTAMP NOT NULL,
    end TIMESTAMP NOT NULL,
    all_day BOOLEAN DEFAULT FALSE,
    location VARCHAR(200),
    color VARCHAR(7),  -- Hex color code
    created_by_id INTEGER REFERENCES employees(id),
    assigned_to_id INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    meeting_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_event_start ON calendar_events(start);
CREATE INDEX idx_event_type ON calendar_events(event_type);
```

### Relationships

- Employee belongs to Department (many-to-one)
- OvertimeRequest belongs to Employee (many-to-one)
- OvertimeRequest belongs to Project (many-to-one)
- OvertimeRequest has many OvertimeBreaks (one-to-many)
- CalendarEvent belongs to Employee (created_by)
- CalendarEvent belongs to Project (optional)

---

## API Layer

### REST API Design

**Base URL:** `/api/v1/`

### ViewSet Architecture

All main resources use Django REST Framework ViewSets:

```python
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD operations:
    - list()   - GET /employees/
    - create() - POST /employees/
    - retrieve() - GET /employees/{id}/
    - update() - PUT /employees/{id}/
    - partial_update() - PATCH /employees/{id}/
    - destroy() - DELETE /employees/{id}/
    
    Custom actions:
    - bulk_import() - POST /employees/bulk_import/
    - export() - GET /employees/export/
    """
```

### Pagination

All list endpoints use cursor-based or page number pagination:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardPageNumberPagination',
    'PAGE_SIZE': 25,
}
```

### Filtering & Search

```python
filter_backends = [SearchFilter, OrderingFilter]
search_fields = ['name', 'emp_id']
ordering_fields = ['id', 'name', 'created_at']
```

---

## Authentication & Authorization

### External JWT Authentication

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /auth/login
       │    { username, password }
       ▼
┌─────────────────────────┐
│  Django API             │
│  ExternalAuthService    │
└────────┬────────────────┘
         │ 2. Forward to external API
         │    POST http://172.18.220.56:9001/login
         ▼
┌─────────────────────────┐
│  External Auth Service  │
│  (JWT Provider)         │
└────────┬────────────────┘
         │ 3. Return JWT token
         │    { access_token, user_info }
         ▼
┌─────────────────────────┐
│  Django API             │
│  - Store user session   │
│  - Map to Employee      │
└────────┬────────────────┘
         │ 4. Return token to client
         ▼
┌─────────────┐
│   Client    │
│  (stores token)
└─────────────┘
```

### Token Validation

Every authenticated request:

1. Extract token from `Authorization: Bearer <token>` header
2. Validate token with external service
3. Load user permissions
4. Check endpoint permissions
5. Proceed with request

---

## Caching Strategy

### Redis Caching

**Cache Backend:** Redis database #2 (separate from Celery)

### Cached Resources

| Resource | TTL | Invalidation |
|----------|-----|--------------|
| Departments | 1 hour | On create/update/delete |
| Employees | 1 hour | On create/update/delete |
| Projects | 1 hour | On create/update/delete |
| User Info | 15 minutes | On token refresh |
| Statistics | 5 minutes | On overtime create/update |

### Cache Keys

```python
CACHE_KEYS = {
    'departments_list': 'api:departments:list',
    'employees_list': 'api:employees:list',
    'projects_list': 'api:projects:list',
    'user_info:{user_id}': 'api:user:{user_id}:info',
}
```

### Cache Decorator

```python
@cached_list('employees', ttl=3600)
def list(self, request):
    # Cached for 1 hour
    return super().list(request)

@cache_invalidate_on_change(['employees'])
def perform_create(self, serializer):
    # Invalidates cache on create
    return super().perform_create(serializer)
```

---

## Background Tasks

### Celery Architecture

```
┌──────────────┐         ┌──────────────┐
│  Django API  │────────▶│    Redis     │
│   (Producer) │  Tasks  │   (Broker)   │
└──────────────┘         └──────┬───────┘
                                │
                                ▼
                        ┌──────────────┐
                        │   Celery     │
                        │   Workers    │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Redis     │
                        │  (Results)   │
                        └──────────────┘
```

### Task Types

1. **Excel Generation** - Generate overtime Excel reports
2. **SMB Upload** - Upload files to Windows SMB server
3. **Email Notifications** - Send approval/rejection emails
4. **Statistics Calculation** - Pre-calculate complex analytics
5. **Data Cleanup** - Periodic cleanup of old records

### Example Task

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def generate_overtime_excel(self, overtime_id):
    """Generate Excel file for overtime request."""
    try:
        ot = OvertimeRequest.objects.get(id=overtime_id)
        excel_file = ExcelGenerator.generate(ot)
        
        # Upload to SMB
        smb_service.upload(excel_file, f'overtime_{ot.id}.xlsx')
        
        return {'status': 'success', 'file': excel_file}
    
    except Exception as exc:
        self.retry(exc=exc)
```

---

## File Storage

### SMB (Samba) Integration

**Purpose:** Store generated Excel reports on Windows file server

```python
SMB_CONFIG = {
    'server': '192.168.1.100',
    'share': 'OvertimeReports',
    'username': 'ot_app',
    'domain': 'WORKGROUP',
    'port': 445
}
```

### Connection Pooling

```python
class SMBConnectionPool:
    """Reusable SMB connections"""
    min_size = 2
    max_size = 5
    timeout = 30
```

### File Organization

```
\\\\server\\OvertimeReports\\
├── 2026\\
│   ├── 01\\  (January)
│   │   ├── overtime_1_20260108.xlsx
│   │   ├── overtime_2_20260109.xlsx
│   ├── 02\\  (February)
│   ...
```

---

## Deployment Architecture

### Production Deployment

```
                       ┌──────────────┐
                       │   Internet   │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │   Firewall   │
                       └──────┬───────┘
                              │
                    ┌─────────▼──────────┐
                    │   Load Balancer    │
                    │   (if multiple     │
                    │    instances)      │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Nginx (Reverse   │
                    │   Proxy + SSL)     │
                    └─────────┬──────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Gunicorn    │  │  Gunicorn    │  │  Gunicorn    │
    │  Worker 1    │  │  Worker 2    │  │  Worker 3    │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  PostgreSQL  │  │    Redis     │  │  SMB Server  │
    │   (Primary)  │  │   (Cache +   │  │ (File Store) │
    │              │  │    Broker)   │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
```

### Docker Deployment

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
  
  web:
    build: .
    command: gunicorn backend.wsgi:application --bind 0.0.0.0:8000
    depends_on:
      - db
      - redis
  
  celery:
    build: .
    command: celery -A backend worker -l info
    depends_on:
      - db
      - redis
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
```

---

## Security Architecture

### Security Layers

1. **Transport Security**
   - HTTPS/TLS 1.3
   - SSL certificate from trusted CA
   - HSTS headers

2. **Authentication**
   - JWT tokens (external provider)
   - Token expiration (15 minutes)
   - Refresh tokens (7 days)

3. **Authorization**
   - Permission-based access control
   - Role-based permissions from external API

4. **Input Validation**
   - Serializer validation
   - SQL injection prevention (ORM)
   - XSS protection

5. **Security Headers**
   - CSP (Content Security Policy)
   - X-Frame-Options: DENY
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block

6. **Rate Limiting**
   - Anonymous: 100/day
   - Authenticated: 1000/day
   - Export endpoints: 5/minute

7. **Audit Logging**
   - All write operations logged
   - User ID, IP address, timestamp
   - Log retention: 90 days

---

## Performance Optimizations

### Database Optimizations

1. **Indexes** - On frequently queried fields
2. **Connection Pooling** - Reuse database connections
3. **Query Optimization** - select_related, prefetch_related
4. **Denormalization** - Strategic data duplication (employee_name, project_name)

### Application Optimizations

1. **Caching** - Redis for frequently accessed data
2. **Async Tasks** - Celery for slow operations
3. **Pagination** - Limit result sets
4. **Compression** - Gzip responses
5. **Static Files** - WhiteNoise for serving

### Monitoring

- **Slow Query Logging** - Queries > 50ms
- **Request Timing** - All requests logged
- **Performance Headers** - X-Request-Time, X-Query-Count
- **Health Checks** - /api/health/ endpoints

---

## Scalability Considerations

### Horizontal Scaling

- **Stateless Application** - Can add more Gunicorn workers
- **Shared Cache** - Redis accessible to all instances
- **Shared Database** - PostgreSQL with connection pooling
- **Load Balancer** - Distribute traffic

### Vertical Scaling

- Increase Gunicorn workers
- Increase PostgreSQL resources
- Increase Redis memory

### Current Capacity

- **Users:** 100 concurrent
- **Requests:** ~1000/minute
- **Database:** 1M overtime records
- **Response Time:** <500ms (p95)

---

## Future Enhancements

1. **Microservices** - Split into separate services
2. **GraphQL** - Alternative to REST API
3. **WebSockets** - Real-time notifications
4. **Elasticsearch** - Full-text search
5. **Container Orchestration** - Kubernetes for scaling
6. **CDN** - Content delivery network for static files
7. **Multi-tenancy** - Support multiple organizations

---

**Version:** 2.0
