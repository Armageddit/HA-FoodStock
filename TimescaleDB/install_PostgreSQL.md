# FoodStock – Installation und Konfiguration von PostgreSQL / TimescaleDB und pgAdmin4

## Zweck

Dieses Dokument beschreibt die Installation und Konfiguration der PostgreSQL-Datenbank für das Projekt **FoodStock** auf einem Raspberry Pi 4 mit Home Assistant OS.

Die Anleitung dokumentiert den tatsächlich verwendeten Aufbau und die gewählten Einstellungen, damit die Installation später reproduziert oder nach einem Fehler wiederhergestellt werden kann.

---

# 1. Systemumgebung

## Hardware

- Raspberry Pi 4
- RAM: 4 GB
- USB-3.0-SSD
- SSD ist der einzige angeschlossene Speicher
- keine SD-Karte
- Home Assistant läuft 24/7

## Home Assistant

Zum Zeitpunkt der Installation:

```text
Home Assistant Core:       2026.9.0
Home Assistant Supervisor: 2026.08.0
Home Assistant OS:        18.2
Architektur:              aarch64 / raspberrypi4-64
```

# 2\. Vorhandene Home-Assistant-Apps

Zum Zeitpunkt der Einrichtung waren bereits mehrere Apps/Add-ons vorhanden.

Unter anderem:

-   ESPHome Device Builder
-   Mosquitto broker
-   motionEye
-   Node-RED
-   Samba NAS
-   Samba NAS2-β
-   Samba share
-   Solarflow Control
-   Studio Code Server
-   Terminal & SSH
-   Zigbee2MQTT

Einige Apps waren bewusst gestoppt und laufen nur bei Bedarf.

## Ziel

Die vorhandene Home-Assistant-Installation sollte möglichst nicht verändert oder gefährdet werden.

Deshalb wurde ausdrücklich NICHT:

-   Docker manuell auf dem Host installiert
-   ein normales Linux-Docker-System eingerichtet
-   PostgreSQL außerhalb von Home Assistant installiert
-   der Home-Assistant-OS-Host manuell verändert
-   PostgreSQL direkt aus dem Internet erreichbar gemacht

PostgreSQL wird als Home-Assistant-App/Add-on betrieben.

* * *

# 3\. PostgreSQL-Variante

Für FoodStock wird die Home-Assistant-App:

```text
TimescaleDB
```

des Projekts:

```text
Expaso / hassos-addon-timescaledb
```

verwendet.

Repository:

```text
https://github.com/expaso/hassos-addon-timescaledb
```

Zum Zeitpunkt der Einrichtung:

```text
Add-on / App Version: 5.4.2
PostgreSQL:            17.6
TimescaleDB:           2.22.1
PostGIS:               3.6.0
TimescaleDB Toolkit:   1.21.0
pgAgent:               4.2.3
```

Die Datenbank wird für FoodStock als normale PostgreSQL-Datenbank verwendet.

TimescaleDB-Funktionen werden für FoodStock derzeit nicht benötigt.

* * *

# 4\. Warum TimescaleDB verwendet wird

FoodStock benötigt zunächst nur eine normale relationale PostgreSQL-Datenbank.

TimescaleDB bietet zusätzlich Erweiterungen für Zeitreihendaten.

Für die eigentliche FoodStock-Datenbank werden diese Funktionen zunächst nicht benötigt.

Der Vorteil der gewählten App ist jedoch:

-   aktuelle PostgreSQL-Version
-   ARM64-Unterstützung
-   Home-Assistant-App
-   persistenter Speicher über `/data`
-   Backup-Unterstützung
-   später mögliche Nutzung von TimescaleDB
-   keine zusätzliche manuelle Docker-Installation erforderlich

FoodStock verwendet die Datenbank zunächst wie normales PostgreSQL.

* * *

# 5\. Repository hinzufügen

In Home Assistant:

```text
Einstellungen
→ Apps
→ App-Store / Apps
→ ⋮
→ Repositories
```

Das Expaso-Repository hinzufügen, falls noch nicht vorhanden:

```text
https://github.com/expaso/hassos-addon-timescaledb
```

Danach sollte die TimescaleDB-App im App-Store erscheinen.

