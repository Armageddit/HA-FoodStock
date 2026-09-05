# FoodStock Backend Specification

## 1\. Backend Role

The FoodStock Backend is the central authority for all application data and business rules.

The backend must remain independent of the FlutterFlow UI.

## 2\. Framework

The backend uses FastAPI.

FastAPI provides:

-   REST API
-   Request validation
-   Response validation
-   OpenAPI documentation
-   Dependency injection
-   Authentication integration
-   Async request handling

## 3\. Data Validation

Pydantic models are used for API input and output validation.

Invalid input must be rejected before business logic is executed.

Examples:

-   Invalid barcode
-   Invalid date
-   Invalid quantity
-   Unknown inventory ID
-   Unauthorized user
-   Invalid storage location

## 4\. Database Access

SQLAlchemy 2 is used as the database abstraction layer.

`asyncpg` is used as the PostgreSQL driver.

Database access must be centralized.

API route handlers should not contain raw SQL business logic.

## 5\. Migrations

Alembic is used for database schema migrations.

Every schema change must be represented by a migration.

Production database changes must never depend on manually editing tables.

Example:

```text
Migration 001
Initial schema

Migration 002
Add audit events

Migration 003
Add product image metadata
```

## 6\. Configuration

Configuration must come from environment variables and/or Home Assistant App configuration.

Secrets must never be hardcoded.

Examples:

```text
DATABASE_URL
JWT_SECRET
STORAGE_ROOT
LOG_LEVEL
```

The actual variable names will be finalized during implementation.

## 7\. Health Checks

The backend must expose:

```text
GET /health
```

The health endpoint should verify application availability.

A separate readiness endpoint should eventually verify dependencies:

```text
GET /ready
```

Readiness should verify that the database is reachable.

## 8\. Error Handling

The API should use consistent error responses.

Example:

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "The requested product does not exist."
  }
}
```

Error messages must not expose:

-   Passwords
-   Database credentials
-   Internal stack traces
-   SQL statements
-   Secrets

## 9\. Logging

Logs should contain:

-   Timestamp
-   Log level
-   Request ID
-   User ID where appropriate
-   Operation
-   Error information

Sensitive values must be excluded.

## 10\. Request IDs

Each API request should have a request identifier.

This makes it possible to correlate:

```text
Mobile App
   |
   | request ID
   v
API
   |
   v
Database
```

with server logs.

## 11\. Transactional Inventory Operations

Inventory changes must be implemented as database transactions.

A consume operation should:

1.  Authenticate the user.
2.  Check authorization.
3.  Select the appropriate active inventory unit.
4.  Lock the relevant database row.
5.  Mark the inventory unit consumed.
6.  Create an audit event.
7.  Recalculate affected shopping-list state.
8.  Commit the transaction.

If any step fails, the transaction must roll back.

## 12\. FEFO

FoodStock uses:

```text
First Expire, First Out
```

as the default consumption strategy.

Sorting:

1.  Active inventory
2.  Earliest expiration date
3.  Stable secondary ordering

The secondary ordering prevents nondeterministic behavior for equal dates.

## 13\. Shopping List Calculation

Shopping-list calculation must be centralized.

Pseudocode:

```text
if current_stock < minimum_stock:

    if ideal_stock is defined:
        quantity = ideal_stock - current_stock
    else:
        quantity = minimum_stock - current_stock

    add_or_update_shopping_item()
```

## 14\. Product Import

Open Food Facts is an external enrichment source.

Imported data is treated as untrusted external data.

The backend must normalize and validate imported fields before presenting them to the user.

The user's locally stored product data remains authoritative after confirmation.

## 15\. File Storage

The backend stores files outside PostgreSQL.

Database records contain references such as:

```text
storage_key
file_name
mime_type
size
checksum
created_at
```

A storage abstraction should be used so that the physical storage implementation can be changed later.

## 16\. Image Security

Uploaded files must be validated.

At minimum:

-   MIME type validation
-   File size limit
-   Extension normalization
-   Generated storage filenames
-   No executable file types
-   No user-controlled filesystem paths

## 17\. API Versioning

The initial API should use:

```text
/api/v1/
```

Example:

```text
/api/v1/products
/api/v1/inventory
/api/v1/shopping-list
```

This allows future breaking API changes without immediately breaking older mobile versions.

## 18\. API Documentation

FastAPI's generated OpenAPI documentation should be used during development.

The API specification should additionally be maintained as a project document so that the API does not depend solely on generated documentation.

## 19\. Backend Testing

Tests should cover:

-   Authentication
-   Authorization
-   Product creation
-   Product lookup
-   Inventory creation
-   FEFO consumption
-   Negative inventory
-   Shopping-list calculation
-   Expiration categories
-   Concurrent consumption
-   Audit events
-   File metadata
-   API validation

Critical business rules require automated tests.
