# Architecture Decisions

This document records the major architectural decisions made for FoodStock.

Architecture decisions describe the intended structure of the system and the reasoning behind it. They should be updated when an existing decision is deliberately changed or superseded.

The current implementation is the authoritative reference for implemented behavior.

* * *

## ADR-001 — Self-Hosted Architecture

### Status

**Accepted**

### Decision

FoodStock is designed as a self-hosted household application.

The primary deployment target is a Raspberry Pi running Home Assistant OS.

### Reason

The primary goals are:

-   Household data ownership
-   Privacy
-   Low recurring cost
-   No mandatory cloud infrastructure
-   Reliable operation within the home network

### Consequences

#### Positive

-   Data remains under household control
-   No mandatory cloud database
-   No mandatory Firebase dependency
-   Low recurring infrastructure cost
-   Works within an existing Home Assistant environment

#### Negative

-   Backup responsibility remains with the operator
-   Hardware failures must be handled locally
-   Network and VPN configuration remain deployment responsibilities
-   Updates and infrastructure maintenance require local administration

* * *

## ADR-002 — FoodStock-Home as a Home Assistant App

### Status

**Accepted**

### Decision

The backend is deployed as the Home Assistant application:

```text
FoodStock-Home
```

### Reason

The target environment already runs Home Assistant OS.

Using the Home Assistant App model avoids modifying the Home Assistant host directly and allows Home Assistant to manage the application's lifecycle.

### Consequences

#### Positive

-   Supervisor-managed lifecycle
-   Container isolation
-   Persistent application storage
-   Home Assistant integration potential
-   Consistent deployment model

#### Negative

-   Home Assistant App restrictions apply
-   Storage mappings must be designed carefully
-   Host-level server administration is intentionally limited
-   Conventional Docker/server deployment patterns may not apply directly

* * *

## ADR-003 — FastAPI Backend

### Status

**Accepted**

### Decision

FoodStock uses FastAPI as its backend framework.

### Reason

FastAPI provides:

-   Request validation
-   OpenAPI generation
-   Type-safe API definitions
-   Good Python ecosystem integration
-   Low infrastructure complexity
-   Suitable performance for the target hardware

The existing backend was already implemented using FastAPI, making continued use preferable to introducing a different framework.

### Consequences

#### Positive

-   Existing backend can be extended
-   Automatic API documentation
-   Pydantic-based validation
-   Straightforward Python integration
-   Lightweight deployment

#### Negative

-   Business logic must be implemented explicitly
-   Authentication and authorization require application-level implementation
-   Offline synchronization requires explicit design and implementation

* * *

## ADR-004 — PostgreSQL as the Authoritative Database

### Status

**Accepted**

### Decision

PostgreSQL is the primary and authoritative persistent database for FoodStock.

The backend communicates with PostgreSQL through SQLAlchemy.

### Reason

FoodStock requires:

-   Relational data
-   Referential integrity
-   Database transactions
-   Concurrent updates
-   Row-level locking for critical inventory operations
-   Reliable persistence

### Consequences

#### Positive

-   Strong relational consistency
-   Transaction support
-   Concurrent access support
-   Mature database technology
-   Good SQLAlchemy integration

#### Negative

-   Requires a separate database service
-   Requires database backup procedures
-   Requires database monitoring and maintenance
-   PostgreSQL must be protected from direct external access

### Migration Note

The current implementation does **not** use Alembic or another versioned migration framework.

Database tables are currently initialized using SQLAlchemy metadata.

Future introduction of a migration system would require a separate architectural decision.

* * *

## ADR-005 — TimescaleDB Compatibility

### Status

**Accepted**

### Decision

FoodStock remains compatible with the existing PostgreSQL/TimescaleDB environment.

FoodStock currently uses standard PostgreSQL functionality.

### Reason

The target Home Assistant environment may already provide PostgreSQL through a TimescaleDB installation.

FoodStock does not currently require TimescaleDB-specific time-series functionality.

### Consequences

-   The existing PostgreSQL/TimescaleDB installation can be reused.
-   FoodStock remains largely portable to standard PostgreSQL.
-   No TimescaleDB-specific schema is required.
-   Introducing time-series functionality in the future would require a separate architectural decision.

* * *

## ADR-006 — Mobile Does Not Access PostgreSQL

### Status

**Accepted**

### Decision

FoodStock-Mobile communicates exclusively with the FoodStock API.

The mobile application must never connect directly to PostgreSQL.

```text
FoodStock-Mobile
       |
       | HTTP(S) API
       v
FoodStock Backend
       |
       | SQLAlchemy
       v
PostgreSQL
```

### Reason

Direct database access from the mobile application would:

-   Expose database credentials
-   Bypass authorization
-   Bypass validation
-   Bypass business rules
-   Make schema changes harder
-   Increase the attack surface

### Consequences

All business rules remain centralized in the backend.

The mobile application sends commands and requests data through the API.

The mobile client must not send calculated replacement stock values to the server.

* * *

## ADR-007 — Barcode Processing

### Status

**Accepted**

### Decision

Barcode scanning and barcode lookup are separate concerns.

