# Architecture Decisions

## ADR-001 — Self-Hosted Architecture

### Decision

FoodStock is self-hosted on a Raspberry Pi running Home Assistant OS.

### Reason

The primary goal is private household data ownership and minimal recurring cloud cost.

### Consequences

Positive:

-   Data remains under household control
-   No mandatory database cloud service
-   No Firebase dependency
-   Low recurring cost

Negative:

-   Backup responsibility
-   Hardware failure responsibility
-   Local network/VPN responsibility
-   Manual infrastructure maintenance

* * *

## ADR-002 — FoodStock-Home as Home Assistant App

### Decision

The backend is deployed as the Home Assistant App:

```text
FoodStock-Home
```

### Reason

The Raspberry Pi already runs Home Assistant OS.

Using the supported Home Assistant App model avoids manually modifying the Home Assistant OS host.

### Consequences

Positive:

-   Supervisor-managed lifecycle
-   Container isolation
-   App configuration
-   Home Assistant integration potential

Negative:

-   Home Assistant App constraints
-   Storage mapping must be designed carefully
-   Some conventional server patterns cannot be used directly

* * *

## ADR-003 — FastAPI Backend

### Decision

FoodStock Backend uses FastAPI.

### Reason

The current prototype already runs FastAPI successfully.

FastAPI provides validation and OpenAPI support and is lightweight enough for the target hardware.

### Consequences

Positive:

-   Existing prototype can be extended
-   Python ecosystem
-   Good API tooling
-   Async support
-   Low infrastructure complexity

Negative:

-   Some functionality requires custom Python code
-   Offline synchronization still requires explicit implementation

* * *

## ADR-004 — PostgreSQL

### Decision

PostgreSQL is the primary database.

### Reason

The project requires:

-   Transactions
-   Referential integrity
-   Concurrent updates
-   Relational data
-   Reliable migrations

### Consequences

PostgreSQL remains the authoritative data store.

* * *

## ADR-005 — TimescaleDB Compatibility

### Decision

The existing TimescaleDB installation remains in place.

FoodStock will initially use standard PostgreSQL functionality.

### Reason

The existing database is already operational.

FoodStock does not currently require time-series features.

### Consequence

The application remains portable without creating an immediate migration project.

* * *

## ADR-006 — Mobile Does Not Access PostgreSQL

### Decision

FoodStock-Mobile communicates exclusively with the FoodStock API.

### Reason

Direct database access would expose credentials and bypass business logic and authorization.

### Consequence

All business rules remain centralized.

* * *

## ADR-007 — Local Barcode Recognition

### Decision

Barcode recognition happens on the Android device.

### Reason

It reduces server load, improves responsiveness and works offline.

### Consequence

Only the barcode value is transmitted to the backend.

* * *

## ADR-008 — Local OCR

### Decision

Expiration-date OCR runs locally on the Android device.

### Reason

Expiration images are private and do not need to leave the phone.

### Consequence

OCR can work offline.

The user must confirm every OCR result.

* * *

## ADR-009 — Individual Inventory Units

### Decision

Products and physical inventory units are separate entities.

### Reason

Different physical units can have different expiration dates and locations.

### Consequence

FEFO can be implemented correctly.

* * *

## ADR-010 — Server-Side Inventory Transactions

### Decision

Inventory changes are server-side operations.

### Reason

Absolute client-side quantity updates cause race conditions.

### Consequence

Concurrent operations can be serialized transactionally.

* * *

## ADR-011 — No Mandatory AI API

### Decision

The initial recipe feature generates a prompt for external use.

### Reason

The basic application must remain free of mandatory AI API costs.

### Consequence

Recipe functionality works without an external AI provider.

* * *

## ADR-012 — English Documentation

### Decision

All technical documentation is English-only.

### Reason

English provides consistent terminology for APIs, source code, infrastructure and external technical documentation.

### Consequence

The mobile application can still be fully bilingual.

* * *

## ADR-013 — Two Explicit Application Names

### Decision

The applications are named:

```text
FoodStock-Home
FoodStock-Mobile
```

### Reason

This prevents confusion between the server-side Home Assistant App and the Android client.

### Consequence

All repositories, documentation, screenshots and UI references should use these names consistently.