* * *

# 6\. TimescaleDB installieren

In Home Assistant:

```text
Einstellungen
→ Apps
→ TimescaleDB
```

Die App installieren.

Vor der Installation wurde ein vollständiges Home-Assistant-Backup erstellt.

Das Backup wurde zusätzlich auf einem separaten Netzwerklaufwerk gespeichert.

## Warum?

Die SSD des Raspberry Pi ist der einzige lokale Speicher.

Bei einem Defekt der SSD wären ohne externes Backup sämtliche Daten gefährdet.

Daher:

```text
Raspberry Pi SSD
      ↓
Home-Assistant-Backup
      ↓
separates Netzwerklaufwerk
```

* * *

# 7\. TimescaleDB-Konfiguration

Verwendete Konfiguration:

```yaml
databases:
  - foodstock

timescale_enabled: []

timescaledb:
  telemetry: "off"
  maxmemory: "512MB"
  maxcpus: "2"

max_connections: 25

system_packages: []

init_commands: []
```

Falls die tatsächliche App-Oberfläche die Werte anders darstellt, müssen die entsprechenden Felder sinngemäß gesetzt werden.

* * *

# 8\. Begründung der TimescaleDB-Einstellungen

## 8.1 Datenbank

```yaml
databases:
  - foodstock
```

Die Datenbank `foodstock` wird automatisch angelegt.

Damit ist die eigentliche FoodStock-Datenbank von der Home-Assistant-Datenbank getrennt.

FoodStock greift später ausschließlich auf:

```text
foodstock
```

zu.

* * *

# 9\. TimescaleDB-Erweiterung

Verwendet wurde:

```yaml
timescale_enabled: []
```

## Grund

FoodStock benötigt aktuell keine TimescaleDB-Zeitreihenfunktionen.

Die Anwendung ist eine klassische relationale Datenbankanwendung mit:

-   Produkten
-   Beständen
-   Lagerorten
-   Benutzern
-   Einkaufsliste
-   Transaktionen
-   Änderungshistorie

Daher wird die TimescaleDB-Erweiterung für die `foodstock`\-Datenbank derzeit nicht aktiviert.

Sollte später eine sinnvolle Verwendung für Zeitreihen entstehen, kann dies separat geprüft werden.

* * *

# 10\. Telemetrie

Verwendet:

```yaml
telemetry: "off"
```

## Grund

FoodStock benötigt keine TimescaleDB-Telemetrie.

Da das Projekt möglichst privat und selbst gehostet betrieben werden soll, wird die Telemetrie deaktiviert.

* * *

# 11\. PostgreSQL-RAM-Begrenzung

Verwendet:

```yaml
maxmemory: "512MB"
```

## Grund

Der Raspberry Pi besitzt:

```text
4 GB RAM
```

Zum Zeitpunkt der Installation waren ungefähr:

```text
2 GB RAM frei
```

FoodStock ist keine große Datenbankanwendung.

Zu hohe PostgreSQL-Speicherlimits wären daher unnötig.

Die Begrenzung auf:

```text
512 MB
```

lässt ausreichend RAM für:

-   Home Assistant
-   Supervisor
-   Node-RED
-   Mosquitto
-   Zigbee2MQTT
-   weitere Apps
-   FoodStock Backend
-   Betriebssystem

Damit wird verhindert, dass PostgreSQL unnötig viele Ressourcen beansprucht.

* * *

# 12\. PostgreSQL-CPU-Begrenzung

Verwendet:

```yaml
maxcpus: "2"
```

## Grund

Der Raspberry Pi 4 besitzt vier CPU-Kerne.

FoodStock benötigt keine hohe Datenbank-Rechenleistung.

Die Begrenzung auf zwei CPU-Kerne lässt bewusst Ressourcen für:

-   Home Assistant
-   vorhandene Apps
-   FoodStock Backend
-   andere Systemaufgaben

Die Datenbank soll nicht unnötig die gesamte CPU beanspruchen.

* * *

# 13\. Maximale PostgreSQL-Verbindungen

Verwendet:

```yaml
max_connections: 25
```

## Grund

FoodStock ist eine private Familienanwendung.

