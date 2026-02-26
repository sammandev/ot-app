# API Usage Guide - Overtime Management System

**Version:** 2.0  
**Base URL:** `http://your-server:8000/api/v1/`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Resources](#core-resources)
3. [Departments API](#departments-api)
4. [Employees API](#employees-api)
5. [Projects API](#projects-api)
6. [Overtime Requests API](#overtime-requests-api)
7. [Overtime Regulations API](#overtime-regulations-api)
8. [Calendar Events API](#calendar-events-api)
9. [Statistics Endpoints](#statistics-endpoints)
10. [Bulk Operations](#bulk-operations)
11. [Health Checks](#health-checks)
12. [Error Handling](#error-handling)
13. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints require authentication via JWT tokens obtained from the external authentication service.

### Login

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "name": "John Doe",
    "permissions": ["view_overtime", "manage_overtime"]
  }
}
```

### Using the Token

Include the access token in all subsequent requests:

```http
GET /api/v1/employees/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Get Current User

```http
GET /api/auth/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response:**
```json
{
  "id": 1,
  "username": "user@example.com",
  "name": "John Doe",
  "permissions": ["view_overtime", "manage_overtime"]
}
```

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Core Resources

### Pagination

All list endpoints support pagination:

```http
GET /api/v1/employees/?page=1&page_size=25
```

**Response Structure:**
```json
{
  "count": 150,
  "next": "http://api/v1/employees/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 25, max: 100)

### Searching

Most endpoints support search:

```http
GET /api/v1/employees/?search=john
```

### Ordering

Sort results by field:

```http
GET /api/v1/employees/?ordering=-created_at
```

Use `-` prefix for descending order.

### Filtering

Filter by specific fields:

```http
GET /api/v1/overtime-requests/?status=approved&project=5
```

---

## Departments API

### List Departments

```http
GET /api/v1/departments/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "code": "IT",
      "name": "Information Technology",
      "is_enabled": true,
      "created_at": "2026-01-08T10:00:00Z",
      "updated_at": "2026-01-08T10:00:00Z"
    }
  ]
}
```

### Create Department

```http
POST /api/v1/departments/
Content-Type: application/json

{
  "code": "HR",
  "name": "Human Resources",
  "is_enabled": true
}
```

### Get Department

```http
GET /api/v1/departments/1/
```

### Update Department

```http
PATCH /api/v1/departments/1/
Content-Type: application/json

{
  "name": "Information Technology Department"
}
```

### Delete Department

```http
DELETE /api/v1/departments/1/
```

---

## Employees API

### List Employees

```http
GET /api/v1/employees/
```

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "emp_id": "EMP001",
      "name": "John Doe",
      "department": 1,
      "department_id": 1,
      "department_name": "Information Technology",
      "exclude_from_reports": false,
      "created_at": "2025-01-01T08:00:00Z",
      "updated_at": "2025-01-01T08:00:00Z"
    }
  ]
}
```

### Create Employee

```http
POST /api/v1/employees/
Content-Type: application/json

{
  "emp_id": "EMP002",
  "name": "Jane Smith",
  "department": 1,
  "exclude_from_reports": false
}
```

### Update Employee

```http
PATCH /api/v1/employees/1/
Content-Type: application/json

{
  "department": 2,
  "exclude_from_reports": true
}
```

### Bulk Import Employees

```http
POST /api/v1/employees/bulk_import/
Content-Type: multipart/form-data

file: employees.csv
update_existing: true
```

**CSV Format:**
```csv
emp_id,name,department,exclude_from_reports
EMP003,Alice Johnson,1,false
EMP004,Bob Wilson,2,false
```

**Response:**
```json
{
  "created": 2,
  "updated": 0,
  "errors": [],
  "total_rows": 2
}
```

### Export Employees to CSV

```http
GET /api/v1/employees/export/?fields=id,emp_id,name,department.name
```

Returns a CSV file with the specified fields.

---

## Projects API

### List Projects

```http
GET /api/v1/projects/
```

**Response:**
```json
{
  "count": 30,
  "results": [
    {
      "id": 1,
      "name": "Mobile App Development",
      "description": "New mobile application",
      "is_active": true,
      "created_at": "2025-01-01T08:00:00Z"
    }
  ]
}
```

### Create Project

```http
POST /api/v1/projects/
Content-Type: application/json

{
  "name": "Web Portal Upgrade",
  "description": "Upgrade company web portal",
  "is_active": true
}
```

---

## Overtime Requests API

### List Overtime Requests

```http
GET /api/v1/overtime-requests/
```

**Response:**
```json
{
  "count": 500,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "employee_name": "John Doe",
      "project": 1,
      "project_name": "Mobile App Development",
      "ot_date": "2026-01-08",
      "time_in": "18:00:00",
      "time_out": "22:00:00",
      "total_hours": "4.00",
      "work_description": "Bug fixing and testing",
      "status": "approved",
      "approved_by": 5,
      "approved_at": "2026-01-09T09:00:00Z",
      "rejection_reason": null,
      "breaks": [
        {
          "id": 1,
          "start_time": "19:30:00",
          "end_time": "19:45:00",
          "duration_minutes": 15
        }
      ],
      "is_weekend": false,
      "is_holiday": false,
      "created_at": "2026-01-08T14:00:00Z"
    }
  ]
}
```

### Create Overtime Request

```http
POST /api/v1/overtime-requests/
Content-Type: application/json

{
  "employee": 1,
  "project": 1,
  "ot_date": "2026-01-10",
  "time_in": "18:00",
  "time_out": "21:00",
  "work_description": "Feature development",
  "breaks": [
    {
      "start_time": "19:00",
      "end_time": "19:15",
      "duration_minutes": 15
    }
  ]
}
```

### Approve Overtime Request

```http
PATCH /api/v1/overtime-requests/1/
Content-Type: application/json

{
  "status": "approved"
}
```

### Reject Overtime Request

```http
PATCH /api/v1/overtime-requests/1/
Content-Type: application/json

{
  "status": "rejected",
  "rejection_reason": "Insufficient justification"
}
```

### Filter by Status

```http
GET /api/v1/overtime-requests/?status=pending
GET /api/v1/overtime-requests/?status=approved
GET /api/v1/overtime-requests/?status=rejected
```

### Filter by Date Range

```http
GET /api/v1/overtime-requests/?start_date=2026-01-01&end_date=2026-01-31
```

---

## Statistics Endpoints

### Employee Statistics

Get overtime statistics aggregated by employee:

```http
GET /api/v1/overtime-requests/employee-stats/
```

**Optional Parameters:**
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

**Response:**
```json
{
  "results": [
    {
      "employee_id": 1,
      "employee_name": "John Doe",
      "total_hours": "120.00",
      "weekday_hours": "80.00",
      "weekend_hours": "30.00",
      "holiday_hours": "10.00",
      "total_requests": 30,
      "approved_requests": 25,
      "pending_requests": 3,
      "rejected_requests": 2
    }
  ]
}
```

### Project Statistics

Get overtime statistics aggregated by project:

```http
GET /api/v1/overtime-requests/project-stats/?start_date=2026-01-01&end_date=2026-01-31
```

**Response:**
```json
{
  "results": [
    {
      "project_id": 1,
      "project_name": "Mobile App Development",
      "total_hours": "250.00",
      "total_requests": 50,
      "unique_employees": 15
    }
  ]
}
```

### Summary Statistics

Get overall overtime statistics:

```http
GET /api/v1/overtime-requests/summary-stats/?start_date=2026-01-01
```

**Response:**
```json
{
  "total_hours": "5000.00",
  "total_requests": 500,
  "unique_employees": 100,
  "unique_projects": 25,
  "weekday_hours": "3500.00",
  "weekend_hours": "1200.00",
  "holiday_hours": "300.00",
  "approved_requests": 450,
  "pending_requests": 30,
  "rejected_requests": 20
}
```

---

## Overtime Regulations API

### List Regulations

```http
GET /api/v1/overtime-regulations/
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "Maximum Daily Overtime",
      "description": "Employees may work a maximum of 4 hours overtime per day.",
      "category": "limits",
      "order": 1,
      "is_active": true,
      "created_at": "2026-01-09T10:00:00Z"
    }
  ]
}
```

### Create Regulation

```http
POST /api/v1/overtime-regulations/
Content-Type: application/json

{
  "title": "Weekend Approval",
  "description": "Weekend overtime requires manager approval 48 hours in advance.",
  "category": "approval",
  "order": 2,
  "is_active": true
}
```

### Filter by Category

```http
GET /api/v1/overtime-regulations/?category=limits
GET /api/v1/overtime-regulations/?category=approval
GET /api/v1/overtime-regulations/?category=compensation
```

---

## Calendar Events API

### List Events

```http
GET /api/v1/calendar-events/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "Team Meeting",
      "event_type": "meeting",
      "description": "Weekly team sync",
      "start": "2026-01-10T14:00:00Z",
      "end": "2026-01-10T15:00:00Z",
      "all_day": false,
      "location": "Conference Room A",
      "color": "#3498DB",
      "employee": 1,
      "employee_name": "John Doe",
      "project": 1,
      "project_name": "Mobile App Development",
      "meeting_url": "https://meet.example.com/abc123",
      "created_at": "2026-01-08T10:00:00Z"
    }
  ]
}
```

### Create Event

```http
POST /api/v1/calendar-events/
Content-Type: application/json

