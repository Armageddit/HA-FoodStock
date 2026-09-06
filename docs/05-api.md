# API

## Overview

The FoodStock API is the communication layer between FoodStock-Mobile and FoodStock-Home.

The backend is authoritative for all persistent application state and business-critical operations.

The current API is an internal household API.

## Base URL

The current implementation does **not** use an `/api/v1` prefix.

Endpoints are therefore exposed directly from the backend root.

Example:

```text
http://<foodstock-host>:8000
```

FastAPI's interactive API documentation is available at:

```text
http://<foodstock-host>:8000/docs
```

The generated OpenAPI specification is available through the FastAPI application.

## Authentication

Authenticated endpoints require a bearer access token.

### Obtain token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
```

Form fields:

```text
username
password
```

Example response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

The client should send the token with subsequent authenticated requests:

```http
Authorization: Bearer <jwt>
```

The current implementation does not provide refresh tokens, logout, or server-side token revocation.

## Current User

```http
GET /auth/me
Authorization: Bearer <token>
```

Returns information about the authenticated user.

## System Endpoints

### Root

```http
GET /
```

Returns application status and version information.

### Health

```http
GET /health
```

Checks application/database availability.

### Database configuration

```http
GET /database-configured
```

Returns non-secret database connection metadata used for diagnostics/setup.

Passwords, secrets, and credentials must never be returned.

## Users

User administration is restricted to administrators.

### List users

```http
GET /users
Authorization: Bearer <admin-token>
```

### Create user

```http
POST /users
Authorization: Bearer <admin-token>
```

### Update user

```http
PATCH /users/{user_id}
Authorization: Bearer <admin-token>
```

Users can be activated/deactivated and their roles can be changed.

An administrator cannot deactivate their own account.

## Storage Locations

### List locations

```http
GET /storage-locations
Authorization: Bearer <token>
```

Returns active storage locations.

### Create location

```http
POST /storage-locations
Authorization: Bearer <admin-token>
```

### Update location

```http
PATCH /storage-locations/{location_id}
Authorization: Bearer <admin-token>
```

Storage locations support hierarchical relationships through `parent_id`.

## Products

### List products

```http
GET /products
Authorization: Bearer <token>
```

By default, only active products are returned.

To include inactive products:

```http
GET /products?include_inactive=true
```

### Get product

```http
GET /products/{product_id}
Authorization: Bearer <token>
```

### Create product

```http
POST /products
Authorization: Bearer <token>
```

Product creation is available to authenticated users.

A barcode must be unique when provided.

### Update product

```http
PATCH /products/{product_id}
Authorization: Bearer <admin-token>
```

Product modification requires administrator privileges.

### Deactivate product

```http
DELETE /products/{product_id}
Authorization: Bearer <admin-token>
```

The current implementation does not physically delete the product.

It sets:

```text
active = false
```

and returns a deactivation result.

### Upload product image

```http
POST /products/{product_id}/image
Authorization: Bearer <admin-token>
Content-Type: multipart/form-data
```

Supported image types:

```text
image/jpeg
image/png
image/webp
```

Maximum upload size:

```text
10 MB
```

The image is stored in the persistent FoodStock filesystem.

## Barcode Lookup

```http
GET /scan/{barcode}
Authorization: Bearer <token>
```

The backend first checks the local product database.

If no local product exists, it queries Open Food Facts.

Possible result flow:

```text
Local product found
    ↓
return local product

Local product not found
    ↓
Open Food Facts lookup
    ↓
