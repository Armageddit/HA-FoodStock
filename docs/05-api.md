# API

## Base URL

The API is currently served by the FoodStock backend.

The current implementation does not use an `/api/v1` prefix.

Interactive API documentation is available through FastAPI at:

```text
/docs
```

## Authentication

### Obtain access token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
```

Form fields:

```text
username
password
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Current user

```http
GET /auth/me
Authorization: Bearer <token>
```

## System

### Root

```http
GET /
```

Returns application status and version.

### Health

```http
GET /health
```

Checks application and database availability.

### Database configuration

```http
GET /database-configured
```

Returns non-secret database connection metadata.

Passwords and secrets must never be returned.

## Users

Administrator only:

```http
GET   /users
POST  /users
PATCH /users/{user_id}
```

Users can be activated/deactivated and their roles can be changed.

An administrator cannot deactivate their own account.

## Storage Locations

```http
GET   /storage-locations
POST  /storage-locations
PATCH /storage-locations/{location_id}
```

Reading requires authentication.

Creating and modifying locations requires administrator privileges.

## Products

```http
GET    /products
GET    /products/{product_id}
POST   /products
PATCH  /products/{product_id}
DELETE /products/{product_id}
POST   /products/{product_id}/image
```

`DELETE` currently deactivates the product. It does not physically delete it.

`GET /products` supports:

```text
include_inactive=true
```

to include inactive products.

Product creation is available to authenticated users.

Product modification, deactivation, and image upload require administrator privileges.

## Barcode Lookup

```http
GET /scan/{barcode}
```

Behavior:

```text
local product found
    -> return local product

local product not found
    -> query Open Food Facts
    -> return optional suggestion
```

No product is automatically created from Open Food Facts data.

## Inventory

### Add inventory

```http
POST /inventory
```

The request contains the product, quantity, optional expiration date, optional storage location, and optional client operation ID.

The server creates an inventory entry.

### Consume inventory

```http
POST /products/{product_id}/consume
```

The request specifies the quantity to consume.

The backend performs FEFO consumption.

The client does not specify which inventory entries are consumed.

### Correct inventory

```http
POST /products/{product_id}/correct
```

Administrator operation.

The correction is recorded as a transaction.

### List inventory

```http
GET /inventory
```

Optional status filtering is supported.

### Expiring inventory

```http
GET /expiring?days=14
```

Returns active inventory entries with an expiration date within the requested horizon.

## Shopping List

### List

```http
GET /shopping-list
```

### Update status

```http
PATCH /shopping-list/{product_id}
```

The current implementation identifies a shopping-list entry by product ID.

## Transactions

Administrator only:

```http
GET /transactions
```

The endpoint supports a configurable result limit.

The transaction history includes the associated product and user information.

## Recipe Prompt

```http
GET /ai/prompt
```

Returns a generated recipe prompt based on current inventory.

This endpoint does not call an AI provider.

It only generates structured prompt text.

## API Stability

The API is currently an internal household API.

Before the Android application becomes dependent on the API, request and response models should be treated as a formal client contract.

Breaking API changes should then require an explicit versioning or migration strategy.
