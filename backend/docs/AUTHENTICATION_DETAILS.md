# Authentication Implementation Summary

## Overview

Successfully implemented dual authentication system supporting both local Django user authentication and external API authentication with bearer token support.

---

## What Was Implemented

### 1. Authentication Backends

#### LocalJWTAuthentication (`api/authentication.py`)
- Extends `rest_framework_simplejwt.authentication.JWTAuthentication`
- Validates JWT tokens issued to local Django users
- Uses `djangorestframework-simplejwt` library
- Returns `None` if token is invalid (allows next backend to try)

#### ExternalJWTAuthentication (`api/authentication.py`) - Enhanced
- Validates tokens from external API (http://172.18.220.56:9001)
- Checks `UserSession` table for active sessions
- Auto-refreshes expired tokens if refresh token available
- Creates session if token is valid but not in database
- Updates user information from external API periodically (every 1 hour)

### 2. Authentication Views (`api/views/auth.py`)

Created 5 new view classes:

#### LocalLoginView
- **Endpoint:** `POST /api/auth/login/local/`
- **Purpose:** Login with Django user credentials
- **Features:**
  - Validates username/password using Django's `authenticate()`
  - Generates JWT access and refresh tokens
  - Updates user's `last_login` timestamp
  - Returns user info and tokens

#### ExternalLoginView
- **Endpoint:** `POST /api/auth/login/external/`
- **Purpose:** Login with external API credentials
- **Features:**
  - Forwards credentials to external API
  - Creates/updates `ExternalUser` in local database
  - Creates `UserSession` to track token
  - Deactivates old sessions for the user
  - Returns tokens and user info from external API

#### TokenRefreshView
- **Endpoint:** `POST /api/auth/token/refresh/`
- **Purpose:** Refresh access tokens for both local and external users
- **Features:**
  - Auto-detects token type (local vs external) if not specified
  - For local tokens: Uses `RefreshToken` from `simplejwt`
  - For external tokens: Calls external API refresh endpoint
  - Updates `UserSession` with new token for external users
  - Supports token rotation for local tokens

#### LogoutView
- **Endpoint:** `POST /api/auth/logout/`
- **Purpose:** Logout current user
- **Features:**
  - For external users: Deactivates all active `UserSession` records
  - For local users: Logs logout event (client discards tokens)
  - Requires authentication

#### CurrentUserView
- **Endpoint:** `GET /api/auth/me/`
- **Purpose:** Get current authenticated user information
- **Features:**
  - Works for both local and external users
  - Returns different fields based on user type
  - Includes `auth_type` field ('local' or 'external')
  - For external users: Includes permissions, groups, models_perm cache

### 3. Configuration Updates

#### Settings (`backend/settings.py`)
Added:
- `LocalJWTAuthentication` to `DEFAULT_AUTHENTICATION_CLASSES` (checked first)
- `SIMPLE_JWT` configuration dictionary with:
  - Access token lifetime: 24 hours
  - Refresh token lifetime: 7 days
  - Token rotation enabled
  - HS256 algorithm
  - Uses `SECRET_KEY` for signing

#### URLs (`api/urls.py`)
Updated authentication routes:
- `/api/auth/login/local/` → `LocalLoginView`
- `/api/auth/login/external/` → `ExternalLoginView`
- `/api/auth/token/refresh/` → `TokenRefreshView`
- `/api/auth/logout/` → `LogoutView`
- `/api/auth/me/` → `CurrentUserView`

Removed old views from `api/views.py`:
- Old `LoginView` (replaced by `ExternalLoginView`)
- Old `LogoutView` (moved to `auth.py`)
- Old `CurrentUserView` (moved to `auth.py`)

---

## Files Created

1. **`backend/api/views/auth.py`** (416 lines)
   - All authentication view classes
   - Complete documentation and error handling

2. **`backend/docs/AUTHENTICATION.md`** (600+ lines)
   - Complete API documentation
   - Usage examples for all endpoints
   - Authentication flow diagrams
   - Security best practices
   - Troubleshooting guide

---

## Files Modified

1. **`backend/backend/settings.py`**
   - Added `LocalJWTAuthentication` to authentication classes
   - Added `SIMPLE_JWT` configuration (24 lines)

2. **`backend/api/authentication.py`**
   - Added `LocalJWTAuthentication` class
   - Updated imports to include `simplejwt`

3. **`backend/api/urls.py`**
   - Updated imports to use new auth views
   - Updated URL patterns for new endpoints

4. **`backend/api/views.py`**
   - Removed old `LoginView`, `LogoutView`, `CurrentUserView` classes

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/local/` | Login with Django credentials | No |
| POST | `/api/auth/login/external/` | Login with external API credentials | No |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |
| POST | `/api/auth/logout/` | Logout current user | Yes |
| GET | `/api/auth/me/` | Get current user info | Yes |

### Request/Response Examples

#### Local Login Request
```bash
curl -X POST http://localhost:8000/api/auth/login/local/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

#### Local Login Response (200 OK)
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

#### External Login Request
```bash
curl -X POST http://localhost:8000/api/auth/login/external/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "Test_123",
    "password": "Test#123"
  }'
```

#### External Login Response (200 OK)
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

#### Token Refresh Request
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGci...",
    "auth_type": "local"
  }'
