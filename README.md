# FoodStock

FoodStock is a private, self-hosted food inventory management system for households.

It is designed to manage food products, stock units, expiration dates, storage locations, shopping lists, and recipe-assistance workflows while keeping the data under the user's control.

## Goals

FoodStock is designed around the following principles:

-   Self-hosted operation
-   No mandatory cloud database
-   No Firebase dependency
-   Low recurring cost
-   Multiple household users
-   Secure remote access through VPN
-   Local barcode scanning
-   Local expiration-date OCR
-   Centralized server-side business logic
-   Reliable and auditable inventory transactions
-   English and German mobile application UI
-   English technical documentation
-   Long-term maintainability

## Architecture

FoodStock consists of two clearly separated applications.

### FoodStock-Home

`FoodStock-Home` is the Home Assistant App running on the household's Raspberry Pi.

It provides:

-   REST API
-   Authentication and authorization
-   Server-side business logic
-   PostgreSQL connectivity
-   Product management
-   Inventory management
-   Shopping-list management
-   Expiration-date calculations
-   Inventory transaction history
-   Product image storage
-   Web interface
-   Future Home Assistant integration

The backend is the only component that communicates directly with PostgreSQL.

### FoodStock-Mobile

`FoodStock-Mobile` is the Android application used by household members.

It is responsible for the user-facing mobile experience, including:

-   Barcode scanning
-   Product lookup
-   Product creation
-   Local expiration-date OCR
-   Inventory management
-   Expiration-date management
-   Shopping-list management
-   Offline-first operation
-   Synchronization with FoodStock-Home
-   Recipe prompt generation
-   English and German UI

Barcode recognition and OCR are performed locally on the Android device where possible.

## System Architecture

```text
┌─────────────────────┐
│   FoodStock-Mobile  │
│      Android       │
└──────────┬──────────┘
           │
           │ REST API
           │
           ▼
┌─────────────────────┐
│   FoodStock-Home    │
│    Home Assistant   │
│                     │
│  FastAPI Backend    │
│  Business Logic     │
│  Authentication     │
│  Web Interface      │
└──────────┬──────────┘
           │
           │ SQL
           │
           ▼
┌─────────────────────┐
│     PostgreSQL      │
└─────────────────────┘
```

The mobile application must never connect directly to PostgreSQL.

All business-critical operations are performed by the backend. This includes inventory changes, stock calculations, consumption ordering, shopping-list logic, and transaction recording.

## Inventory Model

FoodStock manages inventory as individual stock units associated with products and storage locations.

Each stock unit can contain information such as:

-   Quantity
-   Best-before date
-   Storage location
-   Stock status
-   Creation or intake information

### FEFO consumption

FoodStock uses **FEFO (First Expire, First Out)** for stock consumption.

When stock is consumed, units with the earliest best-before date are consumed first.

This is intentional: for food inventory, expiration date is more relevant than simple insertion order.

### Negative stock

FoodStock supports negative stock situations.

When consumption exceeds physically available stock, the missing quantity is represented explicitly rather than silently discarded.

This allows the system to preserve the difference between:

-   physically available stock
-   confirmed missing stock
-   historical inventory changes

All inventory-changing operations are recorded in the transaction history.

## Idempotent Operations

The backend supports client operation identifiers for inventory-changing requests.

This is important for the mobile application's offline-first architecture.

A mobile client may safely retry an operation after a network interruption without unintentionally applying the same inventory change twice.

The backend remains authoritative for the final inventory state.

## Database

FoodStock uses PostgreSQL as its central relational database.

The current Home Assistant installation uses the existing PostgreSQL/TimescaleDB App.

FoodStock does not currently depend on TimescaleDB-specific functionality.

The mobile application never accesses the database directly.

## Server

The initial target platform is:

-   Raspberry Pi 4
-   4 GB RAM
-   USB 3 SSD
-   Home Assistant OS
-   24/7 operation

FoodStock is designed to run alongside the existing Home Assistant installation without replacing or modifying the underlying Home Assistant OS environment.

FoodStock must not install a conventional Docker environment directly on the Home Assistant OS host.

## Network and Remote Access

The recommended initial deployment keeps FoodStock inside the home network.

Remote access is provided through VPN, for example:

```text
Android
   │
   │ WireGuard / FRITZ!Box VPN
   ▼
Home Network
   │
   ▼
Raspberry Pi
   │
   ▼
FoodStock-Home
```

PostgreSQL must never be exposed directly to the Internet.

