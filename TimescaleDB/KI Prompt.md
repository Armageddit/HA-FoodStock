
# Projekt: FoodStock – private Lebensmittelverwaltungs-App

Ich möchte jetzt gemeinsam mit dir eine vollständige Android-App für die Verwaltung meines Lebensmittelvorrats bauen.

Der Plan ist **finalisiert**. Bitte beginne nicht erneut mit einer allgemeinen Technologieauswahl, sondern setze die folgende Architektur als Grundlage um.

Ich bin kein professioneller Programmierer und möchte die App möglichst **ohne klassisches Programmieren** erstellen. Verwende nach Möglichkeit No-Code/Low-Code und führe mich bei jedem Schritt exakt durch die notwendigen Einstellungen.

* * *

**1\. Festgelegte Hardware**

Der zentrale Server läuft zu Hause auf:

-   Raspberry Pi 4
-   4 GB RAM
-   USB-3.0-SSD mit installiertem Home Assistant OS (es gibt keine SD karte)
-   24/7-Betrieb
-   derzeit ungefähr 6 Home-Assistant-Apps/Add-ons installiert
-   FRITZ!Box als Router
-   Zugriff von außen soll über VPN erfolgen

Derzeit sind folgende Apps installiert:  
  

- ESPHome Device Builder (gestoppt läuft nur nach Bedarf)
- Mosquitto broker
- motionEye
- Node-RED
- Samba NAS (gestoppt nur als Notlösung für Zugriffe)
- Samba NAS2-β
- Samba share (gestoppt nur als Notlösung für Zugriffe)
- Solarflow Control (Version: 0.11.6 ohne Updates da es funktioniert)
- Studio Code Server (gestoppt läuft nur nach Bedarf)
- Terminal & SSH (gestoppt läuft nur nach Bedarf)
- Zigbee2MQTT

InstallationsmethodeHome Assistant OS

-   Core2026.9.0
-   Supervisor2026.08.0
-   Operating System18.2
-   Frontend 20260826.4

Die vorhandene Home-Assistant-Installation soll möglichst **nicht beeinträchtigt** werden.

Bitte prüfe bei jedem Installationsschritt, dass Home Assistant und die vorhandenen Apps weiterhin funktionieren.

## Entwicklungsrechner

Der Entwicklungsrechner des Projekts ist ein Windows-PC.

Windows wird für folgende Aufgaben verwendet:

- Bearbeiten von Projektdateien
- Entwicklung und Verwaltung des FoodStock-Backends
- Zugriff auf den Raspberry Pi über das Netzwerk
- Git/Versionsverwaltung
- FlutterFlow
- Android-App-Entwicklung und Tests

Der Raspberry Pi selbst verwendet weiterhin ausschließlich
Home Assistant OS.

Es wird kein normales Docker-System manuell auf dem
Home-Assistant-OS-Host installiert.


* * *

**2\. Grundprinzip**

Die App soll möglichst vollständig selbst gehostet werden.

Keine Firebase-Datenbank als primäre Lösung.

Keine dauerhafte Abhängigkeit von einem externen Cloud-Anbieter für die eigentlichen Vorratsdaten.

Die gewünschte Architektur ist:

Android-Handy

    │

    │ HTTPS / VPN

    ▼

FRITZ!Box

    │

    ▼

Raspberry Pi 4

    │

    └── Home Assistant OS

          │

          ├── Home Assistant

          │

          ├── PostgreSQL

          │

          └── FoodStock Backend

                 │

                 ├── API

                 ├── Geschäftslogik

                 ├── Benutzer/Rechte

                 ├── Produktdaten

                 ├── Bestandsdaten

                 ├── Einkaufsliste

                 └── Dateispeicher

Der Raspberry Pi soll damit praktisch mein eigener kleiner Heimserver für die Lebensmittel-App sein.

* * *

**3\. Wichtige technische Entscheidung**

Wir wollen **nicht Supabase zwingend auf Home Assistant OS installieren**, wenn eine schlankere eigene Lösung sinnvoller ist.

Bevorzugt werden:

