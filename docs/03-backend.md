# FoodStock Backend Specification

## 1\. Backend Stack

### Aktuelle Doku

Die Doku nennt unter anderem:

```text
FastAPI
SQLAlchemy
asyncpg
Alembic
Pydantic
PostgreSQL
```

### Tatsächlicher Stand

Der aktuelle Dependency-Stand verwendet:

```text
FastAPI
SQLAlchemy
psycopg[binary]
Pydantic
PostgreSQL
```

`asyncpg` ist aktuell nicht der verwendete PostgreSQL-Treiber. Die Datenbank-URL verwendet:

```text
postgresql+psycopg://
```

Das sollte unbedingt korrigiert werden.

* * *

# 2\. Alembic ist aktuell nicht implementiert

Das ist eine der deutlichsten Fehlerstellen.

Die Doku beschreibt:

> Alembic is used for database schema migrations.

Das stimmt derzeit nicht.

Der aktuelle Backend-Start verwendet:

```python
Base.metadata.create_all(engine)
```

Damit werden die Tabellen beim Start aus den SQLAlchemy-Modellen erzeugt. (github.com)

Es gibt aktuell kein funktionierendes Alembic-Migrationssystem, das wir als Teil der Backend-Architektur dokumentieren sollten.

### Änderung

Statt:

```text
Alembic is used for database schema migrations.
```

sollte dort stehen:

> The current implementation initializes the database schema using SQLAlchemy metadata during application startup. A dedicated migration framework such as Alembic is not currently implemented.

Falls Alembic später eingeführt wird, kann die Dokumentation dann entsprechend aktualisiert werden.

* * *

# 3\. Projektstruktur stimmt nicht

Die Doku beschreibt eine Struktur in Richtung:

```text
app/
├── api/
├── core/
├── models/
├── schemas/
├── services/
└── migrations/
```

Der tatsächliche aktuelle Code liegt wesentlich flacher:

```text
foodstock/
└── app/
    ├── main.py
    ├── models.py
    ├── database.py
    ├── schemas.py
    └── ...
```

Der größte Teil der Endpoints und Business-Logik befindet sich momentan in `main.py`. (github.com)

### Empfehlung

Nicht behaupten, dass die modulare Struktur bereits existiert.

Wenn wir sie weiterhin als Ziel wollen:

```text
Current structure
```

und separat:

```text
Target structure
```

Das hatten wir schon bei `02` — hier sollte die Backend-Doku konsistent sein.

* * *

# 4\. Application Startup

Der Startup-Ablauf in der Doku ist teilweise richtig, aber sollte genauer werden.

Aktuell passiert beim Start unter anderem:

```text
Create database engine
↓
Create database tables
↓
Create storage directories
↓
Initialize default storage locations
↓
Initialize initial admin
↓
Start FastAPI
```

Die Anwendung legt die benötigten Storage-Verzeichnisse an und initialisiert unter anderem Standard-Lagerorte. (github.com)

Außerdem wird ein initialer Admin-Account über die konfigurierten Environment-Variablen vorbereitet.

Das sollte in `03` explizit dokumentiert werden.

* * *

# 5\. Database Initialization

Die Doku spricht aktuell von:

> migrations are executed on startup

Das ist falsch.

Aktuell:

```text
SQLAlchemy Base.metadata.create_all()
```

Das bedeutet:

-   fehlende Tabellen werden erzeugt
-   bestehende Tabellen werden nicht über Migrationen versioniert
-   Schemaänderungen werden nicht automatisch als Migration ausgeführt

Das ist ein wichtiger Unterschied.

* * *

# 6\. Authentication

Die aktuelle Doku beschreibt ein komplexeres Auth-System, als tatsächlich vorhanden ist.

Aktuell existieren:

```text
POST /auth/token
GET /auth/me
```

Der Login verwendet OAuth2 Password Form und gibt einen JWT Access Token zurück. (github.com)

Es gibt aktuell **nicht**:

```text
/auth/login
/auth/refresh
/auth/logout
```

als separates API-Modell.

Insbesondere ein Refresh-Token-System ist derzeit nicht implementiert.

### Daher

Die Backend-Doku sollte beschreiben:

```text
User credentials
      ↓
POST /auth/token
      ↓
JWT access token
      ↓
Authorization: Bearer <token>
```

und nicht ein Login/Refresh/Logout-System dokumentieren, das es aktuell nicht gibt.

* * *

# 7\. Password Storage

Dieser Teil ist grundsätzlich korrekt.

Passwörter werden nicht im Klartext gespeichert.

Die aktuelle Implementierung verwendet einen Password-Hashing-Mechanismus über `pwdlib`/Argon2. (github.com)

Hier würde ich allerdings prüfen, ob die aktuelle Doku noch explizit **bcrypt** nennt.

Falls dort steht:

```text
bcrypt
```

muss das korrigiert werden.

Der aktuelle Code verwendet Argon2-basierte Password-Hashing-Unterstützung.

Das ist wichtig, weil wir bei Security-Dokumentation exakt sein sollten.

* * *

# 8\. Authorization

Das Prinzip der Doku ist korrekt:

> Authorization is enforced server-side.

Der aktuelle Code verwendet Role Checks für Admin-Funktionen. (github.com)

Die Doku sollte aber die tatsächlich vorhandenen Rollen nennen:

```text
user
admin
```

und keine zusätzliche Permission-/Role-Hierarchie suggerieren.

Es gibt aktuell kein komplexes RBAC-System.

* * *

# 9\. Product API

Der aktuelle Backend-Code unterstützt unter anderem:

```text
GET    /products
POST   /products
PATCH  /products/{product_id}
DELETE /products/{product_id}
```

sowie Barcode- und Bildfunktionen. (github.com)

Hier muss die Doku insbesondere prüfen, ob noch alte `/api/v1/...`\-Pfade verwendet werden.

Falls ja:

❌ entfernen.

Die aktuelle API verwendet keine solche `/api/v1`\-Prefix-Struktur.

* * *

# 10\. Inventory API

Die aktuelle Inventory-API ist ebenfalls anders als die alte Doku.

Relevant sind aktuell:

```text
POST /inventory
POST /products/{product_id}/consume
POST /products/{product_id}/correct
GET  /inventory
GET  /expiring
```

(github.com)

Die Backend-Doku sollte hier besonders deutlich machen:

### Add inventory

Erzeugt einen Inventory Record.

### Consume

Führt serverseitig FEFO aus.

### Correct

Korrigiert Bestand serverseitig.

### Inventory

Liefert den aktuell berechneten Bestand.

### Expiring

Liefert Ablauf-/MHD-relevante Bestände.

* * *

# 11\. Inventory Consumption

Dieser Abschnitt ist wichtig und sollte sehr detailliert bleiben.

Der Code macht nicht einfach:

```text
quantity -= requested_quantity
```

sondern:

```text
Find active inventory
↓
Sort by expiration date
↓
Lock selected rows
↓
Consume available quantity
↓
Create missing quantity if necessary
↓
Record transaction
↓
Update shopping list
↓
Commit
```

Das ist die tatsächliche Business-Logik. (github.com)

Das sollte in `03-backend.md` als zentraler Backend-Prozess dokumentiert werden.

* * *

# 12\. Idempotency

Die aktuelle Doku unterschätzt bzw. übersieht hier ein gutes Feature.

Der Code unterstützt:

```text
client_operation_id
```

bei Inventory-Mutationen.

Wenn dieselbe Operation erneut mit derselben ID gesendet wird, wird sie nicht noch einmal angewendet. (github.com)

Das sollte unbedingt in die Backend-Dokumentation.

Beispiel:

```text
Client
  |
  | operation_id = ABC
  v
Backend
  |
  ├── Operation not seen → execute
  |
  └── Operation already seen → ignore/reuse result
```

Das ist insbesondere für Mobile-Retries wichtig.

* * *

# 13\. Shopping List

Der aktuelle Code synchronisiert die Shopping List während relevanter Inventory-Operationen.

Die Doku sollte deshalb nicht behaupten, dass ein separater Scheduler oder Hintergrundjob die gesamte Liste kontinuierlich aktualisiert.

Aktuell ist die Logik eng an Inventory-Änderungen gekoppelt. (github.com)