{
  "title": "Project Deadline",
  "event_type": "deadline",
  "description": "Final delivery date",
  "start": "2026-01-15T00:00:00Z",
  "end": "2026-01-15T23:59:59Z",
  "all_day": true,
  "location": "",
  "color": "#E74C3C",
  "project": 1
}
```

### Create Meeting with Location

```http
POST /api/v1/calendar-events/
Content-Type: application/json

{
  "title": "Client Presentation",
  "event_type": "meeting",
  "start": "2026-01-12T10:00:00Z",
  "end": "2026-01-12T12:00:00Z",
  "all_day": false,
  "location": "Building B, Room 301",
  "color": "#2ECC71",
  "meeting_url": "https://zoom.us/j/123456789",
  "project": 1
}
```

---

## Health Checks

### Basic Health Check

```http
GET /api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "overtime-api",
  "timestamp": 1704801234.567
}
```

### Detailed Health Check

```http
GET /api/health/detailed/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "overtime-api",
  "timestamp": 1704801234.567,
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "cache": {
      "status": "healthy",
      "message": "Cache connection successful"
    },
    "celery": {
      "status": "healthy",
      "message": "2 worker(s) active"
    }
  }
}
```

### Readiness Check

```http
GET /api/health/ready/
```

Returns 200 if all critical services are ready, 503 otherwise.

### Liveness Check

```http
GET /api/health/live/
```

Returns 200 if application is alive.

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Validation error message"]
  }
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Validation Errors

```json
{
  "emp_id": ["This field is required."],
  "name": ["Ensure this field has no more than 100 characters."]
}
```

---

## Rate Limiting

### Default Limits

- **Anonymous users:** 100 requests per day
- **Authenticated users:** 1000 requests per day
- **Export endpoints:** 5 requests per minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1704887400
```

