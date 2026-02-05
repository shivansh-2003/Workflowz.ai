# Core

Core configuration, security, and exception handling modules.

## Overview

This directory contains the foundational modules that provide core functionality for the FastAPI application, including configuration management, security utilities (password hashing, JWT), and custom exception classes.

## Files

### `config.py`
Application configuration and settings management using Pydantic.

**Classes:**
- `Settings` - Application settings loaded from environment variables

**Configuration Values:**
- `APP_NAME` - Application name (default: "Workflowz.ai")
- `API_V1_PREFIX` - API route prefix (default: "/api")
- `DATABASE_URL` - PostgreSQL database connection URL (required)
- `SECRET_KEY` - JWT signing secret key (required)
- `ALGORITHM` - JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 10080 = 7 days)

**Usage:**
```python
from app.core.config import settings

db_url = settings.DATABASE_URL
secret_key = settings.SECRET_KEY
```

**Environment Variables:**
Settings are loaded from `.env` file or environment variables. See `.env.example` for required variables.

### `security.py`
Security utilities for password hashing and JWT token management.

**Functions:**
- `get_password_hash(password)` - Hash password using bcrypt
- `verify_password(plain_password, hashed_password)` - Verify password against hash
- `create_access_token(data)` - Create JWT access token

**Features:**
- Bcrypt password hashing with fallback handling
- Password length validation (72 byte limit)
- JWT token creation with expiration
- Robust error handling for password operations

**Usage:**
```python
from app.core.security import get_password_hash, verify_password, create_access_token

# Hash password
hashed = get_password_hash("user_password")

# Verify password
is_valid = verify_password("user_password", hashed)

# Create JWT token
token = create_access_token({"sub": "user@example.com", "role": "member"})
```

**Password Hashing:**
- Uses `passlib` with bcrypt backend
- Handles bcrypt's 72-byte password limit
- Includes fallback for edge cases

**JWT Tokens:**
- Tokens include expiration time (`exp` claim)
- Signed with `SECRET_KEY` from settings
- Algorithm configurable via settings

### `exceptions.py`
Custom exception classes for consistent error handling.

**Classes:**
- Custom HTTP exceptions for common error scenarios

**Usage:**
```python
from app.core.exceptions import not_found, bad_request

raise not_found("Resource not found")
raise bad_request("Invalid input")
```

**Purpose:**
Provides consistent error responses across the API.

## Design Principles

### Configuration
- **Environment-based**: All settings loaded from environment variables
- **Type-safe**: Uses Pydantic for validation
- **Default values**: Sensible defaults where appropriate
- **Required fields**: Clear indication of required configuration

### Security
- **Password hashing**: Secure bcrypt hashing with salt
- **JWT tokens**: Industry-standard token-based authentication
- **Error handling**: Robust handling of edge cases
- **Validation**: Input validation for security-critical operations

### Error Handling
- **Consistent**: Standardized exception classes
- **Informative**: Clear error messages
- **HTTP-compliant**: Proper HTTP status codes

## Dependencies

Core modules depend on:
- `pydantic` - Settings validation
- `passlib[bcrypt]` - Password hashing
- `python-jose` - JWT token handling
- `python-dotenv` - Environment variable loading

## Usage in Application

### Settings
Settings are used throughout the application:
```python
from app.core.config import settings

# In database connection
database_url = settings.DATABASE_URL

# In security operations
secret_key = settings.SECRET_KEY
```

### Security
Security functions are used in:
- User registration (password hashing)
- User login (password verification)
- Token generation (JWT creation)
- Authentication dependencies (token verification)

### Exceptions
Custom exceptions are used in:
- Router endpoints for error responses
- CRUD operations for not found scenarios
- Validation errors

## Best Practices

1. **Never commit secrets**: Keep `.env` files out of version control
2. **Use strong secrets**: Generate strong `SECRET_KEY` values
3. **Validate inputs**: Always validate password length and format
4. **Handle errors**: Use custom exceptions for consistent error responses
5. **Document settings**: Keep `.env.example` up to date

## Security Considerations

- **Password storage**: Passwords are never stored in plain text
- **Token expiration**: Tokens expire after configured time
- **Secret key**: Must be kept secure and never exposed
- **Password limits**: Enforced 72-byte limit for bcrypt compatibility
