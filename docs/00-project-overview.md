# FoodStock Project Overview

## 1\. Purpose

FoodStock is a self-hosted household food inventory management system.

It provides a central inventory shared by multiple household users and is designed to answer:

-   What food do we have?
-   Where is it stored?
-   How much is available?
-   What expires soon?
-   What has already expired?
-   What needs to be purchased?
-   What should be consumed first?
-   Which products are below their configured minimum stock?
-   Which foods can be used for recipe suggestions?

The backend is provided by the **FoodStock Backend** and is deployed as part of the **FoodStock-Home** Home Assistant application. The Android client is called **FoodStock-Mobile**.

## 2\. Project Goals

FoodStock is designed around the following goals:

-   Self-hosted operation
-   Household-owned data
-   PostgreSQL as the persistent database
-   Multiple authenticated users
-   User and administrator roles
-   Barcode-based product lookup
-   Local/mobile OCR for expiration dates
-   Inventory tracking with expiration dates
-   Storage-location management
-   Shopping-list management
-   FEFO-based consumption
-   Support for inventory shortages
-   Server-side inventory and shopping-list business logic
-   Optional integration with Open Food Facts for product lookup
-   Future integration with Home Assistant
-   Future direct AI integration

The system is intentionally designed for a private household rather than Internet-scale operation.

## 3\. Current Implementation

The current backend is implemented with:

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy
-   PostgreSQL
-   JWT-based authentication
-   bcrypt password hashing

The current application code is located primarily below:

```text
foodstock/
└── app/
    ├── main.py
    ├── models.py
    ├── database.py
    ├── schemas.py
    └── ...
```

The FastAPI application exposes authentication, user, product, storage-location, inventory, shopping-list, transaction, barcode and AI-prompt endpoints.

The backend also performs the critical inventory operations server-side, including inventory consumption and correction.

## 4\. Product and Inventory Model

A **product** represents reusable product information.

Examples of product information include:

-   Product name
-   Barcode
-   Manufacturer
-   Unit
-   Default storage location
-   Minimum stock
-   Ideal stock
-   Product image

A product does not represent a single physical item.

Physical stock is represented by records in the `inventory` table. An inventory record contains, among other fields:

-   Product
-   Quantity
-   Expiration date
-   Storage location
-   Status
-   Optional image path
-   User who added it
-   Creation timestamp
-   Consumption timestamp

The current implementation therefore supports quantities on inventory records. It does **not** require every physical item to have its own database row.

## 5\. Inventory Behavior

Inventory operations are handled by the backend.

Consumption uses **FEFO (First Expire, First Out)**. Inventory records are selected according to their expiration date, with the creation time used as an additional ordering criterion.

The client must not replace the complete inventory quantity based on stale locally cached data.

Instead, inventory changes are sent to the backend as explicit operations such as:

-   Add inventory
-   Consume inventory
-   Correct inventory

The backend performs the corresponding database operation.

Inventory records can also represent shortages. The current implementation uses the `missing` inventory status for stock that could not be fulfilled by the available inventory.

## 6\. Users and Roles

FoodStock currently supports two application roles:

### User

A normal user can:

-   Authenticate
-   View products
-   Add products
-   Add inventory
-   Consume inventory
-   Correct permitted inventory data
-   View inventory
-   View expiration information
-   Manage shopping-list state
-   Generate the available AI recipe prompt

### Administrator

An administrator has additional management permissions, including:

-   User management
-   Product management
-   Storage-location management
-   Product deactivation
-   Product restoration where supported
-   Administrative inventory corrections

Authorization is enforced by the backend.

The current implementation stores the role directly on the user record. Roles are not implemented as a separate database table.

## 7\. Barcode Processing

Barcode recognition is intended to take place on the mobile device.

The backend receives the barcode value and attempts to resolve it against the local product database.

If a local product is not available, the backend can use external product information sources such as Open Food Facts where supported.

External product information must not silently overwrite trusted local product information.

The user remains responsible for confirming imported product information before it becomes trusted local product data.

## 8\. Expiration Dates and OCR

Expiration-date OCR is a mobile/client-side concern.

The intended workflow is:

```text
Camera
  |
  v
Local OCR
  |
  v
Candidate expiration date
  |
  v
User confirmation
  |
  v
Backend
```

An OCR result must not be treated as a confirmed expiration date without user confirmation.

The current backend stores the confirmed expiration date on the inventory record.

Expiration images are not currently a general-purpose backend feature. Any future persistent expiration-image workflow must therefore be treated as a planned extension rather than as an existing capability.