-   PostgreSQL als Datenbank
-   eigenes schlankes FoodStock-Backend
-   REST API bzw. geeignete HTTPS-API
-   Home-Assistant-App/Add-on für das Backend
-   eigener Speicher auf der SSD

Wenn du feststellst, dass eine Komponente technisch mit Home Assistant OS nicht sinnvoll als App/Add-on betrieben werden kann, suche eine geeignete Alternative.

Bitte Home Assistant OS **nicht durch manuelle Installation eines normalen Docker-Systems verändern**.

Keine Anleitung, die Home Assistant OS unnötig gefährdet.

* * *

**4\. Android-App**

Die Android-App soll möglichst mit FlutterFlow umgesetzt werden.

FlutterFlow dient hauptsächlich als Benutzeroberfläche.

Die eigentliche Datenhaltung und Geschäftslogik liegt auf dem Raspberry Pi.

Architektur:

FlutterFlow Android-App

        │

        ▼

FoodStock API

        │

        ▼

PostgreSQL

Die Android-App soll niemals direkt mit PostgreSQL kommunizieren.

* * *

**5\. Barcode-Erkennung**

Der Barcode soll **direkt auf dem Smartphone** mit der Kamera erkannt werden.

Der Raspberry Pi erhält nur die erkannte Barcode-Nummer.

Ablauf:

📱 Barcode scannen

       ↓

Barcode lokal erkennen

       ↓

Barcode = 4001234567890

       ↓

FoodStock API

       ↓

eigene Produktdatenbank

       ↓

wenn nicht vorhanden:

Open Food Facts abfragen

Wenn das Produkt gefunden wird:

-   Produktname
-   Hersteller
-   Produktbild
-   Kategorie
-   weitere verfügbare Informationen

übernehmen.

Wenn es nicht gefunden wird:

Benutzer kann das Produkt manuell anlegen.

* * *

**6\. OCR für MHD**

Die OCR soll **direkt auf dem Smartphone** laufen.

Bevorzugt soll eine On-Device-OCR-Lösung wie Google ML Kit verwendet werden, sofern sie sich sinnvoll mit FlutterFlow bzw. den notwendigen Custom Actions integrieren lässt.

Wichtig:

Die MHD-Fotos müssen nicht standardmäßig zum Raspberry Pi übertragen werden.

Ablauf:

📱 Foto vom MHD

       ↓

OCR lokal auf Smartphone

       ↓

Datum erkannt?

       │

       ├── Ja

       │    ↓

       │  Plausibilitätsprüfung

       │    ↓

       │  Benutzer bestätigt

       │

       └── Nein

            ↓

       Benutzer wählt Datum

       manuell aus

* * *

**7\. MHD-Erkennung darf niemals blind gespeichert werden**

Wenn OCR beispielsweise erkennt:

15.09.2026

zeigt die App:

Erkanntes Datum:

15.09.2026

\[✓ Übernehmen\]

\[✏️ Ändern\]

Wenn OCR unsicher ist:

⚠️ Datum konnte nicht sicher erkannt werden.

\[📅 Datum manuell auswählen\]

Der Benutzer kann jederzeit einen anderen Wert auswählen.

* * *

**8\. MHD-Kameraansicht**

Beim Fotografieren soll möglichst ein Bereich angezeigt werden, in dem das MHD platziert werden soll.

Beispielsweise:

┌─────────────────────────────┐

│                             │

│   MHD innerhalb des Rahmens │

│                             │

│    ┌───────────────────┐    │

│    │ MHD 15.09.2026    │    │

│    └───────────────────┘    │

│                             │

└─────────────────────────────┘

            \[📷\]

Ziel:

Die OCR soll möglichst nur den relevanten Bereich analysieren.

* * *

**9\. MHD-Fotos**

Standardmäßig:

Foto aufnehmen

↓

OCR

↓

Datum bestätigen

↓

Foto nicht dauerhaft speichern

Optional soll ein Originalfoto gespeichert werden können.

Wenn gespeichert:

Raspberry Pi SSD

    ↓