Es werden voraussichtlich nur wenige Benutzer und Geräte gleichzeitig auf die API zugreifen.

25 Verbindungen sind für die Anwendung mehr als ausreichend.

Eine unnötig hohe Anzahl an PostgreSQL-Verbindungen würde zusätzlichen RAM-Verbrauch verursachen.

* * *

# 14\. System Packages

Verwendet:

```yaml
system_packages: []
```

## Grund

FoodStock benötigt keine zusätzlichen Alpine-Linux-Pakete für PostgreSQL.

Deshalb werden keine zusätzlichen Pakete installiert.

Das reduziert:

-   Installationsaufwand
-   Startzeit
-   Wartungsaufwand
-   potenzielle Fehlerquellen

* * *

# 15\. Init Commands

Verwendet:

```yaml
init_commands: []
```

## Grund

Es sind keine manuellen Änderungen an der PostgreSQL-Konfiguration erforderlich.

Insbesondere wird nicht versucht, die PostgreSQL-Konfigurationsdateien außerhalb der vorgesehenen App-Konfiguration zu verändern.

* * *

# 16\. PostgreSQL-Port

Die TimescaleDB-App verwendet intern:

```text
5432/tcp
```

Der Port wurde NICHT als öffentlich benötigter PostgreSQL-Zugang eingerichtet.

## Wichtig

FoodStock soll später:

```text
FoodStock Backend
       ↓
PostgreSQL
```

intern verwenden.

Die Android-App darf niemals direkt auf PostgreSQL zugreifen.

Die geplante Architektur lautet:

```text
Android
   ↓
HTTPS / VPN
   ↓
FoodStock Backend
   ↓
PostgreSQL
```

## Kein direkter PostgreSQL-Zugriff

Nicht konfigurieren:

```text
Internet → 5432 → PostgreSQL
```

und möglichst auch nicht unnötig:

```text
LAN → 5432 → PostgreSQL
```

Die Datenbank ist ausschließlich für Backend-Zugriffe vorgesehen.

* * *

# 17\. Kontrolle des TimescaleDB-Starts

Nach der Installation wurde TimescaleDB gestartet.

Der Start verlief erfolgreich.

Wichtige Meldungen:

```text
starting PostgreSQL 17.6
```

und:

```text
database system is ready to accept connections
```

sowie:

```text
TimescaleDb is running!
```

Außerdem wurde automatisch die Datenbank angelegt:

```text
Create database if not exist: 'foodstock'
CREATE DATABASE
```

Damit war die Datenbank erfolgreich verfügbar.

* * *

# 18\. Tatsächlich verwendete App-ID

Die TimescaleDB-App wurde über folgende Home-Assistant-App-ID gefunden:

```text
77b2833f_timescaledb
```

Die interne Kommunikation verwendet:

```text
77b2833f-timescaledb
```

Port:

```text
5432
```

Damit kann eine andere Home-Assistant-App später intern auf PostgreSQL zugreifen.

Beispiel:

```text
Host:
77b2833f-timescaledb

Port:
5432
```

* * *

# 19\. pgAdmin4

Zur einfachen Verwaltung der PostgreSQL-Datenbank wurde zusätzlich:

```text
pgAdmin 4
```

installiert.

Repository:

```text
https://github.com/Expaso/hassos-addon-pgadmin4
```

pgAdmin dient ausschließlich als Verwaltungswerkzeug.

FoodStock selbst benötigt pgAdmin nicht.

* * *

# 20\. pgAdmin-Konfiguration

Verwendete Konfiguration:

```yaml
ssl: true
certfile: fullchain.pem
keyfile: privkey.pem
system_packages: []
init_commands: []
leave_front_door_open: false
```

* * *

# 21\. SSL in pgAdmin

Verwendet:

```yaml
ssl: true
```

mit:

```yaml
certfile: fullchain.pem
keyfile: privkey.pem
```

## Grund

Die Weboberfläche von pgAdmin soll nicht unnötig unverschlüsselt betrieben werden.

Die vorhandenen Home-Assistant-Zertifikatsdateien werden verwendet.

* * *

# 22\. `leave_front_door_open`

Verwendet:

