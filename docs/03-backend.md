# Backend

## Overview

FoodStock-Home provides the server-side application for the FoodStock system.

The backend is responsible for:

-   Authentication and authorization
-   Product management
-   Storage-location management
-   Inventory management
-   FEFO stock consumption
-   Negative-stock handling
-   Shopping-list calculation and status management
-   Inventory transaction history
-   Product image storage
-   Barcode lookup
-   Recipe-prompt generation
-   PostgreSQL access

The backend is authoritative for all business-critical inventory operations.

The mobile application must not implement conflicting server-side business rules or access PostgreSQL directly.

## Technology

The current backend uses:

-   Python
-   FastAPI
-   SQLAlchemy 2
-   PostgreSQL
-   `psycopg`
-   Pydantic
-   JWT authentication
-   `scrypt` password hashing
-   HTTPX for Open Food Facts requests

The database layer currently uses synchronous SQLAlchemy sessions.

The current implementation does **not** use `asyncpg`.

Some HTTP endpoints are asynchronous where they perform asynchronous external I/O, such as the Open Food Facts lookup and product-image upload.

## Application Structure

The current backend is organized around the following responsibilities:

```text
FoodStock-Home
│
├── FastAPI application
│
├── Authentication
│   ├── JWT access tokens
│   └── role-based authorization
│
├── Product management
│
├── Inventory management
│   ├── intake
│   ├── FEFO consumption
│   └── corrections
│
├── Shopping list
│
├── Transaction history
│
├── External product lookup
│   └── Open Food Facts
│
├── Recipe prompt generation
│
└── PostgreSQL
```

The backend is intentionally kept as the single authority for persistent application state.

## Database Access

Only FoodStock-Home communicates directly with PostgreSQL.

FoodStock-Mobile communicates with the backend through HTTP.

The mobile application must never:

-   connect directly to PostgreSQL
-   contain database credentials
-   modify database records outside the API
-   bypass server-side inventory rules

This separation ensures that all clients use the same validation and business logic.

## Authentication

Authentication is currently implemented using JWT bearer access tokens.

### Login

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
```

The endpoint follows the OAuth2 password-form convention used by FastAPI.

The request contains:

```text
username
password
```

A successful response contains:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

The JWT contains the authenticated user's identity, role, and expiration information.

### Current user

```http
GET /auth/me
Authorization: Bearer <token>
```

The endpoint returns information about the authenticated user.

### Current limitations

The current implementation does not provide:

-   refresh tokens
-   server-side logout
-   token revocation
-   token deny-listing

These are future improvements if the application's security requirements make them necessary.

For the intended private household deployment, access is additionally protected by the surrounding network architecture.

## Authorization

Authorization is enforced server-side.

The current roles are:

```text
user
admin
```

The client UI must not be treated as a security boundary.

Administrator-only operations are protected by backend authorization.

Examples include:

-   User administration
-   Storage-location creation and modification
-   Product modification
-   Product deactivation
-   Product-image upload
-   Inventory correction
-   Transaction-history access

## Password Handling

Passwords are never stored in plain text.

The database stores password hashes only.

Password hashes and passwords must never be returned through the API or written to operational logs.

The current implementation uses `scrypt` for password hashing.

## Inventory Business Logic

Inventory mutations are performed by the backend.

### Intake

Inventory can be added through:

```http
POST /inventory
```

The backend creates an inventory record and updates the associated shopping-list state.

The storage location can be supplied by the client. If it is omitted, the product's default storage location is used when configured.

### Consumption

Consumption is performed through:

```http
POST /products/{product_id}/consume
```

The client specifies the quantity to consume.

The client does **not** select individual inventory records.

The backend determines which inventory records are consumed.

### FEFO

FoodStock uses:

**FEFO — First Expire, First Out**

Active inventory is ordered primarily by expiration date and secondarily by the time the inventory was added.

This ensures that stock with the earliest known expiration date is consumed first.

Inventory without an expiration date is handled after inventory with a known expiration date.

The selected rows are locked during the operation to prevent conflicting concurrent inventory consumption.

### Negative stock

FoodStock explicitly supports consumption beyond the currently available active stock.

If the requested quantity exceeds available stock, the missing quantity is represented as an inventory entry with status:

```text
missing
```

This preserves the distinction between:

-   available stock
-   consumed stock
-   confirmed missing stock

The corresponding transaction is recorded as well.

## Inventory Corrections

Administrators can correct inventory through:

```http
POST /products/{product_id}/correct
```

A correction must have a non-zero quantity delta.

Positive corrections add active inventory.

Negative corrections are represented as missing inventory.

Corrections are recorded in the transaction history.

## Idempotency

Inventory-changing operations support a client-generated operation identifier:

```text
client_operation_id
```

The identifier is persisted with the corresponding transaction and is protected by a unique database constraint.

This provides server-side idempotency for supported inventory commands.

The intended flow is:

```text
Mobile client
    │
    │ operation + client_operation_id
    ▼
