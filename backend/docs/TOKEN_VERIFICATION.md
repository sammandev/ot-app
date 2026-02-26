# Token Verification API

## Overview

The Token Verification API allows you to verify JWT tokens and determine whether they originated from the local API or an external authentication service. This is useful for systems that support multiple authentication sources and need to differentiate between them.

## Endpoint

**POST** `/auth/token/verify/`

## Authentication

No authentication required (public endpoint)

## Request

### Request Body

```json
{
  "token": "eyJhbGci..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | The JWT token to verify |

### Example Request

```bash
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## Response

### Success Response (200 OK)

The endpoint always returns `200 OK` with details about the token verification.

#### Valid Local Token

```json
{
  "valid": true,
  "source": "local",
  "details": {
    "user_id": 42,
    "username": "john_doe",
    "exp": 1759831574,
    "iat": 1759745114
  }
}
```

#### Valid External Token (In Database)

```json
{
  "valid": true,
  "source": "external",
  "details": {
    "user_id": 123,
    "username": "external_user",
    "exp": 1759831574,
    "iat": 1759745114
  }
}
```

#### Valid External Token (Verified with External API)

```json
{
  "valid": true,
  "source": "external",
  "details": {
    "user_id": 47,
    "exp": 1759831574,
    "iat": 1759745114
  }
}
```

#### Invalid or Expired Token

```json
{
  "valid": false,
  "source": "external",
  "details": {
    "error": "Token is invalid or expired"
  }
}
```

#### Unknown Token

```json
{
  "valid": false,
  "source": "unknown",
  "details": {
    "error": "Verification failed"
  }
}
```

### Error Response (400 Bad Request)

```json
{
  "error": "Token is required"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| valid | boolean | Whether the token is valid and not expired |
| source | string | Token source: `"local"`, `"external"`, or `"unknown"` |
| details | object | Additional information about the token |
| details.user_id | integer | User ID from the token payload |
| details.username | string | Username (only for local tokens or cached external sessions) |
| details.exp | integer | Token expiration timestamp (Unix epoch) |
| details.iat | integer | Token issued at timestamp (Unix epoch) |
| details.error | string | Error message if token is invalid |

## Verification Logic

The endpoint follows this verification flow:

### 1. Local Token Verification

First, the endpoint attempts to validate the token as a local Django JWT token:

- Uses `djangorestframework-simplejwt` to validate the token
- Checks if the user exists in the local database
- If valid, returns `source: "local"`

### 2. External Token Verification (Session Check)

If not a local token, checks the `UserSession` database:

- Looks for an active session with the provided token
- Verifies the token hasn't expired
- If found and valid, returns `source: "external"`
- If expired, deactivates the session and returns `valid: false`

### 3. External Token Verification (External API)

If not found in the session database, verifies with the external API:

- Calls the external API's token verification endpoint: `POST /user/token/verify`
- Decodes the token payload to extract metadata
- If valid, returns `source: "external"`
- If invalid, returns `valid: false`

### 4. Unknown Token

If all verification methods fail:

- Returns `source: "unknown"` and `valid: false`

## External API Integration

The verification process integrates with the external authentication API at `http://172.18.220.56:9001`.

### External Verification Endpoint

**POST** `http://172.18.220.56:9001/user/token/verify`

**Request:**
```json
{
  "token": "your-token-here"
}
```

**Response (Valid Token - 200 OK):**
```json
{}
```

