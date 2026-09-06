# Database

## Overview

FoodStock uses PostgreSQL as its central relational database.

The database is accessed exclusively by FoodStock-Home.

FoodStock-Mobile never connects directly to PostgreSQL.

The current schema is defined by the SQLAlchemy ORM models in the backend.

## Current Schema

The current application schema contains these tables:

```text
users
storage_locations
products
inventory
shopping_list
transactions
```

The current implementation does **not** contain separate tables named:

```text
roles
audit_events
file_objects
inventory_units
inventory_transactions
```

Those concepts are either represented by existing columns/tables or remain future architectural options.

## Entity Relationships

The main relationships are:

```text
users
  │
  ├──────────────┐
  │              │
  ▼              ▼
inventory     transactions
  │              │
  ▼              │
products ◄───────┘
  │
  ├── default_storage_location
  │
  └── shopping_list

storage_locations
  │
  └── parent_id → storage_locations
```

Inventory records represent individual stock entries for a product.

Transactions record inventory-changing operations.

## `users`

The `users` table stores application users.

Current fields:

```text
id
username
password_hash
role
active
created_at
```

### Constraints

`username` is unique.

`role` uses the application's `UserRole` enum.

### Active state

Users can be deactivated without being physically removed.

Inactive users cannot authenticate successfully.

## `storage_locations`

The `storage_locations` table represents physical storage locations.

Current fields:

```text
id
name
parent_id
active
created_at
```

### Hierarchical locations

`parent_id` allows storage locations to form a hierarchy.

Example:

```text
Basement
└── Shelf 2
```

A storage location can therefore represent either a top-level area or a child location.

Location names are unique.

## `products`

The `products` table stores the product master data.

Current fields:

```text
id
barcode
name
manufacturer
category
unit
image_path
default_storage_location_id
minimum_stock
ideal_stock
active
created_at
updated_at
```

### Barcode

The barcode is unique when present.

Products without a barcode are supported.

### Active state

Products support soft deactivation through the `active` field.

The API's `DELETE /products/{product_id}` operation currently deactivates the product rather than physically deleting the database record.

This protects existing inventory and transaction references.

### Stock targets

`minimum_stock` defines the threshold below which replenishment may be required.

`ideal_stock` defines the desired target level when configured.

These values are used by the shopping-list logic.

## `inventory`

The `inventory` table represents individual stock entries.

Current fields:

```text
id
product_id
quantity
expiration_date
storage_location_id
status
image_path
added_by
added_at
consumed_at
```

### Inventory status

The current status values are:

```text
active
consumed
missing
deleted
```

### Active inventory

`active` inventory represents currently available physical stock.

Only active inventory participates in normal FEFO consumption.

### Consumed inventory

When an inventory entry is completely consumed, its status changes to:

```text
consumed
```

and `consumed_at` is populated.

### Missing inventory

`missing` represents stock that is known to be absent.

It is used to preserve negative-stock situations instead of silently discarding the difference between requested and available quantities.

### Deleted inventory

The model supports a deleted status for inventory lifecycle handling.

The application should prefer state changes over physical database deletion where historical traceability matters.

## FEFO

FoodStock uses:

**FEFO — First Expire, First Out**

When inventory is consumed, active entries are ordered by:

1.  Known expiration date
2.  `added_at`

The backend performs the selection and update inside the database transaction.

The client does not choose individual inventory records.

This keeps the inventory-consumption rule centralized.

## `shopping_list`

The `shopping_list` table stores the current shopping-list state per product.

The ORM model is:

```text
ShoppingListItem
```

Current fields:

```text
product_id
quantity
status
updated_by
updated_at
```

`product_id` is the primary key.

Therefore, the current implementation allows at most one shopping-list entry per product.

### Status

Shopping-list status uses the application's `ShoppingStatus` enum.

The current API updates the status through:

```text
PATCH /shopping-list/{product_id}
```

## `transactions`

The `transactions` table records inventory-changing operations.

Current fields:

```text
id
product_id
inventory_id
user_id
event
quantity_delta
reason
client_operation_id
created_at
```

### Purpose

The transaction table currently serves both as:

-   inventory operation history
-   audit/history information

A separate `audit_events` table does not currently exist.

### Quantity delta

Inventory changes are represented through `quantity_delta`.

Examples:

```text
+5  added
-2  consumed
+3  corrected
-1  corrected
```

### Client operation ID

`client_operation_id` is used for idempotency.

It has a unique database constraint:

```text
uq_transaction_operation
```

This allows the backend to recognize a previously processed client operation and avoid applying the same inventory mutation twice.

This mechanism is important for offline-capable clients and request retries.

## Referential Relationships

The current schema uses foreign keys to maintain relationships between the main entities.

Important relationships include:

```text
products.default_storage_location_id
    → storage_locations.id

inventory.product_id
    → products.id

inventory.storage_location_id
    → storage_locations.id

inventory.added_by
    → users.id

transactions.product_id
    → products.id

transactions.inventory_id
    → inventory.id

transactions.user_id
    → users.id

shopping_list.product_id
    → products.id

shopping_list.updated_by
    → users.id
```

The exact SQLAlchemy relationship configuration remains defined by the ORM models and should be treated as the implementation source of truth.

## Images and Files

Product and inventory images are stored on the persistent FoodStock filesystem.

PostgreSQL stores image paths rather than binary image data.

The current implementation does not have a generalized `file_objects` table.

The current storage model is intentionally simple:

```text
/data/foodstock/
└── products/
    └── <product-id>.<extension>
```

The filesystem is therefore part of the application's persistent data and must be included in backups.

## Database Initialization

The current application does not use Alembic migrations.

The SQLAlchemy metadata is used to initialize the schema.

This is acceptable for the current development stage but does not provide a complete versioned schema-migration strategy.

## Migration Strategy

Before the application requires regular schema-changing releases, a migration system should be introduced.

The preferred future approach is:

```text
SQLAlchemy models
       │
       ▼
Alembic migration
       │
       ▼
PostgreSQL schema
```

Each schema change should then have an explicit migration.

Until this is implemented, documentation must not imply that Alembic migrations are already available.

## Backup Requirements

A complete FoodStock backup must include both:

-   PostgreSQL data
-   `/data/foodstock` persistent files

Backing up only PostgreSQL is insufficient because product/image files are stored outside the database.

A backup should be considered operationally valid only after restoration has been tested.

## Source of Truth

For the current database schema, the following are authoritative:

1.  SQLAlchemy models
2.  Actual PostgreSQL schema
3.  Database migration files once a migration system is introduced

This document describes the current logical schema and must be updated whenever the persistent data model changes.