### Rate Limit Exceeded

**Response:**
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

**Status Code:** `429 Too Many Requests`

---

## Examples

### Complete Overtime Workflow

#### 1. Create Overtime Request

```bash
curl -X POST http://api/v1/overtime-requests/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "project": 1,
    "ot_date": "2026-01-10",
    "time_in": "18:00",
    "time_out": "22:00",
    "work_description": "Database optimization"
  }'
```

#### 2. Manager Approves

```bash
curl -X PATCH http://api/v1/overtime-requests/1/ \
  -H "Authorization: Bearer MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

#### 3. Generate Statistics

```bash
curl -X GET "http://api/v1/overtime-requests/employee-stats/?employee=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bulk Employee Import

```bash
curl -X POST http://api/v1/employees/bulk_import/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@employees.csv" \
  -F "update_existing=true"
```

### Export with Custom Fields

```bash
curl -X GET "http://api/v1/employees/export/?fields=emp_id,name,department.name" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -O employees_export.csv
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Cache tokens** - don't request new tokens for every API call
3. **Handle rate limits** - implement exponential backoff
4. **Use pagination** - don't fetch all records at once
5. **Validate data client-side** - reduce unnecessary API calls
6. **Use appropriate HTTP methods** - GET for reading, POST for creating, PATCH for updating
7. **Include error handling** - always handle error responses
8. **Monitor API performance** - use health check endpoints
9. **Use bulk operations** - for importing/exporting large datasets
10. **Respect rate limits** - implement throttling in your client

---

## Support

For API issues or questions:
- **Documentation:** [API Reference](/api/docs/)
- **Swagger UI:** [/api/swagger/](/api/swagger/)
- **ReDoc:** [/api/redoc/](/api/redoc/)

---

**Version:** 2.0
