# Requirements

## Users

FoodStock currently supports two roles.

### User

A normal user can:

-   authenticate
-   view products
-   create products
-   view inventory
-   add inventory
-   consume inventory
-   view expiration information
-   view the shopping list
-   update shopping-list status
-   generate a recipe prompt

### Administrator

An administrator can additionally:

-   create users
-   update users
-   activate or deactivate users
-   change user roles
-   manage storage locations
-   update products
-   deactivate products
-   upload product images
-   correct inventory
-   view transaction history

There is no separate database-backed role table. Roles are represented by the `UserRole` enum.

## Products

A product represents reusable product information.

A product contains:

-   name
-   optional barcode
-   optional manufacturer
-   optional category
-   unit
-   optional product image
-   optional default storage location
-   minimum stock
-   optional ideal stock
-   active state

A product does not represent a physical stock item.

## Inventory

Inventory is represented by inventory entries.

An inventory entry contains:

-   product
-   quantity
-   optional expiration date
-   optional storage location
-   status
-   optional image
-   user who added it
-   creation timestamp
-   optional consumption timestamp

An inventory entry may contain a quantity greater than one. Therefore the current model represents **inventory batches/entries**, not strictly one database row per physical item.

This distinction is important.

Example:

```text
Product: Milk

Inventory entry A:
quantity = 3
expiration_date = 2026-09-10

Inventory entry B:
quantity = 2
expiration_date = 2026-09-15
```

## Inventory Consumption

Consumption is handled by the server.

The client sends a consumption command. It does not send a calculated replacement stock value.

Active inventory entries are processed using FEFO:

> First Expire, First Out

The ordering is based on:

1.  entries with an expiration date before entries without one
2.  earliest expiration date
3.  earliest `added_at` timestamp

The database rows are locked during consumption to prevent conflicting concurrent updates.

If the requested consumption exceeds available stock, the missing quantity is represented by a `MISSING` inventory entry.

This allows negative stock to be represented explicitly.

## Shopping List

The backend calculates required purchase quantities centrally.

If:

```text
current_stock < minimum_stock
```

the product requires replenishment.

If `ideal_stock` is configured:

```text
purchase_quantity = ideal_stock - current_stock
```

Otherwise:

```text
purchase_quantity = minimum_stock - current_stock
```

Negative stock is supported.

Example:

```text
current stock = -2
minimum stock = 5
ideal stock = 10
```

The required quantity is:

```text
10 - (-2) = 12
```

The shopping list uses these states:

-   `needed`
-   `on_list`
-   `purchased`
-   `stocked`

## Expiration

The backend supports expiration queries using a configurable query horizon.

The dashboard categorizes results as:

-   expired
-   urgent: up to 3 days
-   soon: 4–7 days
-   upcoming: 8–14 days

These categories are currently fixed in the backend and are not yet user-configurable.

## Barcode Lookup

Barcode recognition is expected to happen on the client.

The backend provides lookup through:

```text
GET /scan/{barcode}
```

The backend:

1.  checks the local product database
2.  returns the local product if found
3.  otherwise queries Open Food Facts
4.  returns an external product suggestion if available

External information must not silently overwrite local product data.

## OCR

OCR is a client-side responsibility.

The expected workflow is:

```text
Camera
  |
  v
Local OCR
  |
  v
Candidate expiration date
  |
  v
User confirmation
  |
  v
FoodStock API
```

An OCR result must never be persisted as a confirmed expiration date without user confirmation.