* * *

# 14\. Barcode Lookup

Der Backend-Ablauf ist:

```text
GET /scan/{barcode}
```

Zuerst wird lokal gesucht.

Nur wenn kein lokales Produkt gefunden wird, wird Open Food Facts angefragt.

Das Ergebnis kann eine externe Produktsuggestion enthalten. (github.com)

Wichtig:

**Die Barcode-API legt das externe Produkt nicht automatisch als lokales Produkt an.**

Das sollte in `03` klar stehen.

* * *

# 15\. Product Images

Der aktuelle Upload:

```text
POST /products/{product_id}/image
```

ist vorhanden.

Die Implementierung:

-   akzeptiert JPEG
-   akzeptiert PNG
-   akzeptiert WebP
-   begrenzt die Uploadgröße
-   speichert die Datei im Application Storage
-   schreibt den Pfad in `image_path`

(github.com)

Die Doku sollte kein separates `file_objects`\-System voraussetzen.

* * *

# 16\. AI Prompt

Der aktuelle Backend-Endpoint:

```text
GET /ai/prompt
```

ist tatsächlich implementiert.

Die Funktion erstellt einen Prompt aus dem vorhandenen Inventory.

Der aktuelle Code berücksichtigt insbesondere Lebensmittel mit MHD innerhalb eines definierten Zeitraums und sortiert diese nach Ablaufdatum. (github.com)

Die Doku sollte daher klar zwischen:

```text
AI prompt generation
```

und:

```text
AI provider integration
```

unterscheiden.

Ersteres existiert.

Zweiteres nicht.

* * *

# 17\. Transactions

Der aktuelle Backend-Code schreibt Transaktionen bei Inventory-Operationen.

Die Doku sollte aber nicht von einem generischen Audit Framework sprechen.

Aktuelles Modell:

```text
Transaction
├── product_id
├── inventory_id
├── user_id
├── event
├── quantity_delta
├── reason
├── client_operation_id
└── created_at
```

(github.com)

Das ist eine **Inventory Transaction History**, keine universelle Audit Engine.

* * *

# 18\. Error Handling

Hier würde ich die aktuelle API stärker an den tatsächlichen HTTP-Responses ausrichten.

Beispielsweise werden unter anderem verwendet:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
413 Request Entity Too Large
```

je nach Fehlerfall. (github.com)

Falls `03-backend.md` derzeit eigene, nicht implementierte Fehlercodes definiert, sollten wir diese gegen den Code austauschen.

* * *

# 19\. Database Transactions

Dieser Abschnitt sollte unbedingt erhalten bleiben.

Die Inventory-Mutations sind transaktional.

Insbesondere:

```text
Consume
↓
Inventory changes
↓
Transaction record
↓
Shopping-list update
↓
Commit
```

sollten zusammen erfolgen.

Das verhindert einen Zustand, in dem beispielsweise Inventory verändert wurde, aber die zugehörige Transaction nicht geschrieben wurde.

* * *

# 20\. Was ich in `03` ändern würde

### 🔴 Definitiv korrigieren

-   `asyncpg` → `psycopg`
-   Alembic als aktuell vorhanden entfernen
-   aktuelle Projektstruktur dokumentieren
-   `/api/v1/...` entfernen, falls vorhanden
-   `/auth/login`, `/auth/refresh`, `/auth/logout` entfernen
-   JWT Access Token über `/auth/token` dokumentieren
-   Password hashing auf aktuellen Mechanismus korrigieren
-   `roles`/RBAC nicht übertreiben
-   `file_objects` entfernen
-   generisches Audit-System → Transactions
-   Inventory-API an aktuellen Code anpassen

### 🟠 Ergänzen

-   `client_operation_id`
-   Idempotency
-   `MISSING`\-Inventory
-   FEFO mit Row Locking
-   Shopping-List-Update bei Inventory-Operationen
-   tatsächlichen Startup-Prozess
-   AI Prompt Endpoint
-   tatsächliches Image Storage Verhalten

### 🟢 Beibehalten

-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Server-side business logic
-   Transactional inventory mutations
-   Backend authorization
-   Mobile → API → database boundary