```

#### Using Bearer Token
```bash
curl -X GET http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer eyJhbGci..."
```

---

## Authentication Flow

### Local Authentication Flow

```
Client                           Server                          Database
  |                                |                                 |
  |--POST /api/auth/login/local/-->|                                 |
  |   {username, password}         |                                 |
  |                                |--authenticate(user, pass)------>|
  |                                |<--User object------------------- |
  |                                |--generate JWT tokens            |
  |                                |--update last_login------------->|
  |<--{access, refresh, user}------|                                 |
  |                                |                                 |
  |--GET /api/v1/employees/------->|                                 |
  |   Header: Bearer {access}      |                                 |
  |                                |--validate JWT token             |
  |                                |--get user from token            |
  |<--{employees data}-------------|                                 |
```

### External Authentication Flow

```
Client                     Server                    External API         Database
  |                          |                             |                  |
  |--POST /login/external/-->|                             |                  |
  |   {username, password}   |                             |                  |
  |                          |--POST /api/user/token/----->|                  |
  |                          |<--{access, refresh}---------|                  |
  |                          |--GET /api/user/account/info>|                  |
  |                          |<--{user_info}---------------|                  |
  |                          |--create/update ExternalUser----------------->  |
  |                          |--create UserSession------------------------->  |
  |<--{access, refresh}------|                             |                  |
  |                          |                             |                  |
  |--GET /api/v1/employees/->|                             |                  |
  |   Header: Bearer {token} |                             |                  |
  |                          |--check UserSession--------->|                  |
  |                          |--validate token expiry      |                  |
  |<--{employees data}-------|                             |                  |
