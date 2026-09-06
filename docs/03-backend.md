# Backend

## Technology

The current backend uses:

-   Python
-   FastAPI
-   SQLAlchemy 2
-   PostgreSQL
-   `psycopg`
-   Pydantic
-   JWT authentication
-   HTTPX for Open Food Facts requests

The database layer is currently synchronous.

The implementation does not use `asyncpg`.

## Database Access

Only the FoodStock backend communicates directly with PostgreSQL.

The mobile application must never connect to PostgreSQL.

## Authentication

Authentication uses:

```text
POST /auth/token
```

The endpoint follows the OAuth2 password form convention used by FastAPI.

The response contains a JWT access token.

The token contains:

-   user ID
-   role
-   expiration time

The token is signed using the configured JWT secret.

The current implementation does not provide:

-   refresh tokens
-   logout
-   token revocation

Inactive users cannot authenticate successfully.

## Authorization

Authorization is enforced server-side.

The two roles are:

```text
user
admin
```

Administrator-only operations must never rely on client-side visibility or UI restrictions.

## Passwords

Passwords are stored as password hashes.

Plain-text passwords must never be stored in the database or returned by the API.

## Health

Current system endpoints include:

```text
GET /
GET /health
GET /database-configured
```

`/health` performs a database connectivity check.

A separate `/ready` endpoint is not currently implemented.

## Error Handling

The current backend uses FastAPI `HTTPException` responses.

The error contract is therefore currently based on FastAPI's standard `detail` response.

A structured application-specific error code model is a future improvement.

Clients must not depend on localized error text as a stable machine-readable identifier.

## Logging

Operational logs must not contain:

-   passwords
-   password hashes
-   JWT secrets
-   access tokens
-   database credentials

Future observability improvements may add request IDs and structured logging.

## Database Migrations

The current repository does not contain an Alembic migration system.

SQLAlchemy models define the current schema.

Alembic must therefore not be described as an implemented dependency until migration infrastructure has actually been added.

Before production-style upgrades are required, a proper migration strategy should be introduced.
