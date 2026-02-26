# Authentication API Documentation

## Overview

The API supports two types of authentication:

1. **Local Authentication** - Uses Django's built-in user authentication with JWT tokens
2. **External Authentication** - Authenticates with an external API and maintains session tracking

Both authentication methods use Bearer tokens in the `Authorization` header.

---

## Authentication Endpoints

### 1. Local Login

**Endpoint:** `POST /api/auth/login/local/`

**Description:** Authenticate with local Django user credentials and receive JWT tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_staff": true,
    "is_superuser": true
  },
  "auth_type": "local"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid username or password"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Username and password are required"
}
```

**Token Lifetime:**
- Access Token: 24 hours
- Refresh Token: 7 days

---

### 2. External Login

**Endpoint:** `POST /api/auth/login/external/`

**Description:** Authenticate with external API credentials (http://172.18.220.56:9001) and create a session.

**Request:**
```json
{
  "username": "Test_123",
  "password": "Test#123"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 1,
    "external_id": 47,
    "username": "Test_123",
    "email": "test123@gmail.com",
    "worker_id": "WORKER001",
    "is_ptb_admin": true,
    "first_name": "",
    "last_name": ""
  },
  "auth_type": "external"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid username or password"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Authentication service error"
}
```

**Token Lifetime:**
- Access Token: 24 hours (from external API)
- Refresh Token: Varies (from external API)

**External API Reference:**
- Base URL: `http://172.18.220.56:9001`
- Token Endpoint: `/api/user/token/`
- User Info Endpoint: `/api/user/account/info`

---

### 3. Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Refresh an access token using a refresh token. Works for both local and external tokens.

**Request:**
```json
{
  "refresh": "eyJhbGci...",
  "auth_type": "local"  // optional: "local" or "external", auto-detected if omitted
}
```

**Success Response (200 OK):**

For local tokens:
```json
{
  "access": "new_access_token...",
  "refresh": "new_refresh_token..."  // included if token rotation is enabled
}
```

For external tokens:
```json
{
  "access": "new_access_token..."
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid or expired refresh token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Refresh token is required"
}
```

**Auto-Detection:**
If `auth_type` is not specified, the system will attempt to detect the token type:
1. First, tries to parse as local JWT token
2. If that fails, assumes it's an external token

---

### 4. Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Logout current user. For external users, deactivates all active sessions. For local users, logs the logout event (client should discard tokens).

**Authorization Required:** Yes (Bearer token)

**Request:** Empty body

**Success Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 5. Get Current User

**Endpoint:** `GET /api/auth/me/`

**Description:** Get information about the currently authenticated user.

**Authorization Required:** Yes (Bearer token)

**Success Response (200 OK) - Local User:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_active": true,
  "is_staff": true,
  "is_superuser": true,
  "auth_type": "local"
}
```

**Success Response (200 OK) - External User:**
```json
{
  "id": 1,
  "external_id": 47,
  "username": "Test_123",
  "email": "test123@gmail.com",
  "first_name": "",
  "last_name": "",
  "worker_id": "WORKER001",
  "is_ptb_admin": true,
  "is_active": true,
  "is_superuser": false,
  "permissions": {
    "perm_all": [...],
    "permissions": [...],
    "user_permissions": [227, 247, 257]
  },
  "groups": [],
  "models_perm": {
    "MODEL_A": {
      "View": true,
      "Modify": true,
      "Site": "ABC"
    }
  },
  "auth_type": "external"
}
```

---

## Using Bearer Tokens

Once you have an access token, include it in the `Authorization` header for all API requests:

```http
GET /api/v1/employees/
Authorization: Bearer eyJhbGci...
```

**Example with cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer eyJhbGci..."
```

**Example with JavaScript (fetch):**
```javascript
fetch('http://localhost:8000/api/v1/employees/', {
  headers: {
    'Authorization': 'Bearer eyJhbGci...',
    'Content-Type': 'application/json'
  }
})
```

**Example with Python (requests):**
```python
import requests

headers = {
    'Authorization': 'Bearer eyJhbGci...',
}

response = requests.get(
    'http://localhost:8000/api/v1/employees/',
    headers=headers
)
```

---

## Authentication Flow

### Local Authentication Flow

```
1. Client sends username/password to POST /api/auth/login/local/
2. Server validates credentials against Django User model
3. Server generates JWT access and refresh tokens
4. Server returns tokens and user info
5. Client stores tokens (localStorage, sessionStorage, or cookies)
6. Client includes access token in Authorization header for API requests
7. When access token expires, client uses refresh token at POST /api/auth/token/refresh/
8. Server returns new access token (and possibly new refresh token)
9. Client logs out by calling POST /api/auth/logout/ and discarding tokens
```

