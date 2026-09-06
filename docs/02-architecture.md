# FoodStock Architecture

Die Datei beschreibt aktuell eher ein **geplantes Zielbild** als die tatsächlich implementierte Architektur. Einige Teile sind weiterhin sinnvoll als Architekturprinzipien, aber mehrere technische Aussagen stimmen nicht mehr mit dem Repository überein. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub+2

## 1\. High-Level Architecture

Der grundsätzliche Aufbau ist richtig:

```text
FoodStock-Mobile
       ↓
FoodStock-Home
       ↓
FoodStock Backend
       ↓
PostgreSQL
```

Allerdings ist die Darstellung:

```text
FoodStock-Home
Home Assistant App
       ↓
FoodStock Backend
```

etwas irreführend.

**FoodStock-Home ist der Deployment-/Add-on-Rahmen**, während das eigentliche Backend die FastAPI-Anwendung unter `foodstock/app/` ist.

Ich würde das Diagramm eher so darstellen:

```text
┌──────────────────────┐
│   FoodStock-Mobile   │
│      Android App     │
└──────────┬───────────┘
           │
        HTTPS
           │
           ▼
┌──────────────────────┐
│    FoodStock-Home    │
│ Home Assistant App   │
│                      │
│  ┌────────────────┐  │
│  │ FoodStock API  │  │
│  │    FastAPI     │  │
│  └───────┬────────┘  │
└──────────┼───────────┘
           │
           ▼
┌──────────────────────┐
│      PostgreSQL      │
└──────────────────────┘
```

Damit ist klarer, dass FastAPI **innerhalb des FoodStock-Home-Kontexts** läuft.

* * *

# 2\. Home Assistant Environment

Dieser Abschnitt ist grundsätzlich okay.

Die Aussagen über Home Assistant OS als Runtime, Lifecycle, Storage usw. sind Architekturprinzipien und müssen nicht 1:1 im Python-Code auftauchen.

Eine Sache würde ich aber ändern:

> The Raspberry Pi host must not be modified with a manually installed Docker environment.

Das ist sehr spezifisch für eine bestimmte Deployment-Umgebung und gehört eher in die **Deployment-/Operations-Dokumentation** als in die allgemeine Architektur.

In `02-architecture.md` reicht:

> FoodStock-Home is designed to run as a Home Assistant application and uses the Home Assistant-managed container/runtime environment.

* * *

# 3\. FoodStock-Home

Der Abschnitt passt konzeptionell ziemlich gut.

Diese Punkte stimmen:

-   Starting the backend
-   Persistent application storage
-   PostgreSQL connection
-   API access
-   Logs
-   Health checks
-   Configuration

Allerdings ist:

> Future Home Assistant integration

kein Bestandteil der aktuellen Architektur und sollte als **Future** gekennzeichnet werden.

Außerdem würde ich die Aussage:

> Host networking should not be used unless a specific requirement is identified.

nicht löschen, aber eher als **deployment constraint** markieren.

* * *

# 4\. Backend Technology

Hier gibt es eine klare technische Abweichung.

Aktuell dokumentiert:

```text
asyncpg
Alembic
```

Das stimmt nicht mit dem aktuellen Code überein.

Der aktuelle Stack verwendet PostgreSQL über:

```text
psycopg
```

und die Datenbankinitialisierung erfolgt aktuell über SQLAlchemy `Base.metadata.create_all(...)`. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Es gibt derzeit **kein implementiertes Alembic-Migrationssystem**.

Daher:

```text
Python
FastAPI
Pydantic
SQLAlchemy
psycopg
PostgreSQL
```

statt:

```text
asyncpg
Alembic
```

Das ist eine der Stellen, die wir definitiv ändern müssen.

* * *

# 5\. Internal Backend Structure

Hier ist die Dokumentation aktuell **deutlich weiter als der Code**.

Die Doku beschreibt:

```text
app/
├── api/
├── core/
├── models/
├── schemas/
├── services/
└── migrations/
```

Der tatsächliche Code verwendet aber aktuell eine wesentlich flachere Struktur, unter anderem:

```text
foodstock/app/
├── main.py
├── models.py
├── database.py
├── schemas.py
└── ...
```