The client may perform barcode recognition locally using the device camera.

The backend is responsible for resolving the resulting barcode value.

The current backend provides:

```http
GET /scan/{barcode}
```

### Reason

Keeping camera-based barcode recognition on the device:

-   Reduces server processing
-   Improves responsiveness
-   Allows recognition to work without an active API connection
-   Keeps the backend independent of camera hardware

Only the resulting barcode value needs to be sent to the backend for product lookup.

### Consequences

The architecture separates:

```text
Camera
   |
   v
Barcode recognition
   |
   v
Barcode value
   |
   v
FoodStock API
   |
   v
Local / external product lookup
```

The backend remains responsible for product lookup and product data.

* * *

## ADR-008 — Local Expiration-Date OCR

### Status

**Planned**

### Decision

Expiration-date OCR is intended to run locally on the Android device.

### Reason

Expiration-date images may contain private household information and generally do not need to be uploaded to a server for recognition.

Local OCR can also provide:

-   Lower latency
-   Offline operation
-   Reduced server processing
-   Better privacy

### Consequences

The planned mobile workflow is:

```text
Camera
   |
   v
Local OCR
   |
   v
Detected date
   |
   v
User confirmation
   |
   v
FoodStock API
```

The user must confirm OCR results before they are used for inventory data.

This decision does not imply that local OCR is currently implemented in the backend.

* * *

## ADR-009 — Quantity-Based Inventory Records

### Status

**Accepted — Supersedes the previous individual-unit design**

### Decision

FoodStock represents inventory using quantity-based inventory records.

The current database model is:

```text
Product
   |
   +-- Inventory
```

An `Inventory` record contains a quantity rather than representing exactly one physical item.

For example:

```text
Product: Milk
Quantity: 5
Expiration: 2026-09-20
Location: Refrigerator
```

is represented by one inventory record with:

```text
quantity = 5
```

### Reason

The current application model is designed around quantities while still allowing inventory batches to differ by:

-   Expiration date
-   Storage location
-   Status
-   Image
-   Creation information

Multiple inventory records can therefore exist for the same product.

For example:

```text
Milk
├── Inventory #1
│   quantity = 3
│   expiration = 2026-09-10
│   location = Refrigerator
│
└── Inventory #2
    quantity = 5
    expiration = 2026-09-20
    location = Pantry
```

This preserves the information required for FEFO consumption without requiring one database row per physical item.

### Consequences

#### Positive

-   Smaller database representation
-   Simple quantity management
-   Different expiration dates remain possible
-   Different storage locations remain possible
-   FEFO remains possible
-   Inventory operations remain transactional

#### Negative

-   Individual physical items are not separately identified
-   Item-level tracking is not available
-   Future item-level tracking would require a new model or architectural decision

### Important Stock Rule

Individual inventory quantities are not used to represent negative quantities.

A confirmed shortfall can instead be represented using the `missing` inventory status.

This allows calculated stock to become negative while individual inventory quantities remain non-negative.

* * *

## ADR-010 — Server-Side Inventory Transactions

### Status

**Accepted**

### Decision

Inventory changes are performed by the FoodStock backend.

Clients send commands such as:

```text
consume
correct
add inventory
```

rather than sending a calculated replacement stock value.

### Reason

Client-side quantity calculations can produce race conditions.

For example:

```text
Client A reads stock = 5
Client B reads stock = 5

Client A consumes 2
Client B consumes 3
```

If both clients independently calculate a replacement value, one update can overwrite the other.

The backend can instead perform the operation transactionally.

### Consequences

-   Inventory changes are centralized
-   Business rules remain server-side
-   Concurrent operations can be controlled transactionally
-   Database locking can be used where necessary
-   Transaction history can be generated consistently

* * *

## ADR-011 — FEFO Inventory Consumption

### Status

**Accepted**

### Decision

Inventory consumption uses FEFO:

**First Expire, First Out**

When multiple active inventory records exist for the same product, records with the earliest applicable expiration date are consumed first.

### Reason

FoodStock manages household food and should preferentially consume products that expire sooner.

### Consequences

The backend must consider inventory expiration dates when processing consumption requests.

The mobile client must not implement its own independent FEFO algorithm.

The backend remains authoritative.

* * *

## ADR-012 — Idempotent Inventory Operations

### Status

**Accepted**

### Decision

Inventory mutation requests support a client-generated:

```text
client_operation_id
```

The transaction table enforces uniqueness for this operation identifier.

### Reason

Mobile clients operate over networks where requests can fail after reaching the server.

Without idempotency, a retry could apply the same inventory operation twice.

### Consequences

A client can safely retry a supported mutation using the same operation ID.

The backend can detect that the operation has already been processed.

This mechanism is especially important for future offline and unreliable-network support.

* * *

## ADR-013 — No Mandatory AI Provider

### Status

**Accepted**

### Decision

FoodStock does not require a paid or external AI provider for its core functionality.

The backend can generate an AI prompt from current inventory data.

The current API provides:

```http
GET /ai/prompt
```

### Reason

The basic application should remain usable without:

-   AI API credentials
-   Subscription fees
-   External AI availability
-   Mandatory cloud services

