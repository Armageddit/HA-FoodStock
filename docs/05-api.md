# FoodStock REST API

## 1\. API Base Path

All application endpoints use:

```text
/api/v1/
```

## 2\. Authentication

Authenticated endpoints require an access token.

Example:

```http
Authorization: Bearer <access-token>
```

Tokens must never be hardcoded into the application.

## 3\. System

### Health

```http
GET /api/v1/health
```

Purpose:

-   Verify backend availability

### Readiness

```http
GET /api/v1/ready
```

Purpose:

-   Verify backend and database readiness

## 4\. Authentication

```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

## 5\. Products

```http
GET    /api/v1/products
GET    /api/v1/products/{product_id}
POST   /api/v1/products
PATCH  /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}
```

Deleting a product should normally deactivate it rather than physically deleting historical data.

## 6\. Barcode

```http
POST /api/v1/barcodes/lookup
```

Request:

```json
{
  "barcode": "4001234567890"
}
```

The endpoint searches the local database.

A separate endpoint may perform external enrichment:

```http
POST /api/v1/products/enrich
```

## 7\. Storage Locations

```http
GET    /api/v1/storage-locations
POST   /api/v1/storage-locations
GET    /api/v1/storage-locations/{id}
PATCH  /api/v1/storage-locations/{id}
DELETE /api/v1/storage-locations/{id}
```

## 8\. Inventory

```http
GET  /api/v1/inventory
GET  /api/v1/inventory/{id}
POST /api/v1/inventory
```

## 9\. Inventory Consumption

Consumption should be an operation rather than a client-side quantity replacement.

```http
POST /api/v1/inventory/consume
```

Example:

```json
{
  "product_id": "product-id",
  "quantity": 1
}
```

The server selects the appropriate inventory unit according to FEFO.

## 10\. Inventory Correction

Administrator-only:

```http
POST /api/v1/inventory/corrections
```

Example:

```json
{
  "product_id": "product-id",
  "quantity": 2,
  "reason": "Physical stock count"
}
```

## 11\. Expiring Inventory

```http
GET /api/v1/inventory/expiring
```

Optional parameters:

```text
days=14
```

## 12\. Shopping List

```http
GET   /api/v1/shopping-list
POST  /api/v1/shopping-list/items
PATCH /api/v1/shopping-list/items/{id}
DELETE /api/v1/shopping-list/items/{id}
```

## 13\. Shopping List Completion

```http
POST /api/v1/shopping-list/items/{id}/purchase
POST /api/v1/shopping-list/items/{id}/add-to-inventory
```

## 14\. Users

Administrator-only:

```http
GET    /api/v1/users
GET    /api/v1/users/{id}
POST   /api/v1/users
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

## 15\. Audit

Administrator-only:

```http
GET /api/v1/audit-events
GET /api/v1/audit-events/{id}
```

Filtering should support:

```text
user
entity
entity_id
event_type
date_from
date_to
```

## 16\. Files

```http
POST   /api/v1/files
GET    /api/v1/files/{id}
DELETE /api/v1/files/{id}
```

File access must be authenticated and authorized.

## 17\. API Response Model

Successful responses should use consistent structures.

Errors should use:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid."
  }
}
```

## 18\. Idempotency

Operations that may be retried by the offline synchronization layer should support idempotency.

For example:

```http
Idempotency-Key: 7f8f0a...
```

This prevents a network retry from accidentally consuming the same inventory item twice.

## 19\. Synchronization

The mobile client should eventually use:

```http
GET /api/v1/sync
POST /api/v1/sync/operations
```

The synchronization protocol will be specified before offline mode is implemented.

## 20\. API Rule

The mobile application must never implement server-authoritative inventory calculations itself.

The server is authoritative.