Der aktuelle `main.py` enthält einen großen Teil der API- und Business-Logik direkt. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Das bedeutet:

**Die aktuelle Dokumentation beschreibt eine Architektur, die noch nicht implementiert wurde.**

Ich würde hier nicht einfach die gewünschte modulare Architektur löschen.

Besser:

### Current structure

Dokumentieren, wie der Code **jetzt** aufgebaut ist.

### Target structure

Falls wir die Aufteilung in:

```text
api/
services/
models/
schemas/
```

weiterhin wollen, als geplante Refactoring-Struktur kennzeichnen.

Das verhindert, dass die Architektur-Doku den Entwickler über eine nicht existierende Verzeichnisstruktur täuscht.

* * *

# 6\. Business Logic Boundary

Dieser Abschnitt ist grundsätzlich sehr gut und sollte bleiben.

Besonders:

> FlutterFlow must not implement these rules independently.

Das ist wichtig für die Mobile-App.

Die Liste sollte aber an den tatsächlichen Code angepasst werden.

Aktuell sind tatsächlich serverseitig implementiert:

-   Inventory consumption
-   FEFO selection
-   Negative stock handling
-   Shopping-list updates
-   Expiration classification
-   Authorization
-   Transaction recording

G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub+1

Ich würde „Audit events“ durch **Transaction recording** ersetzen, weil es aktuell kein generisches Audit-Event-System gibt.

* * *

# 7\. Database Boundary

Dieser Abschnitt ist korrekt.

Die Mobile-App darf niemals direkt PostgreSQL verwenden.

Die Architektur:

```text
Mobile
  ↓
HTTP API
  ↓
PostgreSQL
```

ist richtig.

Die Aufzählung:

```text
PostgreSQL hostname
PostgreSQL username
PostgreSQL password
PostgreSQL connection string
```

kann bleiben.

* * *

# 8\. File Storage

Hier ist die Dokumentation wieder teilweise Zukunftsarchitektur.

Aktuell gibt es tatsächlich Anwendungsspeicher für Produkt-/Inventarbilder. Die Datenbank enthält dabei einen Pfad bzw. eine Referenz wie `image_path`. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Aber diese Struktur:

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

ist nicht vollständig als aktuelles Systemmodell belegt.

Insbesondere:

```text
exports/
backups/
logs/
```

sollten nicht als FoodStock-Dateispeicher dargestellt werden, wenn sie nicht tatsächlich vom Backend verwaltet werden.

Außerdem ist `expiration-images/` aktuell **nicht als vollständiger Feature-Workflow implementiert**.

Hier sollten wir zwischen:

```text
Current:
product images
inventory images
```

und:

```text
Future:
expiration image storage
exports
additional file management
```

unterscheiden.

* * *

# 9\. PostgreSQL / TimescaleDB

Hier sehe ich eine wichtige Unschärfe.

Die Doku sagt:

> PostgreSQL/TimescaleDB installation remains the database platform.

Der aktuelle FoodStock-Code benötigt aber **keine TimescaleDB-Funktionalität**. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub+1

Deshalb würde ich das klarer formulieren:

> FoodStock uses PostgreSQL as its database platform. No TimescaleDB-specific features are required by the current application.

Falls die Home-Assistant-Umgebung weiterhin eine TimescaleDB-Instanz bereitstellt, kann das als Deployment-Detail dokumentiert werden — aber **FoodStock selbst sollte PostgreSQL als Abhängigkeit nennen**.

* * *

# 10\. Network Model

Grundsätzlich richtig.

Ich würde aber eine Sache präzisieren:

Die aktuelle API ist nicht einfach pauschal „HTTPS only“. HTTPS hängt vom jeweiligen Deployment/Reverse Proxy ab.

Der Backend-Code selbst stellt FastAPI/Uvicorn bereit; TLS-Terminierung ist typischerweise eine Deployment-Frage. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Deshalb besser:

```text
FoodStock API:
- HTTP API exposed by the FoodStock-Home application
- HTTPS should be used for remote/mobile access
- Authentication required for protected endpoints
```

Und nicht so formulieren, als würde FastAPI selbst zwingend TLS terminieren.