FoodStock Storage

    ↓

MHD-Foto

Die Speicherung soll nicht zwingend notwendig sein.

* * *

**10\. Produktbilder**

Produktbilder können kommen aus:

1.  Open Food Facts
2.  Benutzerfoto
3.  Upload

Die Bilddateien werden auf dem Raspberry Pi gespeichert.

Nicht direkt als große Binärdaten in PostgreSQL speichern.

In der Datenbank wird eine Referenz auf die Datei gespeichert.

* * *

**11\. Datenbank**

PostgreSQL soll die zentrale Datenbank werden.

Mindestens folgende Bereiche sollen berücksichtigt werden:

users

products

inventory

storage\_locations

shopping\_list

transactions

Weitere Tabellen können ergänzt werden, wenn sie sinnvoll sind.

Bitte verwende eine relationale Struktur und keine unnötige Datenduplizierung.

* * *

**12\. Produkte**

Ein Produkt beschreibt die allgemeine Information.

Beispiel:

Produkt:

Tomatensoße

Barcode:

4001234567890

Hersteller:

Beispiel GmbH

Standardlagerort:

Keller / Regal 2

Sollbestand:

5

Idealbestand:

10

Einheit:

Stück

Mögliche Felder:

-   product\_id
-   barcode
-   name
-   manufacturer
-   image\_path
-   category
-   unit
-   default\_storage\_location\_id
-   minimum\_stock
-   ideal\_stock
-   active
-   created\_at
-   updated\_at

* * *

**13\. Einzelne Lebensmittel**

Produkte und tatsächliche vorhandene Lebensmittel müssen getrennt sein.

Beispiel:

Produkt:

Milch 1,5 %

Bestand:

02.09.2026

05.09.2026

05.09.2026

12.09.2026

20.09.2026

Deshalb sollen einzelne Bestandseinheiten gespeichert werden.

Eine Inventory-Einheit soll beispielsweise enthalten:

-   inventory\_id
-   product\_id
-   expiration\_date
-   storage\_location\_id
-   status
-   added\_by
-   added\_at
-   consumed\_at
-   optional image reference

* * *

**14\. Bestand**

Der Bestand soll möglichst aus den vorhandenen aktiven Inventory-Einheiten ermittelt werden.

Beispiel:

5 aktive Einheiten

\=

Bestand 5

Wird eine Einheit verbraucht:

5 → 4

Dabei soll möglichst das Lebensmittel mit dem ältesten MHD zuerst verwendet werden.

FIFO:

ältestes MHD

↓

zuerst verbrauchen

* * *

**15\. Negative Bestände**

Negative Bestände sind ausdrücklich erlaubt.

Beispiel:

Tomatensoße

Bestand: -2

Sollbestand: 5

Idealbestand: 10

Das bedeutet, dass 2 Stück fehlen.

Die Einkaufsliste muss damit korrekt umgehen.

* * *

**16\. Sollbestand und Idealbestand**

Für jedes Produkt:

aktueller Bestand

Sollbestand

Idealbestand

Regel:

Wenn

Bestand < Sollbestand

muss das Produkt auf die Einkaufsliste.

Wenn ein Idealbestand existiert:

Einkaufsmenge =

Idealbestand - aktueller Bestand

Beispiel:

Bestand: 4

Soll: 5

Ideal: 10

10 - 4 = 6

Einkauf:

6 Stück

* * *

**17\. Kein Idealbestand**

Wenn Idealbestand nicht definiert ist:

Einkaufsmenge =

Sollbestand - aktueller Bestand

Beispiel:

Bestand: 3

Soll: 5

Ideal: leer

5 - 3 = 2

Bei negativem Bestand muss entsprechend gerechnet werden.

Beispiel:

Bestand: -2

Soll: 5

Ideal: leer

5 - (-2) = 7

Bitte implementiere diese Berechnungslogik zentral im Backend, damit alle Benutzer dieselben Ergebnisse bekommen.

* * *

**18\. Einkaufsliste**

Die Einkaufsliste soll automatisch entstehen.

Beispiel:

🛒 Einkaufsliste

Milch             4

Tomatensoße       6

Nudeln            3

Butter             2

Benutzer können Artikel abhaken.

Es soll zwischen folgenden Zuständen unterschieden werden:

-   benötigt
-   auf Einkaufsliste
-   gekauft
-   in Bestand übernommen

Eine spätere Funktion soll ermöglichen:

Einkauf erledigt

↓

Produkte beim Einräumen scannen

↓

Bestand erhöhen

↓

Einkaufsliste aktualisieren

* * *

**19\. Ablaufdaten**

Die App soll automatisch anzeigen:

**Abgelaufen**

Datum liegt in der Vergangenheit.

**Dringend**

MHD innerhalb von 3 Tagen.

**Bald**

MHD innerhalb von 7 Tagen.

**Demnächst**

MHD innerhalb von 14 Tagen.

Diese Grenzen sollen später einstellbar sein.

* * *

**20\. Rezept-KI**

Die App soll Lebensmittel erkennen, die bald ablaufen.

Beispiel:

Sahne – 1 Tag

Paprika – 2 Tage

Feta – 3 Tage

Tomaten – 4 Tage

Daraus sollen Rezeptvorschläge erzeugt werden.

Priorität:

1.  Lebensmittel mit kürzestem MHD
2.  weitere vorhandene Lebensmittel
3.  möglichst wenige zusätzliche Einkäufe

* * *

**21\. Zunächst kostenlose KI-Funktion**

Die erste Version benötigt keine kostenpflichtige KI-API.

Es soll einen Button geben:

**„Für KI kopieren“**

Die App erzeugt einen strukturierten Prompt/Text.

Beispiel:

Erstelle 3 Rezeptvorschläge aus meinem Lebensmittelvorrat.

Priorität:

Verwende zuerst Lebensmittel, die bald ablaufen.

Bald ablaufend:

\- Sahne, 1 Becher, MHD 23.08.2026

\- Paprika, 2 Stück, MHD 24.08.2026

\- Feta, 1 Packung, MHD 25.08.2026

\- Tomaten, 4 Stück, MHD 26.08.2026

Weitere vorhandene Lebensmittel:

\- Nudeln, 3 Packungen

\- Reis, 2 Packungen

\- Zwiebeln, 5 Stück

\- Tomatensoße, 4 Gläser

Bitte:

\- bevorzuge Lebensmittel mit kurzem MHD

\- verwende möglichst viele vorhandene Lebensmittel

\- vermeide unnötige Einkäufe

\- nenne fehlende Zutaten separat

\- gib Mengen an

\- gib die Zubereitung an

\- berücksichtige die MHD-Reihenfolge

Der Text soll in die Zwischenablage kopiert werden.

* * *

**22\. Spätere direkte KI-Integration**

Als optionale Erweiterung soll eine direkte KI-API möglich sein.

Beispielsweise:

🤖 Was soll ich kochen?

\[🍝 Schnelles Abendessen\]

\[👨‍👩‍👧 Für die Familie\]

\[🥗 Vegetarisch\]

\[⏱ Unter 30 Minuten\]

\[♻️ Möglichst wenig wegwerfen\]

\[🎲 Überraschung\]

Die direkte KI-Anbindung ist optional und kann kostenpflichtig sein.

Die Basis-App soll auch ohne KI-API vollständig funktionieren.

* * *

**23\. Spätere Speiseplanung**

Die Architektur soll später ermöglichen:

Erstelle einen 5-Tage-Speiseplan.

Ziel:

Möglichst wenig Lebensmittel wegwerfen.

Priorität:

Lebensmittel mit kurzem MHD zuerst.

Berücksichtige:

\- Vorrat

\- MHD

\- Mengen

\- Einkaufsliste

Dafür soll jetzt noch keine komplizierte Funktion gebaut werden, aber die Datenstruktur soll dies später ermöglichen.

* * *

**24\. Benutzer**

Es gibt mindestens zwei Rollen:

**Benutzer**

Darf:

-   anmelden
-   scannen
-   Produkte hinzufügen
-   MHD erfassen
-   Lagerort auswählen
-   Bestand ansehen
-   Lebensmittel verbrauchen
-   Einkaufsliste ansehen
-   Einkaufsliste bearbeiten/abhaken
-   KI-Export verwenden

**Administrator**

Darf zusätzlich:

-   Produkte bearbeiten
-   Barcodes korrigieren
-   Produktbilder ändern
-   OCR-/MHD-Daten korrigieren
-   Bestände korrigieren
-   Lagerorte verwalten
-   Sollbestand ändern
-   Idealbestand ändern
-   Benutzer verwalten
-   Produkte deaktivieren/löschen
-   Änderungshistorie ansehen

* * *

**25\. Authentifizierung**

Benutzer sollen sich anmelden.

Die App darf nicht einfach öffentlich auf die API zugreifen.

Die API muss Benutzer authentifizieren und Berechtigungen prüfen.

Ein Admin soll über seine Benutzerrolle erkannt werden.

Kein gemeinsames hartcodiertes Admin-Passwort.

* * *

**26\. Änderungshistorie**

Wichtige Aktionen müssen protokolliert werden.

Beispiele:

22.08.2026

Max

Tomatensoße

\-1

Grund: verbraucht

oder:

22.08.2026

Admin

Tomatensoße

Bestand 3 → 5

Grund: Bestandskorrektur

Mögliche Ereignisse:

-   added
-   consumed
-   purchased
-   corrected
-   deleted
-   restored

* * *

**27\. API**

Das Backend soll eine sichere API bereitstellen.

Die Android-App darf nicht direkt auf PostgreSQL zugreifen.

Beispiel:

GET /products

GET /products/{id}

POST /products

POST /scan

GET /inventory

POST /inventory

POST /inventory/{id}/consume

GET /shopping-list

POST /shopping-list

GET /expiring

GET /users

Das sind nur Beispiele.

Bitte entwirf eine sinnvolle vollständige API.

* * *

**28\. Sicherheit**

Bitte berücksichtige:

-   HTTPS
-   VPN für externen Zugriff
-   Authentifizierung
-   Rollen/Rechte
-   sichere API-Tokens
-   keine PostgreSQL-Zugangsdaten in der Android-App
-   keine offenen PostgreSQL-Ports im Internet
-   keine unnötig offenen Ports
-   sichere Speicherung von Passwörtern
-   Backups
-   Update-Strategie

Die Datenbank soll ausschließlich über das Backend erreichbar sein.

* * *

**29\. VPN**

Der Zugriff von außerhalb des Hauses soll über VPN erfolgen.

FRITZ!Box und/oder WireGuard sollen dafür verwendet werden, sofern das mit der vorhandenen FRITZ!Box sinnvoll möglich ist.

Prinzip:

Handy

 ↓

VPN

 ↓

FRITZ!Box

 ↓

Heimnetz

 ↓

Raspberry Pi

 ↓

FoodStock API

Bitte keine direkte öffentliche Freigabe von PostgreSQL.

Wenn für die Android-App ein sicherer HTTPS-Zugriff ohne manuell ständig aktives VPN sinnvoller ist, erkläre die Vor- und Nachteile, aber bevorzuge zunächst die sichere Lösung mit VPN.

* * *

**30\. Offline-Betrieb**

Die App soll möglichst auch bei schlechtem Internet funktionieren.

Insbesondere:

-   zuletzt geladene Produktdaten
-   Lagerorte
-   relevante Bestandsdaten
-   Scanvorgänge
-   OCR

sollen möglichst lokal funktionieren.

Barcode und OCR funktionieren ohnehin lokal auf dem Handy.

Wenn die Verbindung zum Raspberry Pi nicht verfügbar ist:

Aktion lokal speichern

↓

Verbindung später wieder vorhanden

↓

Synchronisieren

Bitte entwickle eine Strategie zur Konfliktbehandlung.

Insbesondere darf nicht passieren:

Handy 1: Bestand 5 → 4

Handy 2: Bestand 5 → 4

