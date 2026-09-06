# FoodStock Requirements

## 1. Users and Roles

FoodStock supports multiple household users.

### User

A normal user can:

- Log in
- View products
- Add products
- Add inventory
- Consume inventory
- Correct inventory where permitted
- View current inventory
- View expiration information
- View and update the shopping list
- Generate the available AI recipe prompt

### Administrator

An administrator has additional management permissions:

- Manage users
- Manage products
- Manage storage locations
- Deactivate products
- Restore products where supported
- Perform administrative inventory corrections
- View transaction history

The current implementation uses two roles:

- `user`
- `admin`

Roles are stored directly on the user record. A separate roles table is not required.

---

## 2. Product Management

A product represents reusable product information and is independent of individual inventory records.

A product may contain:

- Name
- Barcode
- Manufacturer
- Unit
- Default storage location
- Minimum stock level
- Ideal stock level
- Product image
- Active/inactive state

Products can be created manually or populated from external product information sources.

External product information must not silently overwrite trusted local product data.

---

## 3. Inventory Management

Inventory represents the physical food currently associated with a product.

An inventory record contains:

- Product
- Quantity
- Expiration date
- Storage location
- Status
- Optional image path
- User who added the inventory
- Creation timestamp
- Consumption timestamp

An inventory record may represent multiple physical units with the same expiration date and storage location.

The system does **not** require every physical item to be represented by a separate database record.

### Inventory statuses

The current implementation supports the following inventory statuses:

- `active`
- `missing`
- `consumed`
- `deleted`

`active` records represent physical stock.

`missing` records represent stock that was requested or consumed but was not physically available.

`consumed` records represent inventory that has been consumed.

`deleted` records represent inventory that has been removed from active use.

---

## 4. Inventory Quantity

The current product stock is calculated from inventory records.

The `transactions` table records inventory operations but is not itself the source of the current stock quantity.

For stock calculation:

- `active` inventory contributes positively
- `missing` inventory contributes negatively
- `consumed` inventory does not contribute
- `deleted` inventory does not contribute

For example:

```text
Active inventory:   10
Missing inventory:   2
-----------------------
Current stock:       8
```

Negative stock is therefore explicitly supported.

If more food is consumed than is physically available, the backend creates a `missing` inventory record for the remaining shortage.

For example:

```text
Available stock: 2
Consume:         5

Result:

2 units consumed
3 units recorded as missing

Calculated stock: -3
```

The backend is responsible for applying these rules.

* * *

## 5\. Inventory Operations

Inventory mutations are performed by the backend.

Supported operations include:

-   Add inventory
-   Consume inventory
-   Correct inventory

The client must not blindly overwrite the complete inventory quantity based on stale locally cached data.

Inventory changes should instead be represented as explicit operations.

### Client operation IDs

Inventory mutation requests may contain a client-generated `client_operation_id`.

The backend uses this identifier to prevent the same operation from being applied more than once.

This provides idempotent operation replay and allows the mobile application to safely retry operations.

This mechanism can also be used as a foundation for future offline workflows.

It does not mean that the complete mobile application currently operates fully offline.

* * *

## 6\. FEFO Consumption

Inventory consumption follows **FEFO (First Expire, First Out)**.

When consuming inventory, the backend selects available inventory in the following order:

1.  Inventory with an expiration date
2.  Earliest expiration date first
3.  Earliest `added_at` timestamp as a secondary ordering criterion

Inventory without an expiration date is consumed after inventory with an expiration date.

Inventory rows selected for consumption are locked during the database transaction to prevent conflicting concurrent consumption operations.

The mobile application must not implement a conflicting consumption algorithm.

* * *

## 7\. Storage Locations

Inventory can be assigned to a storage location.

Examples include:

-   Refrigerator
-   Freezer
-   Pantry
-   Basement
-   Kitchen cabinet

Storage locations are managed by the backend.

Products may also have a default storage location.

The default product storage location is used as a convenience when creating inventory but does not prevent an inventory record from using another location.

* * *

## 8\. Shopping List

The shopping list is based on product stock levels.