return optional suggestion
```

Open Food Facts data is not automatically inserted into the FoodStock database.

The response may contain:

```json
{
  "found": false,
  "source": "openfoodfacts",
  "suggestion": {
    "barcode": "...",
    "name": "...",
    "manufacturer": "...",
    "category": "...",
    "remote_image_url": "..."
  }
}
```

## Inventory

### Add inventory

```http
POST /inventory
Authorization: Bearer <token>
Content-Type: application/json
```

The request can contain:

-   Product ID
-   Quantity
-   Optional expiration date
-   Optional storage location
-   Optional `client_operation_id`

The backend creates an inventory entry.

If no storage location is supplied, the product's default storage location is used when available.

A successful response contains the created inventory ID and current product stock.

### Consume inventory

```http
POST /products/{product_id}/consume
Authorization: Bearer <token>
Content-Type: application/json
```

The request specifies:

-   Quantity
-   Optional reason
-   Optional `client_operation_id`

The client does not select individual inventory entries.

The backend performs FEFO consumption.

### FEFO

Consumption uses:

**FEFO — First Expire, First Out**

The backend consumes active inventory with the earliest known expiration date first.

If the available stock is insufficient, the remaining quantity is represented as missing stock.

### Correct inventory

```http
POST /products/{product_id}/correct
Authorization: Bearer <admin-token>
Content-Type: application/json
```

Inventory correction is an administrator operation.

The request specifies:

-   Quantity delta
-   Reason
-   Optional `client_operation_id`

A zero quantity delta is rejected.

Positive corrections create active stock.

Negative corrections create missing stock.

The correction is recorded as a transaction.

### List inventory

```http
GET /inventory
Authorization: Bearer <token>
```

The current implementation supports status filtering.

The default status filter is active inventory.

### Expiring inventory

```http
GET /expiring?days=14
Authorization: Bearer <token>
```

Returns active inventory entries with an expiration date within the requested number of days.

The accepted range is currently:

```text
0–365 days
```

## Idempotent Inventory Operations

Inventory-changing operations support:

```text
client_operation_id
```

The identifier should be generated by the client for each logical operation.

Example:

```json
{
  "product_id": 42,
  "quantity": 2,
  "client_operation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

If the same operation is submitted again with the same identifier, the backend detects the existing transaction and does not execute the operation twice.

Typical response:

```json
{
  "status": "already_applied"
}
```

For consumption and correction, the response also includes the current stock.

This mechanism is intended to support safe retries and the planned offline-first mobile application.

## Shopping List

### List shopping list

```http
GET /shopping-list
Authorization: Bearer <token>
```

Returns the current shopping-list entries.

The response includes product information such as:

-   Product ID
-   Product name
-   Unit
-   Required quantity
-   Status

### Update shopping-list status

```http
PATCH /shopping-list/{product_id}
Authorization: Bearer <token>
Content-Type: application/json
```

The current implementation identifies a shopping-list entry by product ID.

The status update is associated with the authenticated user.

## Transactions

Transaction history is restricted to administrators.

### List transactions

```http
GET /transactions?limit=100
Authorization: Bearer <admin-token>
```

The current result limit range is:

```text
1–500
```

The transaction response contains the transaction data together with associated product and user information.

The transaction table is currently the authoritative history of inventory mutations.

## Recipe Prompt

```http
GET /ai/prompt
Authorization: Bearer <token>
```

Returns generated recipe-prompt text based on the current inventory.

The endpoint does **not** call an AI provider.

It only generates structured prompt text.

An AI provider can be integrated separately in the future.

## HTTP Status Codes

The API uses standard HTTP status codes.

Common examples include:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
413 Payload Too Large
415 Unsupported Media Type
422 Validation Error
```

The exact response body depends on the endpoint and FastAPI validation behavior.

## Error Format

The current application uses FastAPI's standard error format:

```json
{
  "detail": "..."
}
```

Clients should not use localized error messages as stable machine-readable identifiers.

A future API version may introduce structured application-specific error codes.

## API and Offline Synchronization

The backend is authoritative.

The planned mobile application may maintain a local representation of application data for offline use, but synchronization must ultimately use the FoodStock API.

For state-changing operations:

```text
Mobile
   │
   │ operation + client_operation_id
   ▼
FoodStock API
   │
   ├── validate
   ├── execute
   ├── record transaction
   └── return authoritative state
```

The mobile client should not assume that an operation succeeded solely because it was stored locally.

The backend response determines the authoritative server state.

## Future: Product Groups

The current API does not expose product-group management or product-equivalence matching.

The initial mobile application should work with concrete products and their barcodes.

A future API may provide product-group functionality for use cases such as:

-   Finding equivalent products
-   Aggregating stock across equivalent products
-   Shopping-list recommendations
-   Product substitutions
-   Product similarity

Future API design must preserve the distinction between a concrete product and a product group.

For example:

```text
Concrete products:

ALDI Milk 1.5%
REWE Milk 1.5%
Lidl Milk 1.5%

Product group:

Milk 1.5%
```

The API must not automatically replace one concrete product with another merely because both belong to the same product group.

Automatic product matching is a future feature and is not part of the current API contract.

## API Stability

The current API is an internal household API and does not currently use URL-based API versioning.

Before FoodStock-Mobile becomes dependent on the API, request and response models should be treated as a formal client contract.

Breaking changes should be handled deliberately.

Possible future strategies include:

-   Backward-compatible changes
-   Explicit API versioning
-   Migration periods
-   Versioned OpenAPI contracts

The current implementation should not be described as `/api/v1` until such a prefix actually exists in the backend.

## OpenAPI

FastAPI automatically exposes the implemented API through OpenAPI.

The interactive documentation is available at:

```text
/docs
```

This generated specification should be treated as the most direct representation of the currently implemented endpoint surface.

When the mobile application is developed, the API documentation and generated OpenAPI schema should be kept synchronized with the backend implementation.  
:::{"fallbackMarkdown":"","reference":{"matched\_text":" ","prefix":null,"start\_idx":30033,"end\_idx":30033,"safe\_urls":\[\],"refs":\[\],"alt":"","prompt\_text":null,"type":"sources\_footnote","sources":\[{"title":"HA-FoodStock/docs/03-backend.md at docs · Armageddit/HA-FoodStock · GitHub","url":"https://github.com/Armageddit/HA-FoodStock/blob/docs/docs/03-backend.md","attribution":"GitHub"}\],"has\_images":false},"showLoginRequiredCard":false}
