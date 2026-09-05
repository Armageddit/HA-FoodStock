# FoodStock Requirements

## 1\. Users

FoodStock supports at least two roles.

### User

A normal user can:

-   Sign in
-   Scan barcodes
-   Add products
-   Add inventory units
-   Capture expiration dates
-   Select storage locations
-   View inventory
-   Consume food
-   View the shopping list
-   Edit or complete shopping-list items
-   Generate AI recipe prompts

### Administrator

An administrator can additionally:

-   Manage products
-   Correct barcodes
-   Change product images
-   Correct expiration data
-   Correct inventory
-   Manage storage locations
-   Manage minimum stock
-   Manage ideal stock
-   Manage users
-   Deactivate products
-   Restore products where supported
-   View audit history

## 2\. Product Requirements

A product represents reusable product information.

Example:

```text
Product:
Tomato Sauce

Barcode:
4001234567890

Manufacturer:
Example GmbH

Unit:
piece

Default location:
Basement / Shelf 2

Minimum stock:
5

Ideal stock:
10
```

A product does not represent a physical food item.

## 3\. Inventory Requirements

Individual inventory units are stored separately.

Example:

```text
Milk 1.5%

02.09.2026
05.09.2026
05.09.2026
12.09.2026
20.09.2026
```

Each inventory unit has its own expiration date and storage location.

## 4\. Inventory Rules

The displayed inventory quantity is derived from active inventory units plus inventory adjustments represented by the transaction model.

Consumption follows FEFO:

> First Expire, First Out

The inventory unit with the earliest expiration date should normally be consumed first.

The application must never rely on a client-side quantity overwrite for concurrent inventory operations.

## 5\. Negative Inventory

Negative inventory is explicitly supported.

Example:

```text
Current stock: -2
Minimum stock: 5
Ideal stock: 10
```

This represents a shortage of two units.

## 6\. Shopping List Rules

If:

```text
current_stock < minimum_stock
```

the product must be represented on the shopping list.

If an ideal stock is configured:

```text
purchase_quantity = ideal_stock - current_stock
```

Otherwise:

```text
purchase_quantity = minimum_stock - current_stock
```

Example:

```text
current = 4
minimum = 5
ideal = 10

purchase = 10 - 4
purchase = 6
```

Without an ideal stock:

```text
current = 3
minimum = 5

purchase = 5 - 3
purchase = 2
```

Negative inventory:

```text
current = -2
minimum = 5

purchase = 5 - (-2)
purchase = 7
```

This logic must exist centrally in the backend.

## 7\. Expiration Categories

Initial categories:

Category

Rule

Expired

expiration date is before today

Urgent

within 3 days

Soon

within 7 days

Upcoming

within 14 days

The thresholds must eventually become configurable.

## 8\. Barcode Processing

Barcode recognition occurs locally on the smartphone.

The server receives the barcode value.

The backend then:

1.  Searches the local product database.
2.  If found, returns the product.
3.  If not found, optionally queries Open Food Facts.
4.  If Open Food Facts finds the product, the product can be proposed to the user.
5.  The user confirms imported information.
6.  If no product is found, the user can create it manually.

External product information must not automatically overwrite trusted local product information.

## 9\. OCR

OCR runs on the smartphone.

The workflow is:

```text
Camera
  |
  v
Local OCR
  |
  v
Candidate date
  |
  v
Validation
  |
  v
User confirmation
  |
  v
Server
```

No OCR result may be silently persisted as a confirmed expiration date.

## 10\. Optional Expiration Images

Expiration images are optional.

Default:

```text
Capture image
  -> OCR
  -> Confirm
  -> Delete image
```

Optional:

```text
Capture image
  -> OCR
  -> Confirm
  -> Upload image
```

## 11\. Product Images

Product images may originate from:

-   Open Food Facts
-   User camera
-   User upload

Binary image data must not be stored directly in PostgreSQL.

The database stores metadata and a storage reference.

## 12\. Shopping List States

The system must distinguish:

-   Needed
-   On shopping list
-   Purchased
-   Added to inventory

The shopping-list workflow must support future integration with product scanning.

## 13\. Audit Events

Important inventory and administrative actions must be recorded.

Examples:

-   Added
-   Consumed
-   Purchased
-   Corrected
-   Deleted
-   Restored

Audit records should contain the actor, timestamp, target object, operation and relevant before/after information.

## 14\. Future AI Support

The first AI feature does not require an AI API.

FoodStock-Mobile generates a structured prompt and copies it to the clipboard.

The prompt prioritizes:

1.  Food expiring soonest
2.  Other available food
3.  Minimal additional purchases

Direct AI API integration is a future optional feature.

## 15\. Future Meal Planning

The data model must support future meal planning without requiring a major database redesign.

The future planner can use:

-   Inventory
-   Quantities
-   Expiration dates
-   Shopping list
-   Product categories
