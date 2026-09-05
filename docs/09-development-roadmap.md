# FoodStock Development Roadmap

## Phase 1 — Assessment and Preparation

**Status: COMPLETED**

The Home Assistant OS environment, Raspberry Pi hardware, existing Home Assistant Apps, PostgreSQL strategy, storage requirements and security requirements were assessed.

No host-level Docker installation is used.

* * *

## Phase 2 — PostgreSQL

**Status: COMPLETED**

PostgreSQL is provided by the existing TimescaleDB Home Assistant App.

Current database environment:

-   PostgreSQL 17.6
-   TimescaleDB 5.4.2
-   Database: `foodstock`
-   ARM64 compatible
-   PostgreSQL is not exposed externally
-   pgAdmin4 is used for database administration

Database connectivity from FoodStock has been verified.

* * *

# Phase 3 — FoodStock Backend and Home Assistant Interface

**Status: IMPLEMENTED — RASPBERRY PI INSTALLATION AND ACCEPTANCE TESTING PENDING**

FoodStock-Home version:

```text
1.0.2
```

## Implemented Features

### Home Assistant App

FoodStock-Home is implemented as an ARM64-compatible Home Assistant App.

It contains the FoodStock Backend based on FastAPI.

### Database Connectivity

The backend can connect to PostgreSQL.

The Android/mobile application does not access PostgreSQL directly.

### Authentication

JWT authentication is implemented.

Supported roles:

-   User
-   Administrator

Authorization is enforced by the backend.

### Database

The relational database contains the core entities required for the application, including:

-   Users
-   Roles
-   Products
-   Individual inventory units
-   Storage locations
-   Shopping-list data
-   Inventory/change history

### Inventory

Implemented:

-   Individual inventory units
-   Best-before dates
-   Storage locations
-   Negative stock
-   Centralized stock-target logic
-   Consumption according to earliest best-before date

The consumption strategy should technically be referred to as:

**FEFO — First Expire, First Out**

rather than FIFO, because the ordering criterion is the best-before date.

### Shopping List

Implemented:

-   Automatic shopping-list generation
-   Minimum stock handling
-   Ideal stock handling
-   Negative stock calculation
-   Automatic recalculation after inventory changes

### Expiration Overview

Implemented:

-   Expired items
-   Items approaching their best-before date
-   Inventory-based expiration overview

### Barcode Lookup

Barcode lookup is implemented through Open Food Facts.

The barcode is used to retrieve product information.

### Product Images

Product images are stored outside PostgreSQL.

Persistent application storage is located below:

```text
/data/foodstock
```

The database stores references to the relevant files.

### Web Interface

FoodStock-Home provides a Home Assistant-compatible web interface:

```text
http://<home-assistant-ip>:8000/ui/
```

The current interface includes:

-   Login
-   Dashboard
-   Stock intake
-   Inventory consumption
-   Best-before-date management
-   Shopping list
-   Copy for AI

### AI Prompt Export

The endpoint:

```http
GET /ai/prompt
```

generates a structured recipe prompt from the current inventory.

The feature does not require a paid AI API.

### FlutterFlow Specification

The FlutterFlow Android application specification is documented in:

```text
KiPromptAndroidApp.md
```

This document is the development specification for FoodStock-Mobile.

* * *

# Phase 3 Acceptance Testing

The implementation must now be installed and tested on the Raspberry Pi.

No real household inventory should be entered before the acceptance tests have passed.

## Test 1 — Home Assistant App Installation

Install or update:

```text
FoodStock-Home 1.0.2
```

Verify:

-   App starts successfully
-   No Home Assistant errors are introduced
-   Existing Home Assistant Apps continue operating
-   FoodStock logs show normal startup

## Test 2 — Configuration

Configure:

-   PostgreSQL credentials
-   Dedicated JWT secret
-   Initial administrator account

Secrets must not be committed to Git.

## Test 3 — Health Endpoint

Verify:

```http
GET /health
```

Expected result:

```text
HTTP 200
```

The response must indicate that the application is healthy.

## Test 4 — API Documentation

Open:

```text
/docs
```

Verify that the FastAPI OpenAPI documentation loads successfully.

## Test 5 — Web Interface

Open:

```text
/ui/
```

Verify:

-   Login works
-   Dashboard loads
-   No database errors are displayed

