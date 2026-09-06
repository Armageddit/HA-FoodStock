# FoodStock Development Roadmap

## 1\. Purpose

This document defines the development roadmap for FoodStock.

The roadmap distinguishes between:

-   Features already implemented
-   Features that still require installation or acceptance testing
-   Planned features
-   Optional future enhancements

A feature must not be marked as completed merely because related source code exists. Where appropriate, implementation, deployment, functional testing and regression testing must all be completed before a phase is considered operationally complete.

The current backend implementation is the authoritative source for implemented API and database behavior.

* * *

# 2\. Phase 1 — Assessment and Preparation

**Status: COMPLETED**

The initial environment and deployment requirements have been assessed.

This phase covered:

-   Home Assistant OS
-   Raspberry Pi deployment
-   Existing Home Assistant applications
-   PostgreSQL availability
-   Persistent application storage
-   Security requirements
-   ARM64 compatibility
-   Backend deployment requirements

No host-level Docker installation is required for the FoodStock Home Assistant deployment.

* * *

# 3\. Phase 2 — PostgreSQL

**Status: COMPLETED**

FoodStock uses PostgreSQL as its persistent relational database.

The current deployment uses the existing PostgreSQL/TimescaleDB Home Assistant environment.

The database is:

```text
Database: foodstock
```

PostgreSQL must remain private and must not be exposed directly to the Internet.

FoodStock connects to PostgreSQL through the backend. The mobile application does not connect to PostgreSQL directly.

```text
FoodStock-Mobile
       |
       v
FoodStock API
       |
       v
PostgreSQL
```

The database schema is defined by the application's SQLAlchemy models.

The current implementation initializes missing database tables using SQLAlchemy metadata. A versioned migration system such as Alembic is not currently part of the application.

* * *

# 4\. Phase 3 — FoodStock Backend

**Status: IMPLEMENTED**

The FoodStock backend is implemented using FastAPI and SQLAlchemy.

The backend provides:

-   Authentication
-   User management
-   Role-based authorization
-   Product management
-   Storage-location management
-   Inventory management
-   Inventory consumption
-   Inventory correction
-   Shopping-list management
-   Expiration information
-   Barcode lookup
-   Product image handling
-   Inventory transaction history
-   Dashboard data
-   AI prompt generation

The backend is the authoritative component for inventory business logic.

* * *

## 4.1 Authentication

JWT-based authentication is implemented.

Supported roles are:

```text
user
admin
```

The authentication endpoint is:

```http
POST /auth/token
```

Authenticated API requests use:

```http
Authorization: Bearer <token>
```

The backend performs authorization checks independently of the client application.

* * *

## 4.2 Database Model

The current database model is based on these core entities:

```text
User
StorageLocation
Product
Inventory
ShoppingList
Transaction
```

Inventory is quantity-based.

The application does not use a separate database row for every physical item.

An inventory record contains a quantity and can include:

-   Product
-   Quantity
-   Expiration date
-   Storage location
-   Status
-   Image information
-   User information
-   Timestamps

Inventory status is represented explicitly.

The current implementation also supports missing inventory, which allows calculated stock to become negative without storing negative quantities in individual inventory records.

* * *

## 4.3 Inventory Management

Implemented functionality includes:

-   Quantity-based inventory
-   Best-before dates
-   Storage locations
-   Inventory status
-   Negative calculated stock
-   Product stock targets
-   Inventory consumption
-   Inventory correction
-   Inventory transaction history

Inventory consumption uses:

**FEFO — First Expire, First Out**

The inventory record with the earliest applicable expiration date is selected first.

This is intentionally FEFO rather than FIFO.

* * *

## 4.4 Inventory Consumption

Inventory consumption is performed through the product-specific API:

```http
POST /products/{product_id}/consume
```

The backend determines which inventory records should be consumed.

The operation is performed server-side and uses database locking where required to prevent concurrent requests from consuming the same inventory incorrectly.

Consumption can result in missing stock when the requested quantity exceeds the available quantity.

* * *

## 4.5 Inventory Correction

Inventory corrections are performed through:

```http
POST /products/{product_id}/correct
```

Corrections use a quantity delta and a reason.

Example:

```json
{
  "quantity_delta": -2,
  "reason": "Damaged products"
}
```

Corrections are administrator-only operations.

Every inventory mutation should produce the appropriate transaction history.

* * *

## 4.6 Shopping List

The shopping list is integrated with product stock targets.

The system supports:

-   Minimum stock
-   Ideal stock
-   Automatic shopping-list calculation
-   Negative calculated stock
-   Shopping-list status management
-   Recalculation after inventory changes

The current API exposes:

```http
GET /shopping-list
PATCH /shopping-list/{product_id}
```

The shopping list is therefore not implemented as a separate generic item-management subsystem.

* * *

## 4.7 Expiration Overview

The backend provides:

```http
GET /expiring
```

The endpoint returns active inventory approaching or exceeding its expiration date.

The number of days can be specified through the `days` parameter.

The dashboard also provides expiration-related information grouped into useful categories such as:

-   Expired
-   Urgent
-   Soon
-   Upcoming

* * *

## 4.8 Barcode Lookup

Barcode lookup is implemented through:

```http
GET /scan/{barcode}
```

The backend first considers locally available product information and can use Open Food Facts for external product lookup.

External product information does not automatically mean that a permanent local product record has been created.

* * *

## 4.9 Product Images

Product images are stored outside PostgreSQL.

Persistent application data is stored below:

```text
/data/foodstock
```

Product image files are stored in the application's persistent data directory.

The database stores the corresponding file reference.

The product image API is:

```http
POST /products/{product_id}/image
```

Supported image formats are:

```text
image/jpeg
image/png
image/webp
```

The upload size is limited by the backend.

* * *

## 4.10 Transaction History

Inventory changes are recorded as transactions.

The current transaction history is exposed through:

```http
GET /transactions
```

Transaction records can contain information such as:

-   User
-   Product
-   Inventory record
-   Event
-   Quantity delta
-   Reason
-   Client operation ID
-   Creation timestamp

This is an inventory transaction history.

It is not currently a generic application-wide audit framework.

* * *

## 4.11 Idempotent Operations

Mutation requests support a client-generated:

```text
client_operation_id
```

This allows clients to safely retry operations without unintentionally applying the same inventory mutation multiple times.

This mechanism is particularly important for mobile clients and unreliable network connections.

* * *

## 4.12 Dashboard

The backend provides:

```http
GET /dashboard
```

The dashboard endpoint aggregates information required by the web/mobile user interface.

It includes inventory and expiration information as well as shopping-list information.

* * *

## 4.13 AI Prompt Generation

The backend provides:

```http
GET /ai/prompt
```

This generates a structured prompt based on the current inventory.

The feature does not require FoodStock to call a paid AI service.

The generated prompt can be copied to an external AI service by the user.

* * *

# 5\. Phase 4 — Web Interface

**Status: IMPLEMENTED**

FoodStock includes a web interface served by the backend.

The interface provides the core workflows required to operate FoodStock through a browser.

Current workflows include:

-   Login
-   Dashboard
-   Product management
-   Storage locations
-   Inventory intake
-   Inventory consumption
-   Inventory correction
-   Best-before-date management
-   Shopping list
-   Barcode lookup
-   AI prompt export

The web interface is intended to provide a usable administrative and household interface without requiring the mobile application.

* * *

# 6\. Phase 5 — Raspberry Pi Installation and Acceptance

**Status: PENDING ACCEPTANCE**

The backend implementation must be installed and validated on the target Raspberry Pi/Home Assistant environment before being considered operationally complete.

Acceptance testing should verify:

-   FoodStock starts correctly
-   PostgreSQL connectivity works
-   Authentication works
-   Authorization works
-   Database initialization works
-   Product operations work
-   Inventory operations work
-   FEFO consumption works
-   Shopping-list calculations work
-   Expiration information works
-   Barcode lookup works
-   Product image handling works
-   Transaction history works
-   Dashboard works
-   AI prompt generation works
-   Existing Home Assistant services remain operational

No production household inventory should be entered until the deployment has passed the required acceptance tests.

* * *

# 7\. Phase 6 — Backup and Recovery

**Status: PLANNED**

A complete backup strategy must be established before FoodStock is used with important household data.

Backups should include:

-   PostgreSQL data
-   `/data/foodstock`
-   Product images
-   Expiration images, if used
-   Relevant application configuration
-   Home Assistant configuration where required

At least one backup copy should be stored separately from the primary Raspberry Pi storage.

A backup is not considered valid until a restoration test has succeeded.

The restoration procedure should verify:

```text
PostgreSQL
     |
     v
FoodStock application data
     |
     v
Application startup
     |
     v
API health
     |
     v
Authentication
     |
     v
Inventory data
     |
     v
Images
```

The current application does not use Alembic migrations. Database recovery must therefore follow the current SQLAlchemy initialization model.

* * *

# 8\. Phase 7 — Secure Remote Access

**Status: PLANNED**

The initial remote-access strategy is based on private network access and/or VPN connectivity.

A possible architecture is:

```text
FoodStock-Mobile
       |
       v
WireGuard VPN
       |
       v
Home Network
       |
       v
FoodStock-Home
       |
       v
PostgreSQL
```