```yaml
leave_front_door_open: false
```

## Grund

Die Option soll verhindern, dass pgAdmin bewusst ohne Schutz direkt geöffnet wird.

Wichtig:

Bei der tatsächlich installierten App-Version wurde trotzdem beobachtet, dass die pgAdmin-Oberfläche direkt geöffnet wurde.

Daher wird diese Option NICHT als alleinige Sicherheitsgrenze betrachtet.

pgAdmin ist ein Verwaltungswerkzeug und darf nicht als Schutzmechanismus für PostgreSQL angesehen werden.

Die eigentliche PostgreSQL-Sicherheit wird über:

-   PostgreSQL-Rollen
-   Passwörter
-   Netzwerkbegrenzung
-   FoodStock-Backend
-   VPN

realisiert.

* * *

# 23\. Verbindung von pgAdmin zu PostgreSQL

In pgAdmin wurde ein Server registriert:

```text
Name:
FoodStock PostgreSQL
```

Verbindung:

```text
Host:
77b2833f-timescaledb

Port:
5432

Maintenance database:
postgres
```

* * *

# 24\. PostgreSQL-Administrator

Standardmäßig stellte die TimescaleDB-App das Konto bereit:

```text
Username:
postgres

Initial password:
homeassistant
```

Dieses Standardpasswort wurde NICHT dauerhaft verwendet.

* * *

# 25\. `postgres`\-Passwort ändern

Das Passwort des Administratorkontos wurde über pgAdmin geändert.

Das neue Passwort wird aus Sicherheitsgründen NICHT in dieser Dokumentation gespeichert.

Login/Group Roles -> rechtsklick auf postgres -> properties -> Definitions

Platzhalter:

```text
<POSTGRES_ADMIN_PASSWORT>
```

## Wichtig

Das Passwort muss in einem Passwortmanager gespeichert werden.

Nicht:

-   in Git
-   in dieser Markdown-Datei
-   in der Android-App
-   im FoodStock-Frontend

speichern.

* * *

# 26\. FoodStock-Datenbankbenutzer

Für die Anwendung wurde ein separater Benutzer erstellt:

## 1\. Login/Group Roles öffnen

In pgAdmin links:

**Servers**  
→ **FoodStock PostgreSQL**  
→ **Login/Group Roles**

Dann:

**Rechtsklick → Create → Login/Group Role**

* * *

## 2\. General

Bei **Name** eintragen:

```text
foodstock_app
```

* * *

## 3\. Definition

Wechsle zu:

**Definition**

Bei **Password**:

Erzeuge wieder ein **eigenes starkes Passwort**.

Beispielsweise mindestens:

```text
20 Zeichen
Großbuchstaben
Kleinbuchstaben
Zahlen
Sonderzeichen
```

⚠️ **Das Beispielpasswort nicht verwenden.**

Speichere dieses Passwort in deinem Passwortmanager. Wir benötigen es später für das FoodStock-Backend.

* * *

## 4\. Privileges

Wechsle zu:

**Privileges**

Stelle sicher:

Einstellung

Wert

Can login?

**Yes**

Superuser?

**No**

Create databases?

**No**

Create roles?

**No**

Inherit rights from parent roles?

**Yes**

Falls pgAdmin weitere Optionen zeigt, **nichts Zusätzliches aktivieren**.

Die Rolle soll lediglich ein normaler Login-Benutzer sein.

* * *

## 5\. Speichern

Klicke:

**Save**

Danach sollte unter

**Login/Group Roles**

stehen:

```text
foodstock_app
postgres
```

## Grund

Das FoodStock-Backend soll niemals mit dem PostgreSQL-Superuser `postgres` arbeiten.

Prinzip:

```text
postgres
   ↓
Administration

foodstock_app
   ↓
FoodStock Backend
```

Dadurch wird das Risiko reduziert, dass ein Fehler im Backend zu vollständigem Datenbankzugriff führt.

* * *

# 27\. Eigenschaften von `foodstock_app`

Der Benutzer wurde als normaler Login-Benutzer angelegt.

Wichtige Eigenschaften:

```text
Can login:       Yes
Superuser:       No
Create database: No
Create roles:    No
```