Ergebnis soll nicht fälschlicherweise wieder 5 sein.

Verwende für Bestandsänderungen möglichst Transaktionen bzw. serverseitige Operationen.

* * *

**31\. Speicher**

Produktbilder und optionale MHD-Fotos sollen auf der USB-SSD des Raspberry Pi gespeichert werden.

Beispielsweise:

FoodStock/

├── products/

├── expiration-images/

├── backups/

└── exports/

Bitte kläre, wie dieser Speicher innerhalb einer Home-Assistant-App sicher und dauerhaft eingebunden wird.

* * *

**32\. Home Assistant OS**

Die Lösung muss auf Home Assistant OS laufen.

Home Assistant selbst und die vorhandenen ca. 6 Apps dürfen nicht beschädigt werden.

Bevor du Installationsanweisungen gibst:

1.  prüfe die aktuelle Home-Assistant-Dokumentation
2.  prüfe die aktuelle Dokumentation für eigene Apps/Add-ons
3.  prüfe die Anforderungen der vorgeschlagenen Datenbank
4.  prüfe die RAM-/Speicheranforderungen
5.  nenne mögliche Risiken

Keine Änderungen am Host-System, die von Home Assistant OS nicht vorgesehen sind.

* * *

**33\. Ressourcen**

Hardware:

Raspberry Pi 4

4 GB RAM

USB 3 SSD

24/7

Home Assistant OS

ca. 6 vorhandene Apps

Bitte berücksichtige den begrenzten RAM.

Keine unnötigen Dienste installieren.

Wenn PostgreSQL zu viel Ressourcen benötigt, prüfe eine leichtere Alternative.

Wenn du zu dem Ergebnis kommst, dass die Hardware für eine bestimmte Komponente nicht reicht, sage das klar, bevor wir sie installieren.

* * *

**34\. Backups**

Da die Daten vollständig bei mir zu Hause liegen, sind Backups besonders wichtig.

Bitte plane:

-   regelmäßige Datenbank-Backups
-   Backup der Produktbilder
-   Backup der Konfiguration
-   Wiederherstellungstest
-   möglichst automatisches Backup
-   idealerweise zweite Speicherquelle

Die einzige SSD darf nicht der einzige Ort sein, an dem die Daten existieren.

* * *

**35\. Home-Assistant-Integration**

Wenn sinnvoll, soll FoodStock später auch mit Home Assistant kommunizieren können.

Beispiele:

⚠️ 4 Lebensmittel laufen bald ab

🛒 8 Artikel auf Einkaufsliste

📦 126 Lebensmittel vorhanden

Spätere mögliche Funktionen:

-   Home-Assistant-Dashboard
-   Benachrichtigung bei ablaufenden Lebensmitteln
-   Benachrichtigung bei neuer Einkaufsliste
-   Sprachabfrage
-   Automationen

Diese Funktionen müssen zunächst nicht gebaut werden.

Die Architektur soll sie aber ermöglichen.

* * *

**36\. App-Oberfläche**

Die Hauptnavigation:

🏠 Startseite

📷 Scannen

📦 Bestand

⚠️ Bald ablaufend

🛒 Einkaufsliste

🤖 Rezeptvorschläge

📍 Lagerorte

⚙ Einstellungen

Für Admin:

⚙ Admin

├── Produkte

├── Bestand

├── Benutzer

├── Lagerorte

├── Soll-/Idealbestände

└── Änderungshistorie

* * *

**37\. Startseite**

Beispiel:

MEIN VORRAT

\[📷 PRODUKT SCANNEN\]

📦 126 Lebensmittel

⚠️ 4 bald ablaufend

🛒 8 Artikel auf Einkaufsliste

\[📦 Bestand\]

\[🛒 Einkaufsliste\]

\[⚠️ Bald ablaufend\]

\[🤖 Rezeptvorschläge\]

Bitte verbessere das UI, wenn du eine sinnvollere Benutzerführung kennst.

Die App soll für eine Familie einfach und schnell bedienbar sein.

* * *

**38\. Scan-Ablauf**