**Response (Invalid Token - 401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

## Use Cases

### 1. Single Sign-On (SSO) Implementation

Check if a cookie token from another application is valid:

```typescript
const token = getCookie('access_token')
const result = await verifyToken(token)

if (result.valid && result.source === 'external') {
  // Auto-login user with external token
  await loginWithExternalToken(token)
}
```

### 2. Multi-Source Authentication

Determine the authentication source for routing or permissions:

```python
def get_user_permissions(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
    verify_result = verify_token(token)
    
    if verify_result['source'] == 'local':
        return get_local_permissions(verify_result['details']['user_id'])
    elif verify_result['source'] == 'external':
        return get_external_permissions(verify_result['details']['user_id'])
```

### 3. Token Debugging

Verify tokens during development or troubleshooting:

```bash
# Check if a token is valid and where it came from
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGci..."}'
```

## Security Considerations

### 1. Public Endpoint
- No authentication required to call this endpoint
- Only returns minimal information (does not expose sensitive user data)
- Safe to call from client-side applications

### 2. Rate Limiting
- Consider implementing rate limiting to prevent abuse
- Recommended: 100 requests per minute per IP

### 3. Token Exposure
- Never log full tokens in production
- Use token prefixes/suffixes for debugging (e.g., `eyJhbGci...last4chars`)

### 4. External API Availability
- External token verification depends on external API availability
- Implements timeout (10 seconds default)
- Falls back gracefully if external API is unavailable

## Error Handling

### External API Timeout

```json
{
  "valid": false,
  "source": "unknown",
  "details": {
    "error": "Token verification service unavailable"
  }
}
```

### Malformed Token

```json
{
  "valid": false,
  "source": "unknown",
  "details": {
    "error": "Verification failed"
  }
}
```

### Network Error

```json
{
  "valid": false,
  "source": "unknown",
  "details": {
    "error": "Token verification service unavailable"
  }
}
```

## Integration Examples

### Frontend (TypeScript/React)

```typescript
import { authAPI } from '@/services/api'

async function checkTokenSource(token: string) {
  try {
    const result = await authAPI.verifyToken(token)
    
    if (result.valid) {
      console.log(`Valid ${result.source} token`)
      console.log('User ID:', result.details?.user_id)
      console.log('Expires:', new Date(result.details?.exp! * 1000))
    } else {
      console.log('Invalid token:', result.details?.error)
    }
    
    return result
  } catch (error) {
    console.error('Token verification failed:', error)
    return null
  }
}
```

### Backend (Python/Django)

```python
from api.services.external_auth import ExternalAuthService
from rest_framework_simplejwt.tokens import AccessToken

def verify_and_classify_token(token_string):
    """Verify token and determine its source"""
    
    # Try local token first
    try:
        validated_token = AccessToken(token_string)
        return {
            'valid': True,
            'source': 'local',
            'user_id': validated_token['user_id']
        }
    except Exception:
        pass
    
    # Try external token
    try:
        is_valid = ExternalAuthService.verify_token(token_string)
        if is_valid:
            payload = ExternalAuthService.decode_token_payload(token_string)
            return {
                'valid': True,
                'source': 'external',
                'user_id': payload.get('user_id')
            }
    except Exception:
        pass
    
    return {'valid': False, 'source': 'unknown'}
```

## Testing

### Manual Testing

```bash
# Test with a local token
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "<local_jwt_token>"}'

# Test with an external token
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "<external_jwt_token>"}'

# Test with invalid token
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "invalid.token.here"}'
```

### Unit Testing (pytest)

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_verify_local_token(local_user, local_token):
    """Test verification of local JWT token"""
    client = APIClient()
    url = reverse('token-verify')
    
    response = client.post(url, {'token': local_token})
    
    assert response.status_code == 200
    assert response.json()['valid'] is True
    assert response.json()['source'] == 'local'

@pytest.mark.django_db  
def test_verify_external_token(external_token):
    """Test verification of external token"""
    client = APIClient()
    url = reverse('token-verify')
    
    response = client.post(url, {'token': external_token})
    
    assert response.status_code == 200
    assert response.json()['valid'] is True
    assert response.json()['source'] == 'external'

def test_verify_invalid_token():
    """Test verification of invalid token"""
    client = APIClient()
    url = reverse('token-verify')
    
    response = client.post(url, {'token': 'invalid.token'})
    
    assert response.status_code == 200
    assert response.json()['valid'] is False
```

## Monitoring and Logging

### Logged Events

The endpoint logs the following events:

- **Info**: Local token verified successfully
- **Warning**: Local token valid but user not found
- **Debug**: Token not recognized as local token
- **Debug**: External token verified from session database
- **Debug**: External token verified with external API
- **Error**: External token verification failed
- **Error**: General token verification errors

### Log Examples

```
INFO: Local user authenticated: john_doe
DEBUG: Not a valid local token: Token is invalid or expired
DEBUG: External token is valid
WARNING: Local token valid but user not found: 999
ERROR: External token verification failed: Token verification service unavailable
```

## Performance Considerations

### Optimization Tips

1. **Caching**: Consider caching verification results for a short period (30-60 seconds)
2. **Session Check First**: Always check the session database before calling external API
3. **Parallel Checks**: Don't run local and external checks in parallel (sequential is faster)
4. **Connection Pooling**: Reuse HTTP connections to external API

### Typical Response Times

- Local token verification: < 10ms
- External token (session DB): < 50ms  
- External token (API call): 100-500ms (depends on external API)

## Configuration

### Environment Variables

```python
# settings.py
EXTERNAL_API_URL = os.getenv('EXTERNAL_API_URL', 'http://172.18.220.56:9001')
EXTERNAL_API_TIMEOUT = int(os.getenv('EXTERNAL_API_TIMEOUT', 10))
```

### Custom Configuration

```python
# Modify timeout
from api.services.external_auth import ExternalAuthService
ExternalAuthService.TIMEOUT = 5  # 5 seconds

# Change external API URL
ExternalAuthService.BASE_URL = 'https://auth.example.com'
```

## Related Endpoints

- [`POST /auth/login/local/`](./AUTHENTICATION.md#local-login) - Login with local credentials
- [`POST /auth/login/external/`](./AUTHENTICATION.md#external-login) - Login with external credentials
- [`POST /auth/token/refresh/`](./AUTHENTICATION.md#token-refresh) - Refresh access token
- [`GET /auth/me/`](./AUTHENTICATION.md#current-user) - Get current user info

## Changelog

### v1.0.0 (2026-01-09)
- Initial implementation
- Support for local and external token verification
- Integration with external API at http://172.18.220.56:9001
- Session database caching for external tokens
