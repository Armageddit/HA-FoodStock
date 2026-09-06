# Development Roadmap

## Status Definitions

The project uses these status levels:

```text
PLANNED
IN DEVELOPMENT
IMPLEMENTED
LOCALLY TESTED
TARGET TESTED
ACCEPTANCE TESTED
PRODUCTION READY
```

`IMPLEMENTED` does not mean production ready.

## Current Backend

Implemented:

-   FastAPI backend
-   PostgreSQL integration
-   SQLAlchemy models
-   JWT authentication
-   user roles
-   product management
-   storage locations
-   inventory entries
-   FEFO consumption
-   negative inventory
-   shopping-list calculation
-   expiration queries
-   barcode lookup
-   product images
-   transaction history
-   recipe prompt generation
-   web UI

## Immediate Priorities

### 1\. Target installation test

Install the current FoodStock application on the target Home Assistant system.

Verify:

```text
/health
/docs
/ui/
```

### 2\. Functional acceptance test

Test:

-   administrator login
-   user creation
-   storage location creation
-   product creation
-   product image upload
-   inventory intake
-   inventory consumption
-   FEFO ordering
-   negative inventory
-   shopping-list generation
-   barcode lookup
-   transaction history

### 3\. Database migration strategy

Introduce Alembic before the database schema changes become frequent.

The migration system should support:

-   initial schema
-   forward migrations
-   upgrade verification
-   rollback strategy where practical

### 4\. API contract stabilization

Before FlutterFlow/mobile development depends on the API:

-   review all request models
-   review all response models
-   define stable error codes
-   define pagination strategy where required
-   define API versioning strategy

### 5\. Mobile application

Implement:

-   authentication
-   inventory display
-   product management
-   barcode scanning
-   inventory intake
-   consumption
-   expiration display
-   shopping list

### 6\. Offline synchronization

Design this separately.

The design must define:

-   operation IDs
-   retry behavior
-   ordering
-   conflict handling
-   server authority
-   client reconciliation
-   deleted/deactivated entities

Do not implement a generic sync endpoint before these rules are defined.

## Future Features

Possible future work:

-   direct AI provider integration
-   meal planning
-   expiration-date image retention
-   Home Assistant entities and automations
-   configurable expiration thresholds
-   richer audit history
-   generalized file storage
-   API versioning
-   structured request logging