Requirements:

-   PostgreSQL must never be publicly accessible.
-   PostgreSQL must never be directly port-forwarded.
-   Remote access must use an authenticated and appropriately protected connection.
-   Only required services should be exposed.
-   Production remote API access must use appropriate transport security.

The exact VPN and TLS architecture remains a deployment decision.

* * *

# 9\. Phase 8 — FoodStock-Mobile

**Status: PLANNED / IN DEVELOPMENT**

FoodStock-Mobile is the planned native mobile client for FoodStock.

The mobile application must communicate exclusively with the FoodStock API.

It must never connect directly to PostgreSQL.

The planned core workflows are:

1.  Login
2.  Dashboard
3.  Barcode scanning
4.  Product lookup
5.  Product creation
6.  Best-before-date capture
7.  Inventory intake
8.  Inventory consumption
9.  Shopping list
10.  Expiration overview
11.  AI prompt export
12.  English/German localization

The mobile client must respect the backend authorization model.

Administrator-only functionality must not be treated as secure merely because it is hidden from the mobile UI.

* * *

# 10\. Phase 9 — Offline Support and Synchronization

**Status: PLANNED**

Offline operation is a future capability.

The planned architecture includes:

-   Local cache
-   Local operation queue
-   Retry handling
-   Client operation IDs
-   Server synchronization
-   Conflict handling
-   Recovery after connectivity loss

The backend remains authoritative for inventory mutations.

The mobile client must not independently calculate and permanently commit inventory state that conflicts with the server.

A future synchronization implementation should build on the existing `client_operation_id` mechanism rather than introducing an unrelated idempotency mechanism.

* * *

# 11\. Phase 10 — Advanced Mobile Features

**Status: FUTURE**

Potential mobile enhancements include:

-   Local OCR
-   Improved expiration-date recognition
-   Camera-assisted product entry
-   Improved barcode workflows
-   Offline-first operation
-   Push notifications
-   Advanced shopping workflows

These features should only be introduced when they provide a clear benefit without compromising the reliability of the core inventory system.

* * *

# 12\. Phase 11 — Home Assistant Integration

**Status: FUTURE**

Possible Home Assistant integrations include:

-   Home Assistant sensors
-   Home Assistant notifications
-   Home Assistant dashboard cards
-   Inventory-related automations
-   Low-stock notifications
-   Expiration notifications
-   Voice interaction

These features should remain optional.

The core FoodStock backend must remain usable independently of advanced Home Assistant integrations.

* * *

# 13\. Phase 12 — Optional AI Features

**Status: FUTURE**

The current application already provides AI prompt generation through:

```http
GET /ai/prompt
```

FoodStock does not currently require a paid AI provider.

Possible future enhancements include:

-   Direct AI provider integration
-   Recipe generation
-   Meal planning
-   Ingredient substitution
-   Household-specific recipe preferences
-   AI-assisted shopping suggestions

Direct AI integration must remain optional.

The core inventory system must not depend on an external AI service.

* * *

# 14\. Future Database Improvements

The following are potential future improvements:

-   Versioned database migrations
-   More advanced indexing
-   Database maintenance tooling
-   More detailed transaction reporting
-   Generic audit logging if required
-   Improved backup automation
-   Database health monitoring

These features must not be documented as current functionality until implemented.

* * *

# 15\. Release and Completion Principle

FoodStock development follows an incremental approach.

A phase is considered complete only when its acceptance criteria have been met.

The general process is:

```text
Implementation
      |
      v
Installation
      |
      v
Functional Testing
      |
      v
Regression Testing
      |
      v
Operational Validation
      |
      v
Phase Accepted
```

For infrastructure or data-related changes, backup and recovery validation must also be performed where applicable.

* * *

# 16\. Priority Order

The recommended development priority is:

```text
1. Raspberry Pi installation
2. Acceptance testing
3. Backup and recovery
4. Secure remote access
5. FoodStock-Mobile
6. Offline synchronization
7. Advanced mobile features
8. Home Assistant integrations
9. Optional AI features
```

The priority may change based on actual user requirements, deployment findings and acceptance-test results.

* * *

# 17\. Current Project Principle

The roadmap must always distinguish between:

```text
IMPLEMENTED
```

and:

```text
PLANNED
```

Implemented backend behavior must be documented from the current source code.

Planned features must not be presented as existing API endpoints, database tables, application functionality or deployment capabilities.

When the implementation changes, the corresponding documentation and roadmap status should be updated in the same development cycle.

The roadmap is therefore a planning document, not a substitute for the API, database or architecture documentation.
