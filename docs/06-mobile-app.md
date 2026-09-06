# Mobile Application

## Purpose

FoodStock-Mobile is the planned Android client for household inventory management.

The mobile application must use the FoodStock Backend as its source of truth.

## Responsibilities

The mobile client should handle:

-   camera barcode scanning
-   local OCR
-   UI state
-   local form validation
-   API communication
-   authentication token storage
-   user confirmation workflows

The backend handles:

-   inventory calculations
-   FEFO consumption
-   stock calculation
-   shopping-list calculation
-   authorization
-   persistence
-   transaction history

## Barcode Workflow

```text
Scan barcode
    |
    v
GET /scan/{barcode}
    |
    +-- local product found
    |       |
    |       v
    |    display product
    |
    +-- external suggestion
    |       |
    |       v
    |    ask user to confirm
    |
    +-- no result
            |
            v
        create product
```

## Inventory Intake

Recommended workflow:

```text
Select or scan product
        |
        v
Enter quantity
        |
        v
Select or confirm location
        |
        v
Capture or enter expiration date
        |
        v
User confirms
        |
        v
POST /inventory
```

## Consumption

The mobile client must send:

```text
product_id
quantity
```

It must not calculate which inventory entries are consumed.

The backend decides this using FEFO.

## Idempotency

For operations that may be retried, the client should generate a UUID and send it as `client_operation_id`.

The client must persist the operation ID until the server confirms the operation.

This is an idempotency mechanism.

It is not yet a complete offline synchronization protocol.

## OCR

OCR should run locally.

A recognized date is only a candidate until the user confirms it.

## Offline Operation

Offline-first operation is a planned mobile capability.

The current backend does not expose a synchronization endpoint.

The mobile application must therefore not assume that a generic `/sync` API exists.

Offline synchronization should be designed only after the command and conflict model has been formally specified.
