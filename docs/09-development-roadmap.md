# FoodStock Development Roadmap

## Phase 1 — Assessment and Preparation

Status:

```text
COMPLETED
```

Activities:

-   Home Assistant environment assessed
-   Existing apps reviewed
-   PostgreSQL strategy defined
-   FoodStock deployment model defined
-   Storage strategy planned
-   Security requirements defined

## Phase 2 — PostgreSQL

Status:

```text
COMPLETED
```

Current deployment:

```text
PostgreSQL/TimescaleDB App
PostgreSQL 17.6
Database: foodstock
```

Requirements achieved:

-   ARM64 support
-   Database operational
-   External PostgreSQL access disabled
-   pgAdmin4 available
-   Database connection verified

## Phase 3 — FoodStock Backend Preparation

Status:

```text
CURRENT
```

### Step 3.1

Define final FoodStock-Home structure.

### Step 3.2

Define backend directory structure.

### Step 3.3

Define configuration model.

### Step 3.4

Define database connection layer.

### Step 3.5

Introduce SQLAlchemy/Alembic structure.

### Step 3.6

Define persistent application storage.

### Step 3.7

Define logging.

### Step 3.8

Define health/readiness endpoints.

### Step 3.9

Verify PostgreSQL migrations.

### Step 3.10

Verify Home Assistant compatibility.

No mobile application work begins before Phase 3 is stable.

## Phase 4 — Database Schema

Implement:

-   Users
-   Roles
-   Products
-   Storage locations
-   Inventory units
-   Inventory transactions
-   Shopping list
-   Audit events
-   File objects

## Phase 5 — Authentication

Implement:

-   Login
-   Access tokens
-   Token refresh
-   User identity
-   Roles
-   Authorization

## Phase 6 — Product Management

Implement:

-   Product CRUD
-   Barcode lookup
-   Product images
-   Product activation/deactivation
-   Open Food Facts enrichment

## Phase 7 — Inventory

Implement:

-   Add inventory
-   Consume inventory
-   FEFO
-   Negative stock
-   Corrections
-   Transactions
-   Audit history

## Phase 8 — Shopping List

Implement:

-   Automatic calculation
-   Manual items
-   Purchase state
-   Inventory transfer
-   Automatic recalculation

## Phase 9 — Expiration

Implement:

-   Expired
-   Urgent
-   Soon
-   Upcoming
-   Configurable thresholds

## Phase 10 — FlutterFlow Foundation

Create FoodStock-Mobile.

Implement:

-   Theme
-   Navigation
-   Authentication
-   API connection
-   English localization
-   German localization

## Phase 11 — Barcode

Implement:

-   Camera
-   Barcode recognition
-   Local barcode processing
-   API lookup
-   Unknown-product workflow

## Phase 12 — OCR

Implement:

-   Expiration camera
-   Guide frame
-   Local ML Kit OCR
-   Date parser
-   Confidence/validation
-   User confirmation
-   Manual date selection

## Phase 13 — Offline Mode

Implement:

-   Local cache
-   Operation queue
-   Retry
-   Idempotency
-   Synchronization
-   Conflict handling

## Phase 14 — Recipe Export

Implement:

-   Expiring-food selection
-   Prompt generation
-   Clipboard export

## Phase 15 — Images

Implement:

-   Product images
-   Optional expiration images
-   Upload
-   Storage references
-   Image deletion

## Phase 16 — Administration

Implement:

-   Product administration
-   Inventory correction
-   Users
-   Storage locations
-   Stock targets
-   Audit history

## Phase 17 — Backup and Recovery

Implement and test:

-   Database backup
-   File backup
-   Configuration backup
-   Restore
-   Recovery documentation

## Phase 18 — Home Assistant Integration

Optional:

-   Expiring-food sensor
-   Shopping-list sensor
-   Inventory sensor
-   Notifications
-   Dashboard
-   Automations

## Phase 19 — Direct AI

Optional:

-   AI API
-   Recipe generation
-   Family preferences
-   Dietary preferences
-   Meal planning

## Release Strategy

Development releases:

```text
0.x
```

Initial stable release:

```text
1.0.0
```

Breaking API changes require a major version.

Database migrations must accompany schema changes.