### Consequences

Users can copy the generated prompt to an external AI service of their choice.

Future direct AI integrations may be added as optional functionality.

Core inventory functionality must remain independent of AI services.

* * *

## ADR-014 — English Technical Documentation

### Status

**Accepted**

### Decision

All technical project documentation is written in English.

This includes:

-   Architecture documentation
-   API documentation
-   Database documentation
-   Security documentation
-   Development documentation
-   Architecture Decision Records

### Reason

English provides consistent terminology for:

-   Source code
-   APIs
-   Infrastructure
-   Frameworks
-   Libraries
-   External technical documentation

### Consequences

The application itself may support multiple user-facing languages.

Technical documentation remains English-only.

* * *

## ADR-015 — Explicit Application Names

### Status

**Accepted**

### Decision

The two main application components use the following names:

```text
FoodStock-Home
FoodStock-Mobile
```

### Meaning

**FoodStock-Home**

The server-side application running in the Home Assistant environment.

**FoodStock-Mobile**

The client application used on mobile devices.

### Reason

Using explicit names prevents confusion between the backend and mobile client.

### Consequences

Repositories, documentation, configuration, screenshots and UI references should use these names consistently.

* * *

## ADR-016 — Backend Is the Source of Truth

### Status

**Accepted**

### Decision

The FoodStock backend and PostgreSQL database are authoritative for persistent inventory state.

The mobile client is a consumer of that state and sends commands to modify it.

### Reason

Inventory state must remain consistent across:

-   Multiple mobile clients
-   Web clients
-   Concurrent users
-   Future offline clients
-   Home Assistant integrations

Allowing clients to independently become authoritative would create synchronization and consistency problems.

### Consequences

The client should:

-   Request current state from the backend
-   Send explicit commands
-   Use `client_operation_id` for retryable mutations
-   Never directly modify database state
-   Never directly access PostgreSQL

The backend should:

-   Validate commands
-   Apply business rules
-   Perform transactional updates
-   Record inventory transactions
-   Return the resulting state

* * *

## ADR-017 — Authentication and Authorization Are Backend Responsibilities

### Status

**Accepted**

### Decision

Authentication and authorization are enforced by the FoodStock backend.

The current authentication mechanism uses JWT access tokens.

The current application roles are:

```text
user
admin
```

### Reason

Client-side authorization is insufficient because clients can be modified or bypassed.

The backend must therefore independently validate:

-   Token validity
-   Token expiration
-   User identity
-   User active status
-   Administrator privileges where required

### Consequences

The mobile and web applications may hide functionality that the current user cannot access, but this is only a usability measure.

It is not a security boundary.

* * *

## ADR-018 — Persistent Files Are Stored Outside PostgreSQL

### Status

**Accepted**

### Decision

Binary application files such as product images are stored in the FoodStock persistent filesystem rather than directly inside PostgreSQL.

The database stores the corresponding file path/reference.

The application data directory is configurable and defaults to:

```text
/data/foodstock
```

### Reason

Storing image files separately:

-   Keeps PostgreSQL focused on relational data
-   Avoids unnecessarily large database records
-   Simplifies file handling
-   Allows filesystem-level backup of binary data

### Consequences

Database backups alone are not sufficient to restore a complete FoodStock installation.

Backups must also include the relevant FoodStock filesystem data.

* * *

## ADR-019 — Home Assistant Is the Deployment Boundary

### Status

**Accepted**

### Decision

FoodStock is designed to operate inside the Home Assistant environment rather than modifying the underlying Home Assistant OS directly.

### Reason

The target platform is Home Assistant OS.

Using the Home Assistant application boundary provides:

-   Isolation
-   Lifecycle management
-   Persistent storage configuration
-   Controlled resource usage
-   Easier installation and removal

### Consequences

FoodStock should not require:

-   Host-level Docker administration
-   Host-level package installation
-   Direct host filesystem manipulation
-   Unnecessary privileged access

Deployment-specific security settings remain the responsibility of the Home Assistant configuration.

* * *

# Superseded Decisions

## Superseded ADR — Individual Inventory Units

The previous architecture described inventory as individual physical units:

```text
Product
   |
   +-- Inventory Unit
   +-- Inventory Unit
   +-- Inventory Unit
```

This decision is no longer valid.

It has been replaced by **ADR-009 — Quantity-Based Inventory Records**.

The current architecture is:

```text
Product
   |
   +-- Inventory Record
           quantity = N
           expiration_date = ...
           storage_location = ...
```

Multiple inventory records can still represent different batches, expiration dates or locations.

The previous decision must not be used as the basis for new implementation work.

* * *

# Decision Maintenance

Architecture decisions should be reviewed whenever the implementation changes substantially.

In particular, changes involving:

-   Database structure
-   Authentication
-   API architecture
-   Mobile synchronization
-   Offline operation
-   Storage
-   Deployment
-   External services
-   AI integration

should result in a review of the relevant ADR.

A new architectural decision should be added when an existing decision is deliberately changed rather than silently changing the documentation.

The repository code remains the authoritative source for currently implemented behavior.
