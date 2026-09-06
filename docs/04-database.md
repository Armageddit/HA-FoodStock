# FoodStock Database Design

-   #### ChatGPT:
    
    Sure — here is the **English preview for `04-database.md`**, keeping the same review format as before.
    
    # `docs/04-database.md`
    
    This file is currently one of the more outdated documents. It describes a considerably larger and more complex database model than what is actually implemented in `foodstock/app/models.py`.
    
    The main issue is that the documentation mixes the **planned database architecture** with the **current SQLAlchemy implementation**.
    
    ## 1\. Current Tables
    
    The documentation currently describes tables such as:
    
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
    
    The current implementation instead contains these core models:
    
    ```text
    User
    StorageLocation
    Product
    Inventory
    ShoppingList
    Transaction
    ```
    
    Therefore, the current database overview should be:
    
    ```text
    users
    storage_locations
    products
    inventory
    shopping_list
    transactions
    ```
    
    The database schema is currently derived from the SQLAlchemy models. (github.com)
    
    * * *
    
    ## 2\. `roles` Table
    
    The documentation currently describes a separate `roles` table.
    
    That table does **not** exist in the current implementation.
    
    The user's role is stored directly on the `users` table:
    
    ```text
    users
    └── role
    ```
    
    The currently supported roles are:
    
    ```text
    user
    admin
    ```
    
    There is no separate role entity or role relationship.
    
    ### Required change
    
    Replace the documented role table with:
    
    ```text
    users.role
    ```
    
    and explain that authorization is based on this field.
    
    * * *
    
    ## 3\. `inventory_units` Is Outdated
    
    The documentation currently refers to individual inventory units.
    
    The actual table is:
    
    ```text
    inventory
    ```
    
    and the corresponding SQLAlchemy model is:
    
    ```text
    Inventory
    ```
    
    The current implementation does **not** create one database row for every physical item.
    
    Instead, an inventory record contains a quantity:
    
    ```text
    product_id
    quantity
    expiration_date
    storage_location_id
    status
    ```
    
    For example:
    
    ```text
    Product: Milk
    Quantity: 5
    Expiration: 2026-09-20
    Location: Refrigerator
    ```
    
    represents five units through a single inventory record.
    
    This distinction should be reflected throughout the database documentation.
    
    * * *
    
    ## 4\. Current `Inventory` Model
    
    The database documentation should describe the actual fields of the `Inventory` model.
    
    The current model includes fields such as:
    
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
    
    with relationships to:
    
    ```text
    products
    storage_locations
    users
    ```
    
    The exact field names should be taken directly from `models.py` when the final document is written. (github.com)
    
    * * *
    
    ## 5\. Inventory Status
    
    The current implementation uses the following inventory statuses:
    
    ```text
    active
    missing
    consumed
    deleted
    ```
    
    These values should be documented exactly as implemented.
    
    The `missing` status is particularly important because it is used to represent stock that was requested for consumption but was not physically available.
    
    For example:
    
    ```text
    Active inventory:
    quantity = 5
    
    Missing inventory:
    quantity = 2
    ```
    
    The calculated stock becomes:
    
    ```text
    5 - 2 = 3
    ```
    
    The application does not represent this by storing:
    
    ```text
    quantity = -3
    ```
    
    * * *
    
    ## 6\. `transactions`
    
    The current table is:
    
    ```text
    transactions
    ```
    
    with the SQLAlchemy model:
    
    ```text
    Transaction
    ```
    
    The documentation should not refer to this as `inventory_transactions`.
    
    The current transaction model contains fields such as:
    
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
    
    These transactions represent inventory-related operations and provide the history of those operations. (github.com)
    
    * * *
    
    ## 7\. Transactions Are Not Generic Audit Events
    
    The current documentation describes a separate:
    
    ```text
    audit_events
    ```
    
    table.
    
    This does not currently exist.
    
    `transactions` should be described as an **inventory transaction history**, not as a generic audit framework.
    
    It records operations such as:
    
    ```text
    add
    consume
    correct
    ```
    
    together with the relevant product, inventory record, user and quantity change.
    
    A full generic audit system can remain a future enhancement.
    
    * * *
    
    ## 8\. `file_objects` Does Not Exist
    
    The documentation currently describes a dedicated `file_objects` table.
    
    There is no such model in the current implementation.
    
    Images are currently represented by paths stored directly on the relevant models, for example:
    
    ```text
    Product.image_path
    Inventory.image_path
    ```
    
    The actual files are stored in application storage.
    
    Therefore, the database documentation should not describe a database-backed file-object abstraction as an existing feature.
    
    * * *
    
    ## 9\. `Product` Model
    
    The current `Product` model contains fields including:
    
    ```text
    id
    name
    barcode
    manufacturer
    unit
    default_storage_location_id
    minimum_stock
    ideal_stock
    image_path
    active
    created_at
    updated_at
    ```
    
    The exact field list should be verified directly against `models.py` when the final documentation is produced. (github.com)
    
    An important relationship is:
    
    ```text
    Product
    ├── default storage location
    ├── inventory records
    ├── shopping list
    └── transactions
    ```
    
    * * *
    
    ## 10\. Storage Locations
    
    `storage_locations` is a real current table and should remain part of the documented schema.
    
    There are two distinct concepts that need to be documented:
    
    ### Product default location
    
    ```text
    Product.default_storage_location_id
    ```
    
    This provides a default location when creating inventory.
    
    ### Actual inventory location
    
    ```text
    Inventory.storage_location_id
    ```
    
    An inventory record can use a different location from the product's default location.
    
    For example:
    
    ```text
    Product default:
    Pantry
    
    Actual inventory:
    Kitchen cabinet
    ```
    
    This distinction is supported by the current data model. (github.com)
    
    * * *
    
    ## 11\. Shopping List
    
    The current table is:
    
    ```text
    shopping_list
    ```
    
    rather than:
    
    ```text
    shopping_list_items
    ```
    
    The shopping list is associated with products.
    
    The current implementation uses these states:
    
    ```text
    needed
    on_list
    purchased
    stocked
    ```
    
    The database documentation should use these exact values.
    
    The shopping list is therefore not simply a Boolean `is_on_list` flag.
    
    * * *
    
    ## 12\. User Relationships
    
    Inventory records contain information about the user who added them.
    
    Conceptually:
    
    ```text
    users
       │
       └── inventory
    ```
    
    Transactions also reference the user responsible for the operation:
    
    ```text
    users
       │
       └── transactions
    ```
    
    This allows inventory changes and their corresponding operations to be associated with a user.
    
    * * *
    
    ## 13\. `client_operation_id`
    
    This field should be explicitly documented.
    
    The transaction model contains:
    
    ```text
    client_operation_id
    ```
    
    It is used to support idempotent inventory operations.
    
    The basic flow is:
    
    ```text
    Mobile Client
         |
         | client_operation_id
         v
    FoodStock API
         |
         v
    Transaction
    ```
    
    If the client retries the same operation using the same operation ID, the backend can recognize that the operation has already been processed.
    
    This is particularly important for reliable mobile retries.
    
    * * *
    
    ## 14\. Inventory and Transaction Relationships
    
    The database relationships should be represented approximately as:
    
    ```text
    Product
       │
       ├── Inventory
       │      │
       │      └── Transaction
       │
       ├── ShoppingList
       │
       └── Transaction
    ```
    
    Inventory also references:
    
    ```text
    StorageLocation
    User
    ```
    
    Transactions reference:
    
    ```text
    Product
    Inventory
    User
    ```
    
    This reflects the current SQLAlchemy relationships more accurately than the older database diagram. (github.com)
    
    * * *
    
    ## 15\. Current Stock Is Not Stored on `products`
    
    The current product model does not contain a simple:
    
    ```text
    products.stock
    ```
    
    field.
    
    Current stock is derived from inventory records.
    
    Conceptually:
    
    ```text
    stock =
        SUM(active inventory quantity)
        -
        SUM(missing inventory quantity)
    ```
    
    `consumed` and `deleted` inventory records do not contribute to the current stock.
    
    Transactions provide historical information but are not themselves the source of the current stock calculation.
    
    * * *
    
    ## 16\. Negative Stock
    
    Negative stock is not represented by negative inventory quantities.
    
    For example, if:
    
    ```text
    Available:
    2
    
    Requested consumption:
    5
    ```
    
    the backend can represent the result through:
    
    ```text
    2 units consumed
    3 units missing
    ```
    
    The database therefore retains non-negative quantity values while the calculated product stock can become negative.
    
    Conceptually:
    
    ```text
    Active:
    2
    
    Missing:
    3
    
    Calculated stock:
    -1
    ```
    
    This behavior should be explicitly documented because it is an important part of the current inventory model.
    
    * * *
    
    ## 17\. Timestamps
    
    The final documentation should only describe timestamp fields that actually exist in the current models.
    
    Relevant fields include:
    
    ```text
    created_at
    updated_at
    added_at
    consumed_at
    ```
    
    The exact timestamp behavior and nullability should be taken from `models.py` rather than copied from the older documentation. (github.com)
    
    * * *
    
    ## 18\. Database Initialization
    
    The current backend does **not** use Alembic migrations.
    
    At application startup, SQLAlchemy currently initializes the schema using:
    
    ```python
    Base.metadata.create_all(engine)
    ```
    
    This means:
    
    -   SQLAlchemy models define the current schema
    -   Missing tables are created during startup
    -   The current implementation does not maintain versioned Alembic migrations
    -   Schema evolution is therefore not currently handled through migration files
    
    This should be documented accurately rather than describing an Alembic-based migration workflow.
    
    * * *
    
    ## 19\. Current Database Overview
    
    The final documentation should contain a concise overview similar to:
    
    ```text
    ┌─────────────────────┐
    │       users         │
    └─────────┬───────────┘
              │
              ├───────────────┐
              │               │
              ▼               ▼
        ┌───────────┐   ┌──────────────┐
        │ inventory │   │ transactions │
        └─────┬─────┘   └──────┬───────┘
              │                │
              └───────┬────────┘
                      ▼
                ┌──────────┐
                │ products │
                └────┬─────┘
                     │
            ┌────────┴─────────┐
            ▼                  ▼
    ┌──────────────────┐ ┌───────────────┐
    │ storage_locations│ │ shopping_list │
    └──────────────────┘ └───────────────┘
    ```
    
    The exact relationship cardinalities should be verified against the SQLAlchemy definitions before finalizing the document.
    
    * * *
    
    # Required Changes
    
    ### 🔴 Must be corrected
    
    -   Remove `roles` as a database table
    -   Rename `inventory_units` → `inventory`
    -   Rename `inventory_transactions` → `transactions`
    -   Remove `audit_events`
    -   Remove `file_objects`
    -   Remove the assumption that every physical item has its own database row
    -   Document `quantity`\-based inventory
    -   Document the actual inventory statuses
    -   Document `missing` inventory
    -   Remove negative `quantity` as the representation of negative stock
    -   Remove Alembic as a current implementation
    -   Document `client_operation_id`
    
    ### 🟠 Should be clarified
    
    -   Product default storage location vs. actual inventory storage location
    -   Transaction vs. audit event
    -   Stock calculation
    -   User relationships
    -   Timestamp fields
    -   Database initialization
    -   Actual SQLAlchemy relationships
    
    ### 🟢 Can remain
    
    -   PostgreSQL
    -   SQLAlchemy
    -   Product model
    -   Storage locations
    -   Inventory history
    -   Shopping list
    -   User references
    -   Foreign-key relationships
