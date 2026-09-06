# Database

## Current Tables

The current schema contains these application tables:

```text
users
storage_locations
products
inventory
shopping_list
transactions
```

There is no separate:

```text
roles
audit_events
file_objects
inventory_units
```

table in the current implementation.

## users

```text
id
username
password_hash
role
active
created_at
```

Constraints:

-   `username` is unique
-   `role` uses the `UserRole` enum

## storage\_locations

```text
id
name
parent_id
active
created_at
```

`parent_id` allows hierarchical storage locations.

Example:

```text
Basement
└── Shelf 2
```

Location names are unique.

## products

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

`barcode` is unique when present.

`active` provides soft deactivation.

Product deletion therefore does not physically remove the product.

## inventory

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

Inventory statuses:

```text
active
consumed
missing
deleted
```

`missing` represents confirmed negative stock.

## shopping\_list

The database table is named:

```text
shopping_list
```

The ORM model is `ShoppingListItem`.

Columns:

```text
product_id
quantity
status
updated_by
updated_at
```

`product_id` is the primary key.

This means there is currently at most one shopping-list record per product.

## transactions

The `transactions` table is the authoritative history for inventory mutations.

Columns:

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

`client_operation_id` has a unique constraint.

This provides server-side idempotency for supported inventory commands.

The transaction table currently serves the audit/history purpose. A separate audit-event table does not exist.

## Storage

Product and inventory images are stored on the filesystem.

PostgreSQL stores paths, not binary image content.

The current implementation does not provide a generalized file metadata table.

## Migrations

Schema migrations are not yet managed by Alembic.

Adding Alembic should be treated as a future infrastructure task before database schema changes become frequent.