A product is considered below its minimum stock level when:

```text
current_stock < minimum_stock
```

If the current stock is below the minimum stock level, the product can be placed on the shopping list.

If an ideal stock level is configured, the target purchase quantity is calculated using the ideal stock level.

Otherwise, the minimum stock level is used.

Conceptually:

```text
if ideal_stock is configured:
    purchase_quantity = ideal_stock - current_stock
else:
    purchase_quantity = minimum_stock - current_stock
```

The calculated purchase quantity must not become negative.

The backend updates the shopping-list state as part of relevant inventory operations.

The current implementation does not use a separate background synchronization process that continuously recalculates every product.

* * *

## 9\. Shopping List States

The shopping list supports the following states:

-   `needed`
-   `on_list`
-   `purchased`
-   `stocked`

These states allow the shopping process to be tracked beyond a simple yes/no flag.

The intended workflow is:

```text
needed
  ↓
on_list
  ↓
purchased
  ↓
stocked
```

Future versions may connect the `purchased` and `stocked` states more closely to barcode scanning and inventory creation.

* * *

## 10\. Expiration Date Management

Every inventory record may contain an expiration date.

Expiration dates are used for:

-   Expiration warnings
-   FEFO consumption
-   Recipe prompt prioritization
-   Inventory display

The current expiration categories are:

Category

Condition

Expired

Expiration date is before today

Urgent

Expires within 0–3 days

Soon

Expires within 4–7 days

Upcoming

More than 7 days away

These thresholds are currently implemented as fixed values.

### Future requirement

The expiration thresholds should eventually become configurable rather than hard-coded.

* * *

## 11\. Expiration Date OCR

Expiration-date OCR is intended to be performed locally on the mobile device.

The intended workflow is:

```text
Camera
  ↓
Local OCR
  ↓
Candidate expiration date
  ↓
Validation
  ↓
User confirmation
  ↓
Backend
```

OCR results are suggestions and must not automatically become trusted inventory data.

The user must be able to review and confirm the detected expiration date before it is stored.

The backend stores the confirmed expiration date on the inventory record.

* * *

## 12\. Expiration Images

Persistent storage of expiration-date images is a planned feature.

The intended future workflow is:

```text
Capture image
  ↓
Local OCR
  ↓
Detect expiration date
  ↓
User confirmation
  ↓
Optional image upload
  ↓
Backend storage
```

The current backend does not provide a complete persistent expiration-image workflow.

The presence of an optional `save_expiration_image` field must therefore not be interpreted as full expiration-image support.

Future implementation may add:

-   Persistent expiration images
-   Image metadata
-   Image retention policies
-   Image deletion
-   Image access through the API

* * *

## 13\. Barcode Processing

Barcode recognition is intended to be performed on the mobile device.

The intended lookup sequence is:

```text
Scan barcode
  ↓
Local FoodStock product database
  ↓
Product found?
  ├── Yes → return local product
  └── No  → external product lookup
```

The backend can use external product data sources such as Open Food Facts when a local product cannot be found.

External data is treated as a suggestion.

The current implementation does not automatically create or overwrite a trusted local product from an external lookup.

The user must confirm the information before it becomes trusted local product data.

* * *

## 14\. Product Images

Products can have an associated image.

The current implementation stores the image file in application storage and stores the corresponding path/reference in the product record.

Image binary data is not stored directly in PostgreSQL.

The current product-image upload implementation supports:

-   JPEG
-   PNG
-   WebP

The current maximum upload size is 10 MB.

A future dedicated file/object metadata system may be introduced if more advanced file management becomes necessary.

* * *

## 15\. Inventory Images

Inventory records may also contain an image path.

The current implementation uses application file storage rather than a dedicated database file-object model.

Advanced image management is considered a future extension.

* * *

## 16\. Transactions and History

Inventory operations are recorded in the `transactions` table.

A transaction can contain:

-   User
-   Product
-   Inventory record
-   Event
-   Quantity delta
-   Reason
-   Client operation ID
-   Creation timestamp