For external mobile access beyond a trusted VPN environment, HTTPS should be provided through an appropriate reverse proxy or ingress layer.

## Web Interface

FoodStock-Home provides a web interface for administration and basic inventory operations.

The interface is available at:

```text
http://<home-assistant-ip>:8000/ui/
```

The current interface includes:

-   Login
-   Dashboard
-   Product management
-   Stock intake
-   Stock consumption
-   Expiration overview
-   Shopping list
-   AI prompt generation

The FastAPI documentation is available at:

```text
http://<home-assistant-ip>:8000/docs
```

The health endpoint is:

```text
http://<home-assistant-ip>:8000/health
```

## API

FoodStock-Mobile communicates with FoodStock-Home through the REST API.

The backend exposes functionality for:

-   Authentication
-   Products
-   Inventory
-   Storage locations
-   Shopping lists
-   Inventory transactions
-   Expiration information
-   Recipe-AI prompt generation

The API is the contract between FoodStock-Mobile and FoodStock-Home.

Business rules that must be enforced consistently are implemented on the server rather than relying on the mobile client.

The detailed API contract is documented separately in the project documentation.

## Current Status

### FoodStock-Home

The current development version is **1.0.2**.

Implemented functionality includes:

-   Home Assistant App for ARM64
-   FastAPI backend
-   PostgreSQL connectivity
-   JWT authentication
-   User and administrator roles
-   Product management
-   Inventory management
-   Storage locations
-   Shopping-list management
-   Inventory transaction history
-   FEFO stock consumption
-   Negative stock handling
-   Target and ideal stock-level logic
-   Automatic shopping-list generation
-   Expiration overview
-   Open Food Facts barcode lookup
-   Persistent product images
-   Web interface
-   Recipe-AI prompt generation

The current development focus is validation of the complete Home Assistant installation and end-to-end workflows on the target Raspberry Pi.

### FoodStock-Mobile

The Android application is the next major development phase.

The current mobile specification is documented in:

`KiPromptAndroidApp.md`

The planned mobile workflows include:

-   Login
-   Barcode scanning
-   Product lookup
-   Product creation
-   Expiration-date OCR
-   Inventory operations
-   Shopping-list management
-   Offline operation
-   Synchronization
-   Recipe assistance

## Validation

Before real household inventory data is entered, the installation should be validated with test data.

At minimum, the following workflows should be verified:

1.  Create a storage location.
2.  Create a product.
3.  Add multiple stock units with different best-before dates.
4.  Verify FEFO consumption.
5.  Verify negative stock handling.
6.  Verify transaction history.
7.  Verify automatic shopping-list generation.
8.  Verify expiration information.
9.  Verify product image storage.
10.  Verify authentication and authorization.

Database backups should also be tested by performing an actual restoration, not only by verifying that a backup file was created.

## Backup and Recovery

FoodStock data consists of both database data and persistent application files.

Backups should therefore cover:

-   PostgreSQL database
-   `/data/foodstock`

Backups should be stored on a separate storage target.

A backup is considered valid only after a restoration test has successfully recovered the required data.

## Documentation

Technical documentation is written in English.

The mobile application supports:

-   English
-   German

The application language is independent of the documentation language.

Project documentation covers architecture, requirements, backend implementation, database design, API behavior, security, operations, and architectural decisions.

## Development Principles

FoodStock is developed incrementally.

Changes should be implemented against the current architecture and documented behavior.

The backend remains authoritative for:

-   Inventory state
-   Inventory transactions
-   FEFO consumption
-   Authentication and authorization
-   Shopping-list calculations
-   Data validation
-   Idempotent inventory operations

The mobile application must not duplicate server-side business rules in a way that could result in conflicting inventory states.

## Roadmap

The following features are planned for future development:

-   Complete FoodStock-Mobile Android application
-   Robust offline synchronization
-   Optional storage of best-before-date photos
-   Home Assistant dashboard integration
-   Home Assistant notifications
-   Meal planning
-   Optional integration with external AI services
-   Additional reporting and inventory insights
-   Product groups and intelligent product equivalence

## Architectural Changes

The architecture defined by the project documentation is binding.

Fundamental architectural changes should be evaluated before implementation.

A proposed architectural change should document:

1.  What is changing
2.  Why the change is necessary
3.  Advantages
4.  Disadvantages
5.  Additional costs
6.  Migration impact

The goal is to keep FoodStock maintainable and predictable over the long term.
