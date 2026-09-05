# FoodStock Architecture

## 1\. High-Level Architecture

```text
                    ┌──────────────────────┐
                    │   FoodStock-Mobile   │
                    │      Android App     │
                    └──────────┬───────────┘
                               │
                         HTTPS / VPN
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FoodStock-Home    │
                    │ Home Assistant App   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  FoodStock Backend   │
                    │       FastAPI        │
                    └──────────┬───────────┘
                               │
                         PostgreSQL
                               │
                               ▼
                    ┌──────────────────────┐
                    │ PostgreSQL/Timescale │
                    │      foodstock       │
                    └──────────────────────┘
```

## 2\. Home Assistant Environment

FoodStock runs inside Home Assistant OS as a Home Assistant App.

The Raspberry Pi host must not be modified with a manually installed Docker environment.

Home Assistant OS remains responsible for:

-   Container runtime
-   App lifecycle
-   Networking
-   App storage
-   App security
-   Updates
-   Backups

## 3\. FoodStock-Home

FoodStock-Home is the deployment boundary.

Its responsibilities include:

-   Starting the backend
-   Providing persistent application storage
-   Connecting to PostgreSQL
-   Providing API access
-   Providing logs
-   Providing health checks
-   Managing application configuration
-   Future Home Assistant integration

The app should request the minimum Home Assistant permissions necessary.

Host networking should not be used unless a specific requirement is identified.

## 4\. Backend Technology

The backend uses:

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy 2
-   asyncpg
-   Alembic
-   PostgreSQL

Recommended internal structure:

```text
app/
├── main.py
├── api/
│   ├── router.py
│   ├── auth.py
│   ├── products.py
│   ├── inventory.py
│   ├── shopping_list.py
│   ├── storage_locations.py
│   ├── users.py
│   └── system.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── database.py
│
├── models/
│   ├── user.py
│   ├── product.py
│   ├── inventory.py
│   ├── storage_location.py
│   ├── shopping_list.py
│   └── audit.py
│
├── schemas/
│   ├── user.py
│   ├── product.py
│   ├── inventory.py
│   └── shopping_list.py
│
├── services/
│   ├── inventory_service.py
│   ├── shopping_list_service.py
│   ├── product_service.py
│   ├── barcode_service.py
│   └── expiration_service.py
│
└── migrations/
```

## 5\. Business Logic Boundary

Critical rules must exist in backend services.

Examples:

-   Inventory consumption
-   FEFO selection
-   Negative stock handling
-   Shopping quantity calculation
-   Expiration classification
-   Authorization
-   Audit events

FlutterFlow must not implement these rules independently.

## 6\. Database Boundary

Only the FoodStock Backend may connect to PostgreSQL.

FoodStock-Mobile must never receive:

-   PostgreSQL hostname
-   PostgreSQL username
-   PostgreSQL password
-   PostgreSQL connection string

## 7\. File Storage

Application files use the persistent FoodStock application storage.

Logical structure:

```text
/data/
├── app/
├── storage/
│   ├── products/
│   └── expiration-images/
├── exports/
├── backups/
└── logs/
```

The exact physical mapping will be finalized during Phase 3.

## 8\. PostgreSQL

The current PostgreSQL/TimescaleDB installation remains the database platform.

FoodStock uses standard PostgreSQL functionality.

Timescale-specific features are not required for the core application.

This reduces future migration complexity.

## 9\. Network Model

PostgreSQL:

-   Internal only
-   No public port
-   No direct mobile access

FoodStock API:

-   Internal LAN access
-   VPN access
-   HTTPS
-   Authentication required

Internet:

-   No direct PostgreSQL access
-   No direct backend access unless a later approved architecture explicitly requires it

## 10\. Home Assistant Integration

Home Assistant integration is optional for the initial release.

The architecture should later allow:

-   Sensors
-   Notifications
-   Dashboard cards
-   Automations
-   Voice queries

FoodStock should not become tightly coupled to Home Assistant APIs unless required.

## 11\. Offline Mobile Architecture

FoodStock-Mobile maintains a local cache.

The local layer contains:

-   Authentication state
-   Product cache
-   Storage locations
-   Relevant inventory data
-   Pending operations

Server synchronization is authoritative.

Inventory mutations are represented as operations rather than absolute quantity replacements.

## 12\. Concurrency

Example:

```text
Initial inventory = 5

Phone A consumes one
Phone B consumes one
```

Both operations must be sent as separate server-side transactions.

Correct result:

```text
5 -> 4 -> 3
```

Incorrect implementation:

```text
Phone A:
5 -> 4

Phone B:
5 -> 4

Final:
4
```

The backend therefore performs inventory mutation atomically.

## 13\. Scalability Target

The application is intentionally optimized for a small household rather than Internet-scale traffic.

The Raspberry Pi should comfortably support:

-   Several household users
-   Occasional simultaneous requests
-   Hundreds to thousands of products
-   Thousands of inventory units
-   Product images
-   Audit records

No unnecessary infrastructure should be introduced.