## 9\. Product Images

Product images are supported by the backend.

The current implementation stores an image path/reference on the corresponding product or inventory record rather than storing binary image data directly in PostgreSQL.

The current implementation uses application storage for uploaded images.

A future dedicated file/object metadata model may be introduced if the application requires more advanced file management.

## 10\. Shopping List

The shopping list is based on product stock levels.

The intended stock rule is:

```text
current_stock < minimum_stock
```

When a product falls below its minimum stock, it can be represented on the shopping list.

If an ideal stock level is configured, the target purchase quantity is based on the ideal stock. Otherwise, the minimum stock is used.

Conceptually:

```text
if ideal_stock is configured:
    purchase_quantity = ideal_stock - current_stock
else:
    purchase_quantity = minimum_stock - current_stock
```

The backend is responsible for applying the relevant shopping-list logic.

The current shopping-list implementation supports explicit shopping-list states rather than treating the list as a simple boolean flag.

## 11\. Recipe / AI Prompt Support

The first AI-related feature does not require a direct AI service.

The backend can generate a structured recipe prompt based on the available food inventory.

The intended priority is:

1.  Food expiring soonest
2.  Other available food
3.  Minimal additional purchases

The generated prompt can then be copied or passed to an external AI service by the client.

Direct integration with an AI provider is a future feature.

## 12\. Home Assistant Integration

FoodStock-Home is designed to run as a Home Assistant application.

Home Assistant provides the deployment environment, lifecycle management and application storage.

A deeper Home Assistant integration is planned but is not required for the core inventory backend.

Future integration may provide:

-   Sensors
-   Notifications
-   Dashboard cards
-   Automations
-   Voice interaction

The core FoodStock backend should remain usable without tightly coupling its business logic to Home Assistant APIs.

## 13\. Privacy and Data Ownership

FoodStock is designed for household-controlled data.

The normal application architecture does not require a cloud database.

PostgreSQL is used as the backend database and should not be exposed directly to mobile clients.

Mobile clients communicate with the FoodStock Backend rather than connecting directly to PostgreSQL.

External services are only required for optional features such as external product-data lookup.

## 14\. Initial Non-Goals

The following features are not part of the current core implementation:

-   Direct paid AI API integration
-   Automatic meal planning
-   Advanced nutritional analysis
-   Public inventory sharing
-   Multi-household cloud synchronization
-   Direct Internet exposure of PostgreSQL
-   Complex Home Assistant dashboards
-   Fully automatic image recognition of food without a barcode
-   Persistent expiration-image management as a complete workflow
-   Dedicated offline synchronization infrastructure

These features may be introduced later without changing the basic purpose of FoodStock.

## 15\. Component Names

Component

Official Name

Home Assistant application

FoodStock-Home

Android application

FoodStock-Mobile

Backend

FoodStock Backend

Database

PostgreSQL

Repository

HA-FoodStock

## 16\. Language Policy

Technical documentation is written in English.

FoodStock-Mobile is intended to support:

-   English
-   German

The mobile application should normally follow the Android/device language while also allowing the user to select a language manually.

## 17\. Design Principles

### Server-side business logic

Critical business rules belong to the backend.

This includes:

-   Inventory mutations
-   FEFO consumption
-   Inventory shortage handling
-   Authorization
-   Shopping-list calculations
-   Data validation

The mobile application must not independently implement a conflicting version of these rules.

### Transactional inventory operations

Inventory changes are represented by explicit backend operations rather than blind quantity overwrites.

This is required to prevent stale-client updates from silently replacing concurrent changes.

### Minimal user interaction

The normal barcode and expiration-date workflow should require as few user interactions as practical while retaining explicit confirmation where data may be ambiguous.

### Safe automation

Automatically detected information, especially OCR results, must not silently become trusted inventory data.

### Privacy

Household inventory data should remain under the control of the household hosting the application.

## 18\. Documentation Status

This document describes the project at a high level.

Detailed implementation information is maintained separately:

-   `01-requirements.md` — functional requirements
-   `02-architecture.md` — system architecture
-   `03-backend.md` — backend implementation
-   `04-database.md` — database model
-   `05-api.md` — HTTP API
-   `06-mobile-app.md` — mobile application
-   `07-localization.md` — localization
-   `08-security-and-operations.md` — security and operation
-   `09-development-roadmap.md` — development roadmap
-   `10-architecture-decisions.md` — architecture decisions

When documentation conflicts with the implemented backend, the current implementation and its API/schema definitions are the source of truth until the documentation is updated.