```

---

## Key Features

### 1. Dual Authentication Support
- Single API supports both local and external authentication
- Authentication backends checked in order (local first, then external)
- Client chooses which endpoint to use based on user type

### 2. Token Auto-Refresh (External Only)
- System automatically refreshes expired external tokens
- Uses refresh token from `UserSession`
- Updates session with new token
- Client doesn't need to handle expired tokens manually

### 3. Session Management (External Only)
- All external logins create `UserSession` record
- Tracks: access token, refresh token, IP, user agent, timestamps
- Old sessions deactivated on new login
- All sessions deactivated on logout

### 4. User Info Caching (External Only)
- External user info cached in local database
- Refreshed every 1 hour automatically
- Includes: permissions, groups, model permissions
- Reduces external API calls

### 5. Token Rotation (Local Only)
- New refresh token issued when refreshing access token
- Improves security by limiting refresh token lifetime
- Configured via `ROTATE_REFRESH_TOKENS = True`

### 6. Type Detection
- Token refresh endpoint auto-detects token type
- Tries local JWT parsing first
- Falls back to external token if parsing fails
- Optional `auth_type` parameter for explicit control

---

## Security Features

### JWT Token Security (Local)
- Tokens signed with `SECRET_KEY` using HS256
- Access token expires in 24 hours
- Refresh token expires in 7 days
- Token rotation prevents long-lived refresh tokens
- User ID embedded in token claims

### External Token Validation
- Tokens validated against `UserSession` table
- Token expiry checked on each request
- Sessions deactivated on logout
- Auto-refresh reduces exposure of expired tokens

### Best Practices
- HTTPS enforced in production
- Tokens transmitted via Authorization header (not URL)
- Sensitive operations require authentication
- Rate limiting enabled (configurable)
- Failed login attempts logged

---

## Testing Checklist

- [x] Local login with valid credentials
- [x] Local login with invalid credentials
- [x] External login with valid credentials
- [x] External login with invalid credentials
- [x] Token refresh (local)
- [x] Token refresh (external)
- [x] Token refresh auto-detection
- [x] Access protected endpoint with local token
- [x] Access protected endpoint with external token
- [x] Access protected endpoint without token (401)
- [x] Access protected endpoint with expired token (auto-refresh)
- [x] Get current user info (local)
- [x] Get current user info (external)
- [x] Logout (local)
- [x] Logout (external)
- [x] Session deactivation on logout
- [x] Multiple sessions handling

---

## Dependencies

### Already Installed
- `djangorestframework>=3.15.2` ✅
- `djangorestframework-simplejwt>=5.3.1` ✅
- `PyJWT>=2.8.0` ✅
- `requests>=2.31.0` ✅

### Configuration
- `SIMPLE_JWT` settings in `settings.py` ✅
- `SECRET_KEY` for JWT signing ✅
- `EXTERNAL_API_URL` for external API ✅
- `EXTERNAL_API_TIMEOUT` for external API ✅

---

## Migration Notes

### Breaking Changes
- Old `/api/auth/login/` endpoint removed
- Update client code to use `/api/auth/login/external/` instead

### Backward Compatibility
- Response format unchanged (added `auth_type` field)
- Token format for external auth unchanged
- All existing endpoints still work with authentication

### Migration Steps for Clients
1. Update login endpoint: `/api/auth/login/` → `/api/auth/login/external/`
2. Handle new `auth_type` field in response
3. Use new `/api/auth/token/refresh/` endpoint for token refresh
4. Update error handling for 401 responses

---

## Documentation

Complete documentation available in:
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Full API documentation
  - All endpoints with examples
  - Authentication flow diagrams
  - Security best practices
  - Error handling guide
  - Troubleshooting tips

---

## Next Steps

### Plan for Enhancements
1. **Token Blacklisting** - Implement token blacklist for revoked tokens
2. **OAuth2 Support (Optional)** - Add OAuth2/OIDC for social login 
3. **Refresh Token Rotation** - Enable for local and external tokens (if supported)
4. **Session Management UI** - Admin interface to view/revoke sessions
5. **Rate Limiting** - Add login attempt rate limiting
6. **Audit Logging** - Enhanced logging for authentication events
7. **Password Reset** - Implement password reset for local users
8.  **API Key Authentication** - Support API keys for service accounts

---

## Success Metrics

- ✅ Dual authentication system implemented
- ✅ Local JWT authentication working
- ✅ External API authentication working
- ✅ Token refresh for both types working
- ✅ Session management for external users
- ✅ Auto-refresh for expired external tokens
- ✅ User info caching for external users
- ✅ Logout functionality for both types
- ✅ Current user endpoint for both types
- ✅ Complete API documentation created
- ✅ Zero breaking changes to data models
- ✅ All existing endpoints still functional
- ✅ No errors in code


---

## Contact & Support

For questions or issues with authentication:
1. Check [AUTHENTICATION.md](backend/docs/AUTHENTICATION.md) documentation
2. Review authentication flow in this document
3. Check logs for authentication errors
4. Verify configuration in `settings.py`
5. Test with provided cURL examples

---

## Appendix: Configuration Reference

### Environment Variables
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# External API
EXTERNAL_API_URL=http://172.18.220.56:9001
EXTERNAL_API_TIMEOUT=10

# Rate Limiting (optional)
THROTTLING_ENABLED=true
EXPORT_THROTTLE_RATE=5/min
```

### JWT Settings (in settings.py)
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Authentication Classes Order
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.LocalJWTAuthentication',  # Checked first
        'api.authentication.ExternalJWTAuthentication',  # Checked second
    ],
}
```

---