Das Backend benötigt keine administrativen PostgreSQL-Rechte.

* * *

# 28\. Datenbank-Owner

Gehe zu:

**Databases → foodstock**

Rechtsklick:

**Properties**

und öffne **General**.

Dort gibt es das Feld:

**Owner**

Ursprünglich gehörte die Datenbank dem Benutzer:

```text
postgres
```

Der Owner wurde geändert zu:

```text
foodstock_app
```

Endzustand:

```text
foodstock
└── Owner: foodstock_app
```

Damit gehört die eigentliche FoodStock-Datenbank dem Benutzer, der sie für die Anwendung verwendet.

* * *

# 29\. Funktionstest

Die Verbindung wurde zunächst als:

```text
postgres
```

getestet.

Danach wurde die Verbindung als:

```text
foodstock_app
```

getestet.

In pgAdmin:

    Links Servers
    Rechtsklick auf FoodStock PostgreSQL
    Properties
    Tab Connection

Ändere dort nur:

Username

von:

postgres

auf:

foodstock_app

Beim Passwort:

DEIN_PASSWORT_VON_FOODSTOCK_APP

eintragen.

Die übrigen Werte bleiben:

Host: 77b2833f-timescaledb
Port: 5432
Maintenance database: postgres

Dann Save bzw. Verbindung testen.
Erwartetes Ergebnis

Die Verbindung sollte funktionieren.

* * *

# 30\. SQL-Funktionstest

Wir prüfen, ob `foodstock_app` tatsächlich **in der Datenbank `foodstock` arbeiten kann**.

Das geht direkt über pgAdmin.

### 1\. Wieder mit `foodstock_app` verbinden

Das hast du bereits erfolgreich gemacht.

### 2\. Links öffnen

```text
Servers
└── FoodStock PostgreSQL
    └── Databases
        └── foodstock
```

Rechtsklick auf **foodstock** → **Query Tool**

### 3\. Folgenden Test eingeben

```sql
SELECT
    current_database() AS database_name,
    current_user AS database_user;
```

Dann auf **Execute** ▶️ klicken.

### Erwartetes Ergebnis

Eine Zeile ungefähr:

database\_name

database\_user

foodstock

foodstock\_app

Damit wissen wir:

**App-Benutzer → FoodStock-Datenbank → funktioniert.**

Damit ist bestätigt:

```text
foodstock_app
       ↓
foodstock
       ↓
PostgreSQL
```

funktioniert.

* * *

# 31\. Aktueller Datenbankstatus

Der aktuelle Zustand ist:

```text
PostgreSQL 17.6
│
├── postgres
│    └── administratives Konto
│
└── foodstock
     └── Owner: foodstock_app
```

TimescaleDB läuft.

Die Datenbank ist erreichbar.

#Die Anwendung kann über `foodstock_app` auf die Datenbank zugreifen.

* * *
-
-
-
# ab hier nur noch ein paar Infos Installation ist fertig!
-
-
-
* * *

# 32\. Sicherheitsprinzip

Die endgültige FoodStock-Architektur darf NICHT so aussehen:

```text
Android
   ↓
PostgreSQL
```

und auch nicht:

```text
Android
   ↓
Internet
   ↓
PostgreSQL:5432
```

Stattdessen:

```text
Android
   │
   │ HTTPS
   │
   ▼
VPN / Heimnetz
   │
   ▼
FoodStock Backend
   │
   │ interne PostgreSQL-Verbindung
   ▼
TimescaleDB
   │
   ▼
foodstock
```

Die Android-App erhält niemals:

-   PostgreSQL-Passwort
-   PostgreSQL-Port
-   Datenbankzugangsdaten
-   direkten SQL-Zugriff

* * *

# 33\. Backup

Vor der Installation wurde ein Home-Assistant-Backup erstellt.

Das Backup wurde anschließend zusätzlich auf einem separaten Netzwerklaufwerk gespeichert.

## Warum?

Die USB-SSD ist der einzige lokale Speicher.

Ein SSD-Defekt könnte daher sämtliche lokalen Daten zerstören.

Mindestens eine zweite Kopie muss deshalb außerhalb der SSD existieren.