The transaction history is intended to provide an operational history of inventory changes.

Administrators can access transaction history.

The transaction model is not currently a generic audit-event system.

### Future audit requirements

A future audit system may provide:

-   Generic object targets
-   Before/after values
-   More detailed change information
-   Audit events for additional entity types
-   Administrative audit reporting

These features are not part of the current transaction implementation.

* * *

## 17\. AI and Recipe Support

FoodStock provides backend support for generating a recipe-oriented AI prompt.

The current feature does not require a direct connection to an AI provider.

The generated prompt is intended to prioritize food that should be consumed soon.

The current implementation prioritizes inventory with expiration dates within the next 14 days.

These items are ordered by expiration date.

Other available inventory can then be included as additional ingredients.

The generated prompt can be copied or passed to an external AI service by the client.

### Future AI requirements

Future versions may support:

-   Direct AI provider integration
-   Automatic recipe generation
-   Structured recipe responses
-   Meal planning
-   Ingredient substitution
-   Shopping-list integration

* * *

## 18\. Data Validation

The backend is responsible for validating data received from clients.

Validation includes:

-   Required fields
-   Data types
-   Authentication
-   Authorization
-   Product references
-   Storage-location references
-   Inventory quantities
-   Inventory operation parameters
-   Image upload restrictions

The mobile application may perform additional client-side validation for usability, but server-side validation remains authoritative.

* * *

## 19\. Authentication

FoodStock uses token-based authentication.

Users authenticate against the backend and receive a JWT access token.

The backend uses the authenticated identity to determine:

-   User identity
-   User role
-   Authorization

Passwords are stored using secure password hashing and are never stored in plaintext.

The current implementation does not provide a separate refresh-token system.

* * *

## 20\. Authorization

Authorization is enforced by the backend.

Client-side UI restrictions are not considered sufficient security controls.

Administrative operations must require the administrator role.

Examples include:

-   User management
-   Administrative inventory corrections
-   Product administration
-   Product image management
-   Storage-location administration
-   Transaction-history access

The backend remains responsible for enforcing these permissions even if a malicious client bypasses the mobile application's UI restrictions.

* * *

## 21\. Data Ownership and Privacy

FoodStock is designed for self-hosted household use.

The household hosting the application owns and controls its inventory data.

The PostgreSQL database must not be exposed directly to mobile clients.

Mobile clients communicate with the FoodStock backend through its HTTP API.

External services such as Open Food Facts are optional and should only receive the information required for the requested lookup.

* * *

## 22\. Offline and Retry Behavior

The backend supports idempotent inventory mutation requests through `client_operation_id`.

A client may safely retry the same operation using the same operation ID.

The backend must not apply an already completed operation a second time.

This provides the server-side foundation for reliable retry behavior.

A complete offline-first mobile architecture, including:

-   Local database
-   Offline reads
-   Offline mutation queue
-   Synchronization
-   Conflict resolution

is not currently part of the implemented backend.

* * *

## 23\. Home Assistant Integration

FoodStock-Home is designed to run as a Home Assistant application.

The core FoodStock backend should remain responsible for its own business logic.

Future Home Assistant integration may provide:

-   Sensors
-   Notifications
-   Dashboard cards
-   Automations
-   Voice interaction

The core inventory functionality must not depend on Home Assistant-specific APIs.

* * *

## 24\. Internationalization

FoodStock is intended to support at least:

-   English
-   German

The mobile application should use localized user-facing strings rather than hard-coded text.

Technical documentation remains in English.

* * *

## 25\. Future Requirements

The following features are planned but are not part of the current core implementation:

-   Configurable expiration thresholds
-   Persistent expiration images
-   Advanced file metadata management
-   Full offline-first mobile operation
-   Conflict resolution and synchronization
-   Direct AI provider integration
-   Automatic recipe generation
-   Meal planning
-   Advanced Home Assistant integration
-   Additional audit functionality
-   Barcode-driven shopping-list completion
-   Automatic product creation from external product data

Future features must preserve the core principles of server-side business logic, household data ownership and safe inventory mutations.