Der komplette Scanprozess soll möglichst wenige Schritte benötigen:

📷 SCANNEN

↓

Barcode

↓

Produkt erkannt

↓

Menge auswählen

↓

MHD fotografieren

↓

OCR

↓

Datum bestätigen

↓

Lagerort bestätigen

↓

Speichern

Bei bereits bekanntem Produkt:

Barcode

↓

Produkt bekannt

↓

Standardlagerort vorgeschlagen

↓

MHD

↓

Speichern

Je weniger Eingaben nötig sind, desto besser.

* * *

**39\. Unbekanntes Produkt**

Wenn Barcode nicht gefunden wird:

Unbekanntes Produkt

Produktname:

\_\_\_\_\_\_\_\_\_\_\_\_\_

Hersteller:

\_\_\_\_\_\_\_\_\_\_\_\_\_

\[📷 Produktfoto\]

Lagerort:

\_\_\_\_\_\_\_\_\_\_\_\_\_

Sollbestand:

\_\_\_\_

Idealbestand:

\_\_\_\_

\[Speichern\]

Das Produkt soll anschließend dauerhaft in der eigenen Datenbank vorhanden sein.

* * *

**40\. Ablauf „Verbraucht“**

Wenn ein Benutzer ein Lebensmittel verbraucht:

Produkt öffnen

↓

\[Verbraucht\]

↓

älteste aktive Inventory-Einheit auswählen

↓

Status = consumed

↓

Bestand aktualisieren

↓

Einkaufsliste neu berechnen

Falls der Bestand dadurch unter den Sollbestand fällt, soll die Einkaufsliste automatisch angepasst werden.

* * *

**41\. Einkaufsliste und Bestand müssen zusammenarbeiten**

Beispiel:

Bestand: 6

Soll: 5

Ideal: 10

Keine Einkaufsliste

Eine Einheit wird verbraucht:

6 → 5

Noch keine Einkaufsliste.

Noch eine Einheit:

5 → 4

Jetzt:

4 < 5

Einkaufsliste:

6 Stück

Wenn Idealbestand 10 ist.

* * *

**42\. Ziel der Entwicklung**

Am Ende soll eine funktionierende Android-App entstehen:

Barcode

↓

Produkt

↓

MHD per lokaler OCR

↓

Bestätigung

↓

Lagerort

↓

Bestand

↓

Verbrauch

↓

Soll-/Idealbestand

↓

Einkaufsliste

↓

Ablaufwarnungen

↓

KI-Rezeptvorschläge

Mehrere Personen sollen denselben Vorrat nutzen können.

Die eigentlichen Daten bleiben auf meinem Raspberry Pi.

* * *

**43\. Kosten**

Die Lösung soll möglichst ohne monatliche Cloudkosten funktionieren.

Bevorzugt:

-   Home Assistant OS: vorhandene Installation
-   PostgreSQL: Open Source
-   FoodStock Backend: selbst gehostet
-   Bilder: eigene SSD
-   OCR: lokal auf Smartphone
-   Barcode: lokal auf Smartphone
-   KI-Export: kostenlos
-   VPN: vorhandene FRITZ!Box
-   externe KI-API: optional

Bitte unterscheide klar zwischen:

**kostenlos**

und

**einmaligen bzw. optionalen Kosten**.

* * *

**44\. Sehr wichtig: aktuelle Informationen**

Bei technischen Fragen zu:

-   Home Assistant OS
-   Home Assistant Apps/Add-ons
-   FlutterFlow
-   Android
-   ML Kit
-   PostgreSQL
-   Open Food Facts
-   VPN
-   FRITZ!Box
-   Google Play
-   KI-APIs

sollst du bei Bedarf aktuelle offizielle Dokumentation recherchieren.

Keine veralteten Anleitungen verwenden, wenn sich die Plattform inzwischen geändert hat.

Bevorzuge offizielle Dokumentation gegenüber Blogartikeln.

* * *

**45\. Arbeitsweise**

Wir bauen die App Schritt für Schritt.

Bitte nicht 20 Schritte auf einmal geben.

