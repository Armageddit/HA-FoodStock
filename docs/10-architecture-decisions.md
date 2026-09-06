# Architecture Decisions

## ADR-001: PostgreSQL as the source of truth

**Decision:** PostgreSQL is the authoritative persistence layer.

**Reason:** FoodStock is a shared household application. Centralized persistence prevents conflicting client-side inventory state.

**Consequence:** Mobile clients must not write directly to the database.

## ADR-002: FastAPI backend

**Decision:** Use FastAPI for the FoodStock API.

**Reason:** It provides typed request/response models, OpenAPI documentation, authentication integration, and a small operational footprint.

## ADR-003: SQLAlchemy

**Decision:** Use SQLAlchemy 2 with synchronous database access.

**Reason:** The current application has a small workload and does not require an asynchronous database driver.

**Current driver:** `psycopg`.

`asyncpg` is not part of the current implementation.

## ADR-004: Enum-based roles

**Decision:** Store the user role as an application enum.

**Reason:** FoodStock currently has only two fixed roles.

A separate `roles` table would add complexity without a current functional benefit.

If dynamic permissions are required later, this decision can be revisited.

## ADR-005: Inventory entries instead of a single stock counter

**Decision:** Store inventory entries with quantity, expiration date, location, and status.

**Reason:** This allows FoodStock to perform FEFO consumption and retain meaningful stock history.

The current model represents batches/entries rather than strictly one database row per physical item.

## ADR-006: FEFO consumption

**Decision:** Consume stock using First Expire, First Out.

**Reason:** For food, expiration date is more important than simple insertion order.

Tie-breaking uses the inventory creation timestamp.

## ADR-007: Negative inventory

**Decision:** Negative stock is explicitly supported.

**Reason:** Real households may discover a shortage that was not previously recorded.

A `MISSING` inventory entry represents the shortage.

This avoids silently modifying a product-level stock counter.

## ADR-008: Transaction-based idempotency

**Decision:** Inventory mutation requests may include a client operation UUID.

**Reason:** Mobile clients may retry requests because of connectivity problems.

A unique database constraint prevents duplicate application of the same operation.

## ADR-009: External barcode enrichment

**Decision:** Open Food Facts is used as an optional enrichment source.

**Reason:** It provides useful product metadata without requiring FoodStock to maintain a global product catalog.

External data remains untrusted until accepted locally.

## ADR-010: Filesystem image storage

**Decision:** Product images are stored on the FoodStock filesystem.

**Reason:** Binary image data does not need to be stored in PostgreSQL for the current household use case.

The database stores the relative file path.

A generalized object-storage abstraction is deferred until it provides a real benefit.

## ADR-011: No API version prefix yet

**Decision:** The current API uses its existing route structure without `/api/v1`.

**Reason:** The current backend is an internal application and there are no established external API consumers.

If the API becomes a stable public or multi-client contract, versioning should be introduced deliberately.

## ADR-012: Offline synchronization is not yet part of the API

**Decision:** Do not document or implement a generic `/sync` endpoint yet.

**Reason:** Reliable synchronization requires an explicit command, conflict, retry, and reconciliation model.

The current `client_operation_id` mechanism provides idempotency but does not by itself constitute synchronization.

## Documentation Rule

Future architecture changes must update:

1.  implementation
2.  API contract
3.  database documentation
4.  architecture documentation
5.  mobile integration documentation
6.  roadmap/status

Documentation must never describe planned behavior as implemented behavior.

### Wichtigste Änderungen gegenüber den aktuellen Docs

Damit ist insbesondere Folgendes korrigiert:

-   **`asyncpg` → `psycopg`**
-   **keine erfundene Alembic-Infrastruktur**
-   **keine `roles`\-Tabelle**
-   **keine `audit_events`\-Tabelle**
-   **keine `file_objects`\-Tabelle**
-   **`inventory_units` → tatsächliches `inventory`\-Batch/Entry-Modell**
-   **FIFO → FEFO**
-   **`/api/v1/...` → tatsächliche aktuelle API-Routen**
-   **`/auth/login` → `/auth/token`**
-   **kein erfundener `/sync`\-Endpoint**
-   **kein Refresh-Token/Logout behauptet**
-   **`DELETE /products/{id}` korrekt als Deaktivierung beschrieben**
-   **`transactions` als tatsächliche Audit-/Historienquelle**
-   **Open Food Facts korrekt als externe, untrusted enrichment source**
-   **Offline Sync klar als Future Feature**
-   **Statusbegriffe zwischen „implemented“ und „production ready“ getrennt**
-   **technische Dokumentation vollständig auf Englisch**
-   **Architekturentscheidungen als ADRs formuliert**

Die API- und Datenbankteile sind dabei direkt am aktuellen Code ausgerichtet: Die vorhandenen Routen umfassen unter anderem `/auth/token`, `/users`, `/storage-locations`, `/products`, `/scan/{barcode}`, `/inventory`, `/products/{id}/consume`, `/products/{id}/correct`, `/expiring`, `/shopping-list` und `/transactions`; das Datenmodell besteht aktuell aus `users`, `storage_locations`, `products`, `inventory`, `shopping_list` und `transactions`. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub+4

**Eine Sache würde ich vor dem nächsten FlutterFlow-Schritt noch unbedingt machen:** `05-api.md` sollte danach als verbindlicher API-Vertrag gelten und wir sollten die Pydantic Request-/Response-Modelle im Code einmal gegen diese Dokumentation prüfen. Das verhindert, dass FlutterFlow anschließend gegen Felder baut, die die API tatsächlich anders nennt oder zurückgibt.