FoodStock-Home
    │
    ├── operation not known
    │       → execute
    │       → record operation
    │
    └── operation already known
            → do not execute twice
```

This is particularly important for the planned offline-first mobile application, where requests may be retried after network interruptions.

## Shopping List

The backend automatically evaluates shopping-list requirements after relevant inventory changes.

The current shopping-list model contains at most one entry per product.

Shopping-list status changes are handled by:

```http
PATCH /shopping-list/{product_id}
```

The server remains responsible for determining and maintaining shopping-list state.

## Product Management

Products contain persistent product information such as:

-   Name
-   Barcode
-   Manufacturer
-   Category
-   Unit
-   Default storage location
-   Minimum stock
-   Ideal stock
-   Active state
-   Product image path

Product deactivation is preferred over physical deletion.

This preserves references from existing inventory and transaction records.

## Barcode Lookup

The backend provides:

```http
GET /scan/{barcode}
```

The lookup follows this order:

```text
Barcode
   │
   ▼
Local product database
   │
   ├── found → return local product
   │
   └── not found
          │
          ▼
    Open Food Facts
          │
          ▼
    optional suggestion
```

Open Food Facts data is not automatically persisted as a new product.

The client or user must explicitly create the product.

The external request has a short timeout so that an unavailable external service does not unnecessarily block the application.

## Product Images

Product images are stored on the FoodStock persistent filesystem.

The current implementation accepts:

-   JPEG
-   PNG
-   WebP

The current maximum upload size is 10 MB.

PostgreSQL stores the relative image path rather than the binary image content.

The current implementation does not provide a generalized file-object abstraction.

## Recipe Prompt Generation

The backend provides:

```http
GET /ai/prompt
```

The endpoint generates structured recipe-prompt text based on current inventory.

It does not directly call an AI provider.

An external AI provider can be integrated by a future client or service layer without making the inventory database directly accessible to the provider.

## Health and Diagnostics

The current system exposes:

```http
GET /
GET /health
GET /database-configured
```

`/health` performs a database connectivity check.

`/database-configured` exposes non-secret database connection metadata used for diagnostics/setup.

Secrets and database passwords must never be returned.

A dedicated readiness endpoint such as `/ready` is not currently implemented.

## Error Handling

The backend currently uses FastAPI's `HTTPException`.

Error responses therefore follow the standard FastAPI structure:

```json
{
  "detail": "..."
}
```

Localized human-readable error text must not be used as a stable machine-readable identifier.

A structured application-specific error-code system can be introduced in the future.

## Logging

Operational logs must never contain:

-   Plain-text passwords
-   Password hashes
-   JWT secrets
-   Access tokens
-   Database passwords
-   Other application secrets

Future observability improvements may introduce:

-   Structured logging
-   Request IDs
-   Correlation IDs
-   More explicit audit logging

## Database Initialization and Migrations

The current repository does not contain an Alembic migration system.

The SQLAlchemy models define the current database schema.

The current application initializes the schema through SQLAlchemy metadata rather than through versioned migrations.

Therefore:

**Alembic must not currently be described as an implemented backend dependency.**

Before frequent schema-changing releases or production-style upgrade paths are introduced, a proper migration strategy should be added.

At that point, schema changes should be represented as explicit, versioned migrations.

## API Versioning

The current API does not use an `/api/v1` prefix.

Current endpoints are therefore exposed directly under paths such as:

```text
/auth/token
/products
/inventory
/shopping-list
```

Before the mobile application becomes dependent on a stable public contract, API compatibility should be treated explicitly.

Breaking changes should either:

-   be avoided
-   be migrated deliberately
-   or be introduced through a documented versioning strategy

The current FastAPI OpenAPI document at `/docs` is the most direct representation of the implemented endpoint surface.