Arbeite nach folgendem Muster:

**Schritt X**

**Ziel**

Kurze Erklärung.

**Was ich anklicken muss**

Exakte Anleitung.

**Was ich eingeben muss**

Fertige Werte/Code/Dateien.

**Ergebnis**

Was danach sichtbar sein sollte.

**Test**

Wie ich überprüfe, ob es funktioniert.

Erst wenn der Schritt funktioniert, gehen wir weiter.

* * *

**46\. Wenn Code notwendig ist**

Ich möchte möglichst wenig programmieren.

Wenn Code erforderlich ist:

-   erkläre warum
-   gib den vollständigen Code
-   sage exakt, in welche Datei er gehört
-   gib den Dateinamen an
-   gib den Pfad an
-   erkläre, welche Werte ich ändern muss
-   erkläre, wie ich den Code testen kann

Keine unvollständigen Codefragmente, wenn ein vollständiger Code benötigt wird.

* * *

**47\. Erste Aufgabe im neuen Chat**

**Beginne jetzt mit der Umsetzung.**

Da die Architektur bereits festgelegt wurde, möchte ich keine erneute allgemeine Diskussion über Firebase, Google Cloud oder andere Cloud-Backends.

Starte stattdessen mit:

**Phase 1 – Ist-Zustand und Vorbereitung** abgeschlossen

1.  Prüfe anhand der aktuellen offiziellen Home-Assistant-Dokumentation, wie eigene Apps/Add-ons unter Home Assistant OS aktuell aufgebaut und installiert werden.
2.  Prüfe, welche Anforderungen PostgreSQL auf dem Raspberry Pi 4 mit 4 GB RAM hat.
3.  Prüfe, wie wir PostgreSQL als Home-Assistant-App/Add-on betreiben können.
4.  Prüfe, wie ein eigenes FoodStock-Backend als Home-Assistant-App/Add-on aufgebaut werden sollte.
5.  Prüfe, wie der Speicher dauerhaft für Datenbank, Bilder und Backups verwendet werden kann.
6.  Berücksichtige, dass bereits etwa 6 Apps/Add-ons installiert sind.
7.  Entwickle daraus den konkreten Installationsplan.

**Noch keine produktiven Änderungen durchführen.**

Zuerst soll ein sicherer Plan entstehen.

Danach bauen wir zunächst die Serverbasis:

**Phase 2 – PostgreSQL installieren** abgeschlossen

Expaso-App „TimeScaleDb“ als PostgreSQL-Basis unterstützt aarch64

- TimescaleDB **5.4.2**
- PostgreSQL **17.6**
- Datenbank **foodstock**
- App läuft
- Slurg: 77b2833f\_timescaledb
- PostgreSQL-Port **nicht nach außen veröffentlicht**
- **Verwaltung über pgAdmin4**


**Phase 3 – FoodStock-Backend vorbereiten** vorbereiten

- Unsere endgültige Serverstruktur definieren
- Was wir als Backend-Technik verwenden werden
- Speicher planen innerhalb von `/data`


Home Assistant OS

↓

PostgreSQL



↓

FoodStock Backend

↓

API-Test

Erst wenn das funktioniert, beginnen wir mit FlutterFlow und der Android-App.

* * *

**48\. Grundsatz**

Bitte behandle diese Nachricht als **verbindliche Projektspezifikation**.

Wenn du eine bessere technische Lösung findest, ändere die Architektur nicht stillschweigend.

Erkläre:

1.  welche Änderung du vorschlägst
2.  warum sie besser ist
3.  welche Vor- und Nachteile sie hat
4.  ob sie zusätzliche Kosten verursacht

und warte auf meine Zustimmung, bevor du die grundlegende Architektur änderst.

Ziel ist eine:

**private, selbst gehostete, möglichst kostenlose, sichere und langfristig wartbare Android-Lebensmittelverwaltung für mehrere Benutzer mit Barcode, lokaler OCR, MHD-Verwaltung, Lagerorten, Bestand, Einkaufsliste und KI-Rezeptfunktion.**
