# FoodStock Database Design

## 1\. Database

FoodStock uses PostgreSQL.

The current deployment uses PostgreSQL through the installed TimescaleDB Home Assistant App.

Database:

```text
foodstock
```

## 2\. Design Principles

The database should:

-   Use relational modeling
-   Avoid unnecessary duplication
-   Use foreign keys
-   Use appropriate indexes
-   Use transactions
-   Use UTC timestamps
-   Preserve audit information
-   Support future meal planning
-   Avoid storing large binary images directly in PostgreSQL

## 3\. Core Tables

Initial core tables:

```text
users
roles
products
storage_locations
inventory_units
shopping_list_items
inventory_transactions
audit_events
file_objects
```

Additional tables may be added when required.

## 4\. Users

Conceptual structure:

```text
users
-----
id
username
display_name
password_hash
role_id
active
created_at
updated_at
last_login_at
```

Passwords must never be stored in plaintext.

## 5\. Roles

```text
roles
-----
id
name
```

Initial roles:

```text
user
admin
```

Authorization must be role-based.

## 6\. Products

```text
products
--------
id
barcode
name
manufacturer
category
unit
default_storage_location_id
minimum_stock
ideal_stock
active
created_at
updated_at
```

The barcode should be indexed.

Barcode uniqueness should be enforced where appropriate.

## 7\. Storage Locations

```text
storage_locations
-----------------
id
name
description
parent_id
active
created_at
updated_at
```

The optional `parent_id` allows structures such as:

```text
Basement
 ├── Shelf 1
 ├── Shelf 2
 └── Freezer
```

## 8\. Inventory Units

```text
inventory_units
---------------
id
product_id
expiration_date
storage_location_id
status
added_by
added_at
consumed_at
file_object_id
```

Possible statuses:

```text
active
consumed
removed
expired
```

The exact status model will be finalized during implementation.

## 9\. Inventory Transactions

Inventory mutations should be represented by transactions.

Conceptual structure:

```text
inventory_transactions
----------------------
id
product_id
inventory_unit_id
user_id
transaction_type
quantity
reason
created_at
```

Examples:

```text
added
consumed
purchased
corrected
removed
restored
```

## 10\. Shopping List

```text
shopping_list_items
-------------------
id
product_id
quantity
state
created_at
updated_at
purchased_at
added_to_inventory_at
```

The shopping list should be derived and synchronized from inventory state.

## 11\. Audit Events

```text
audit_events
------------
id
user_id
event_type
entity_type
entity_id
old_value
new_value
reason
created_at
```

For complex changes, JSONB may be used for `old_value` and `new_value`.

## 12\. File Objects

```text
file_objects
------------
id
storage_key
original_name
mime_type
size_bytes
checksum
purpose
created_at
```

Possible purposes:

```text
product_image
expiration_image
export
```

## 13\. Indexing

Important indexes include:

```text
products.barcode
products.active
inventory_units.product_id
inventory_units.expiration_date
inventory_units.status
inventory_units.storage_location_id
shopping_list_items.product_id
audit_events.created_at
audit_events.user_id
```

Composite indexes will be added where query patterns justify them.

## 14\. Referential Integrity

Foreign keys should be used wherever possible.

Deletion should normally use logical deactivation rather than physical deletion for entities referenced by historical records.

## 15\. Time Handling

Database timestamps should be stored consistently in UTC.

The mobile application converts timestamps to the user's locale.

Expiration dates are date values rather than timestamps.

This distinction is important.

For example:

```text
2026-09-15
```

is an expiration date.

It should not accidentally become:

```text
2026-09-14 22:00 UTC
```

because of timezone conversion.

## 16\. Stock Calculation

The application should not duplicate stock values unnecessarily.

Current stock should primarily be derived from the inventory model and inventory transactions.

If denormalized summary values are introduced later for performance, they must have a clearly defined consistency mechanism.

## 17\. Negative Stock

Negative stock is a valid business state.

It must not be represented by an invalid negative inventory-unit count.

Instead, negative quantity must be represented by the transaction/adjustment model.

This distinction prevents contradictions between physical inventory units and calculated stock.

## 18\. Future Meal Planning

The database structure intentionally keeps products, inventory and shopping data separate.

This allows future entities such as:

```text
recipes
recipe_ingredients
meal_plans
meal_plan_items
```

without redesigning the core inventory model.