Geplante Backup-Struktur:

```text
Raspberry Pi
│
├── Home Assistant Backup
│
├── PostgreSQL-Daten
│
└── FoodStock-Dateien
       │
       ├── Produktbilder
       ├── optionale MHD-Fotos
       └── Exporte
       
       ↓

Separates Netzwerklaufwerk
```

* * *

# 34\. PostgreSQL-Backup

Die TimescaleDB-App besitzt eine Backup-/Restore-Funktion.

Beim Home-Assistant-Backup wird ein SQL-Dump der PostgreSQL-Datenbanken erzeugt.

Das PostgreSQL-Datenverzeichnis selbst wird dabei nicht einfach als rohe Datenbankdatei kopiert.

Das ist wichtig für:

-   Konsistenz
-   Wiederherstellung
-   Versionswechsel
-   Migration

Die App verwendet dafür einen SQL-Dump.

* * *

# 35\. FoodStock-Dateispeicher

Produktbilder und optionale MHD-Fotos sollen später NICHT direkt in PostgreSQL gespeichert werden.

Geplante Struktur:

```text
FoodStock
├── products/
├── expiration-images/
├── backups/
└── exports/
```

Die Dateien sollen im persistenten Speicher der FoodStock-Home-Assistant-App liegen.

Die PostgreSQL-Datenbank speichert lediglich Referenzen auf die Dateien.

Beispiel:

```text
products/abc123.jpg
```

statt einer großen Binärdatei in PostgreSQL.

* * *

# 36\. Geplante FoodStock-Datenbank

Die eigentliche FoodStock-Datenbank wird später unter anderem folgende Tabellen enthalten:

```text
users
products
inventory
storage_locations
shopping_list
transactions
```

Weitere Tabellen werden bei Bedarf ergänzt.

Die Datenbank wird relational aufgebaut.

Keine direkte PostgreSQL-Kommunikation durch FlutterFlow.

* * *

# 37\. Geplante Backend-Verbindung

Das FoodStock-Backend wird später folgende Verbindung verwenden:

```text
Host:
77b2833f-timescaledb

Port:
5432

Database:
foodstock

User:
foodstock_app

Password:
<FOODSTOCK_APP_PASSWORT>
```

Das Passwort wird ausschließlich im Backend gespeichert.

Es wird NICHT in der Android-App gespeichert.

* * *

# 38\. Ressourcenplanung

Aktueller Raspberry Pi:

```text
RAM:        4 GB
SSD:        109,3 GB
SSD frei:   ca. 54 GB
CPU:        4 Kerne
```

PostgreSQL wurde bewusst begrenzt:

```text
RAM:        512 MB
CPU:        2 Kerne
Connections:25
```

Damit bleiben Ressourcen für Home Assistant und vorhandene Apps verfügbar.

* * *

# 39\. Was NICHT gemacht wurde

Folgende Änderungen wurden bewusst vermieden:

```text
❌ Docker auf dem HAOS-Host installieren
❌ eigenes Docker-System aufbauen
❌ PostgreSQL auf dem Linux-Host installieren
❌ PostgreSQL-Port ins Internet öffnen
❌ PostgreSQL-Port unnötig im Router freigeben
❌ PostgreSQL-Daten in die Android-App einbauen
❌ Datenbankpasswörter in FlutterFlow speichern
❌ Home-Assistant-Systempartition manuell verändern
❌ bestehende Apps entfernen
```

* * *

# 40\. Nächster Projektschritt

Die PostgreSQL-Basis ist abgeschlossen.

Als nächstes wird das FoodStock-Backend als eigene Home-Assistant-App vorbereitet.

Geplante Struktur:

```text
Home Assistant OS
│
├── Home Assistant
│
├── vorhandene Apps
│
├── TimescaleDB
│    └── foodstock
│
├── pgAdmin4
│
└── FoodStock Backend
     │
     ├── REST API
     ├── Authentifizierung
     ├── Benutzer
     ├── Rollen
     ├── Produkte
     ├── Bestand
     ├── Einkaufsliste
     ├── MHD
     ├── Änderungshistorie
     └── Dateispeicher
```