* * *

# 11\. Offline Mobile Architecture

**Das ist aktuell der größte konzeptionelle Fehler in `02`.**

Die Doku behauptet:

> FoodStock-Mobile maintains a local cache.

mit:

```text
Authentication state
Product cache
Storage locations
Relevant inventory data
Pending operations
```

Das beschreibt eine **Mobile-Architektur**, die aus dem Backend-Repository nicht hervorgeht.

Was das Backend tatsächlich unterstützt, ist:

```text
client_operation_id
```

für idempotente Operationen bzw. Retries. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Das ist **nicht dasselbe wie eine Offline-First-App**.

Daher würde ich den Abschnitt umbenennen zu:

### Offline and Retry Strategy

und dann dokumentieren:

```text
The backend supports idempotent mutation requests through
client_operation_id.

A mobile client may retry the same operation using the same ID
without applying the operation multiple times.

A complete local database, offline cache, operation queue and
conflict-resolution system are not currently implemented by the
backend.
```

Wenn FoodStock-Mobile später Offline-First bekommt, kann dieser Abschnitt erweitert werden.

* * *

# 12\. Concurrency

Dieser Abschnitt ist **sehr wichtig und sollte bleiben**.

Das Beispiel:

```text
5
↓
4
↓
3
```

ist richtig.

Die aktuelle Implementierung verwendet bei der Inventory-Auswahl für Consumption Datenbank-Locking (`FOR UPDATE`). G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Das ist also nicht nur Architekturtheorie — das Backend setzt diesen Grundsatz tatsächlich um.

Ich würde lediglich ergänzen:

> Inventory mutations are executed within database transactions.

Und den Begriff „atomic“ behalten.

* * *

# 13\. Scalability Target

Hier gibt es zwei problematische Aussagen:

> Thousands of inventory units

Das alte Konzept von **individual inventory units** ist nicht mehr korrekt.

Das aktuelle Datenmodell verwendet Inventory Records mit `quantity`. G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fgithub.com&sz=128)GitHub

Daher:

❌

```text
Thousands of inventory units
```

besser:

```text
Hundreds to thousands of inventory records
```

Außerdem:

> Audit records

sollte zu:

> Transaction records

geändert werden.

* * *

# Gesamtbewertung von `02`

Ich würde die Datei nicht komplett umwerfen. Die **Architekturprinzipien sind gut**, aber wir müssen deutlich zwischen **Current Architecture** und **Target/Future Architecture** unterscheiden.

### 🔴 Muss korrigiert werden

-   `asyncpg` → `psycopg`
-   `Alembic` → aktuell nicht vorhanden
-   modulare `api/`, `services/`, `models/`\-Struktur → aktuell nicht vorhanden
-   `audit events` → aktuell `transactions`
-   „individual inventory units“ → aktuelles Modell arbeitet mit `quantity`
-   vollständige Offline-Mobile-Architektur → nicht implementiert
-   File-Storage-Struktur teilweise nur geplant
-   TimescaleDB nicht als FoodStock-Anforderung darstellen

### 🟠 Sollte präzisiert werden

-   FoodStock-Home vs. FastAPI Backend
-   HTTPS als Deployment-/Transport-Thema
-   Home-Assistant-Integration als Future
-   Scalability wording
-   File storage

### 🟢 Kann bleiben

-   Backend als Business-Logic-Grenze
-   Mobile → API → PostgreSQL
-   PostgreSQL nicht direkt für Mobile
-   serverseitige FEFO-Logik
-   atomare Inventory-Operationen
-   Concurrency-Konzept
-   Self-hosted/Home-Assistant-Grundarchitektur

## Wichtig für die Überarbeitung

Ich würde bei `02` **nicht** den Fehler von `00` wiederholen und eine komplett neue Architektur erfinden.

Die Datei sollte weiterhin die geplante Architektur dokumentieren dürfen. Wir markieren aber sauber:

```text
Current implementation
```

gegenüber:

```text
Target architecture
```

Das ist gerade bei der modularen Backend-Struktur sinnvoll. Sonst verlieren wir die Architekturentscheidung nur deshalb, weil der aktuelle `main.py` noch monolithischer ist.
