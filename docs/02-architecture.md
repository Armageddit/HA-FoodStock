# Architecture

## Architectural Principles

### Backend as the source of truth

The backend owns:

-   authorization
-   inventory calculations
-   stock calculations
-   FEFO consumption
-   shopping-list calculations
-   transaction creation
-   idempotency handling

The client must not implement competing versions of these rules.

### Command-based inventory operations

Inventory changes are expressed as operations such as:

```text
add inventory
consume inventory
correct inventory
```

The client does not submit a calculated total stock value.

This reduces concurrency problems and keeps business logic centralized.

### Transactional database operations

Inventory mutations are executed inside database transactions.

Consumption uses row locking to protect active inventory entries from concurrent consumption.

### Idempotent client operations

Inventory mutation requests may contain a `client_operation_id`.

The backend stores this identifier on the transaction table and uses a unique constraint to prevent the same operation from being applied twice.

This is the current foundation for reliable mobile retries.

It is not yet a complete offline synchronization protocol.

## External Data

Open Food Facts is used only for barcode enrichment.

External product data is a suggestion.

Local product data remains authoritative.

## File Storage

Product images are stored outside PostgreSQL.

The current implementation stores them below the configured FoodStock data directory.

The database stores a relative image path.

A generic file-object abstraction is not currently implemented.

## Web Interface

The backend exposes a server-side web interface.

Current entry point:

```text
/ui/
```

The web interface provides access to the currently implemented backend functionality.

## API Versioning

The current API does not use an `/api/v1` prefix.

Existing clients must therefore use the actual routes documented in `05-api.md`.

Introducing versioned routes should be treated as a deliberate future API change rather than documented as an existing feature.