Erst wenn das Backend läuft und ein API-Test erfolgreich ist, beginnt die Entwicklung der FlutterFlow-/Android-App.

* * *

# 41\. Sicherheitsregeln für die weitere Entwicklung

Diese Regeln gelten für das gesamte Projekt:

1.  PostgreSQL ist niemals direkt aus dem Internet erreichbar.
2.  PostgreSQL ist niemals direkt aus der Android-App erreichbar.
3.  Das `postgres`\-Konto wird nur administrativ verwendet.
4.  Das Backend verwendet `foodstock_app`.
5.  Passwörter werden niemals in FlutterFlow-Frontend-Code eingebaut.
6.  Die Android-App kommuniziert ausschließlich mit der API.
7.  Externer Zugriff erfolgt zunächst über VPN.
8.  HTTPS wird für die API verwendet.
9.  Änderungen am Bestand erfolgen serverseitig und transaktional.
10.  Wichtige Aktionen werden protokolliert.
11.  Backups werden auf eine zweite Speicherquelle kopiert.
12.  Vor größeren Änderungen wird ein Home-Assistant-Backup erstellt.
13.  Keine manuelle Veränderung des HAOS-Hosts.
14.  Bestehende Home-Assistant-Apps werden nicht unnötig verändert.

* * *

# 42\. Wiederholungs-Checkliste

Bei einer späteren Neuinstallation:

```text
[ ] Home Assistant Backup erstellen
[ ] Backup auf zweite Speicherquelle kopieren
[ ] Ressourcen prüfen
[ ] Expaso TimescaleDB Repository prüfen
[ ] TimescaleDB installieren
[ ] Datenbank foodstock anlegen
[ ] Ressourcen konfigurieren
[ ] PostgreSQL starten
[ ] PostgreSQL-Start prüfen
[ ] pgAdmin4 installieren
[ ] pgAdmin4 starten
[ ] PostgreSQL-Verbindung einrichten
[ ] postgres-Passwort ändern
[ ] foodstock_app erstellen
[ ] foodstock Owner auf foodstock_app setzen
[ ] foodstock_app-Verbindung testen
[ ] SQL-Funktionstest durchführen
[ ] Backup prüfen
```

* * *

# 43\. Erfolgreicher Endzustand

Die PostgreSQL-Basis gilt als erfolgreich eingerichtet, wenn alle folgenden Punkte erfüllt sind:

```text
[✓] TimescaleDB läuft
[✓] PostgreSQL 17.6 läuft
[✓] Datenbank foodstock existiert
[✓] postgres-Passwort wurde geändert
[✓] foodstock_app existiert
[✓] foodstock gehört foodstock_app
[✓] foodstock_app kann sich anmelden
[✓] SQL-Funktionstest erfolgreich
[✓] PostgreSQL-Port nicht öffentlich freigegeben
[✓] Home Assistant weiterhin funktionsfähig
[✓] Bestehende Apps nicht verändert
[✓] Home-Assistant-Backup vorhanden
[✓] Backup zusätzlich auf Netzwerklaufwerk gesichert
```

* * *

# 44\. Aktueller Stand des FoodStock-Projekts

## Fertig

```text
Home Assistant OS
        ↓
TimescaleDB / PostgreSQL
        ↓
foodstock
        ↓
foodstock_app
```

## Als nächstes

```text
FoodStock Backend
        ↓
REST API
        ↓
API-Test
```

Erst danach:

```text
FlutterFlow
        ↓
Android-App
        ↓
Barcode
        ↓
lokale OCR
        ↓
FoodStock API
```

* * *

# 45\. Passwort-Platzhalter

Diese Datei darf keine echten Passwörter enthalten.

Verwendete Platzhalter:

```text
<POSTGRES_ADMIN_PASSWORT>
<FOODSTOCK_APP_PASSWORT>
```

Die echten Passwörter gehören ausschließlich in einen sicheren Passwortmanager bzw. später in die sichere Backend-Konfiguration.

* * *

# Ende

Status:

**PostgreSQL / TimescaleDB erfolgreich eingerichtet und getestet.**

Nächster geplanter Schritt:

**FoodStock Backend als Home-Assistant-App vorbereiten.**