## Test 6 — Storage Location

Create:

```text
Test Location
```

Verify that the location is persisted.

## Test 7 — Product

Create a test product.

Example:

```text
Name:
Test Tomato Sauce

Barcode:
TEST-0001

Minimum stock:
2

Ideal stock:
5
```

Verify that the product can be retrieved again.

## Test 8 — Inventory Unit

Create an inventory unit with a known best-before date.

Example:

```text
Product:
Test Tomato Sauce

Best-before date:
2026-09-20

Quantity:
1
```

Verify that the inventory unit is persisted.

## Test 9 — FEFO Consumption

Create several inventory units with different best-before dates.

Example:

```text
2026-09-20
2026-09-15
2026-10-01
```

Consume one unit.

Expected result:

```text
2026-09-15
```

must be consumed first.

## Test 10 — Shopping List

Example:

```text
Current stock:
1

Minimum stock:
2

Ideal stock:
5
```

Expected shopping quantity:

```text
5 - 1 = 4
```

Verify that the shopping list contains four units.

## Test 11 — Negative Stock

Consume more units than physically available.

Example:

```text
Current stock:
0

Consume:
1
```

Expected:

```text
Current stock:
-1
```

Verify that the shopping-list calculation handles the negative quantity correctly.

## Test 12 — Audit History

Perform:

-   Add inventory
-   Consume inventory
-   Correct inventory

Verify that the corresponding events are recorded with:

-   User
-   Timestamp
-   Event type
-   Affected entity
-   Relevant quantity/change

## Test 13 — Existing Home Assistant Installation

After all tests, verify that:

-   Home Assistant remains operational
-   Existing Apps remain operational
-   PostgreSQL remains operational
-   Zigbee2MQTT remains operational
-   Other previously operational services remain operational

Only after all acceptance tests pass is Phase 3 considered operationally complete.

* * *

# Phase 4 — Backup and Recovery

**Status: NOT STARTED**

Before real household data is entered, configure:

-   PostgreSQL backups
-   `/data/foodstock` backups
-   Home Assistant configuration backup
-   Secondary backup storage

A restoration test is mandatory.

The backup process is considered incomplete until a test restoration succeeds.

* * *

# Phase 5 — Secure Remote Access

**Status: NOT STARTED**

Initial remote-access architecture:

```text
FoodStock-Mobile
       |
       v
WireGuard VPN
       |
       v
FRITZ!Box
       |
       v
Home Network
       |
       v
FoodStock-Home
```

Requirements:

-   No public PostgreSQL access
-   No direct PostgreSQL port forwarding
-   VPN authentication required
-   Only required services accessible

Before distributing the external version of FoodStock-Mobile, HTTPS must be configured appropriately.

* * *

# Phase 6 — FoodStock-Mobile

**Status: NOT STARTED**

FoodStock-Mobile will be implemented with FlutterFlow.

The development specification is:

```text
KiPromptAndroidApp.md
```

Initial workflows:

1.  Login
2.  Dashboard
3.  Barcode scanning
4.  Product lookup
5.  Product creation
6.  Local OCR
7.  Best-before-date confirmation
8.  Inventory intake
9.  Inventory consumption
10.  Shopping list
11.  Expiration overview
12.  Copy for AI
13.  English/German localization

* * *

# Phase 7 — Offline Synchronization

**Status: PLANNED**

Implement:

-   Local cache
-   Local operation queue
-   Retry
-   Idempotency
-   Server synchronization
-   Conflict handling

Inventory mutations must remain server-authoritative.

* * *

# Phase 8 — Optional Features

Possible future extensions:

-   Stored best-before-date photographs
-   Direct paid AI integration
-   Meal planning
-   Home Assistant sensors
-   Home Assistant notifications
-   Home Assistant dashboard
-   Voice interaction

These features must not be allowed to complicate the initial stable application unnecessarily.

* * *

# Release Principle

The project should progress in controlled increments.

A phase is not considered complete merely because the code exists.

For infrastructure phases, completion requires:

```text
Implementation
     ↓
Installation
     ↓
Functional test
     ↓
Regression test
     ↓
Backup verification where applicable
     ↓
Phase accepted
```

Real household data should only be entered after the corresponding phase has passed its acceptance criteria.