### External Authentication Flow

```
1. Client sends username/password to POST /api/auth/login/external/
2. Server forwards credentials to external API (http://172.18.220.56:9001)
3. External API validates and returns tokens + user data
4. Server creates/updates ExternalUser record in local database
5. Server creates UserSession to track the token
6. Server returns tokens and user info to client
7. Client stores tokens and includes access token in requests
8. Server validates token on each request (checks UserSession)
9. If token expired, server auto-refreshes using refresh token (if available)
10. Client can manually refresh token at POST /api/auth/token/refresh/
11. Client logs out by calling POST /api/auth/logout/
12. Server deactivates all UserSession records for that user
```

---

## Token Validation

The API uses multiple authentication backends (checked in order):

1. **LocalJWTAuthentication** - Validates local JWT tokens using `djangorestframework-simplejwt`
2. **ExternalJWTAuthentication** - Validates external API tokens by checking UserSession

### Token Expiry Handling

**Local Tokens:**
- Access tokens expire after 24 hours
- Refresh tokens expire after 7 days
- Token rotation is enabled (new refresh token issued on refresh)
- Client must use refresh token to get new access token

**External Tokens:**
- Access tokens expire after 24 hours (configured on external API)
- System automatically refreshes expired tokens if refresh token is available
- Session is deactivated if refresh fails
- Client should handle 401 errors and re-login if needed

---

## Error Responses

### 401 Unauthorized
Token is invalid, expired, or missing:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "Given token not valid for any token type"
}
```

### 403 Forbidden
User doesn't have permission:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Security Best Practices

1. **HTTPS Only:** Always use HTTPS in production to protect tokens in transit
2. **Secure Storage:** Store tokens securely:
   - **Web:** Use `httpOnly` cookies or `sessionStorage` (avoid `localStorage` for sensitive apps)
   - **Mobile:** Use secure storage (Keychain/KeyStore)
3. **Token Expiry:** Tokens expire automatically. Handle 401 responses by refreshing or re-authenticating
4. **Logout:** Always call logout endpoint and clear stored tokens
5. **CORS:** Configure CORS properly to prevent unauthorized cross-origin requests
6. **Rate Limiting:** API has rate limiting enabled (configurable via environment variables)

---

## Environment Configuration

Configure authentication in `.env` file:

```bash
# Django secret key for JWT signing (local tokens)
SECRET_KEY=your-secret-key-here

# External API settings
EXTERNAL_API_URL=http://172.18.220.56:9001
EXTERNAL_API_TIMEOUT=10

# JWT Settings (set in settings.py)
# ACCESS_TOKEN_LIFETIME = 24 hours
# REFRESH_TOKEN_LIFETIME = 7 days
# ROTATE_REFRESH_TOKENS = True
```

---

## Testing Authentication

### Test Local Login
```bash
curl -X POST http://localhost:8000/api/auth/login/local/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

### Test External Login
```bash
curl -X POST http://localhost:8000/api/auth/login/external/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "Test_123",
    "password": "Test#123"
  }'
```

### Test Token Refresh
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here",
    "auth_type": "local"
  }'
```

### Test Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer your_access_token_here"
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer your_access_token_here"
```

### Test Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer your_access_token_here"
```

---

## Migration from Old Authentication

Migrate the `/api/auth/login/` endpoint and update to use the new endpoints:

**Old:**
```
POST /api/auth/login/
```

**New:**
```
POST /api/auth/login/external/  (for external API authentication)
POST /api/auth/login/local/     (for local Django authentication)
```

The response format remains the same, with an additional `auth_type` field.

---

## Troubleshooting

### "Authentication credentials were not provided"
- Ensure the `Authorization` header is included
- Check format: `Authorization: Bearer <token>`
- Verify token is not empty or corrupted

### "Given token not valid for any token type"
- Token may be expired - use refresh token to get a new one
- Token may be from wrong environment (dev vs prod)
- For external tokens, check if session was deactivated

### "Authentication service unavailable"
- External API is down or unreachable
- Check `EXTERNAL_API_URL` configuration
- Verify network connectivity to external API

### "Token expired and refresh failed"
- Refresh token is also expired
- User must log in again
- Check token expiry configuration

### Token refresh returns 401
- Refresh token is invalid or expired
- User must log in again with username/password
