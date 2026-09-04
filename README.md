
# Projekt: FoodStock – private Lebensmittelverwaltungs-App

Dies ist aktuell eine Beta testverssion die noch nicht funktioniert!
Ich möchte eine vollständige Homeassistant Anwendung mit Android-App für die Verwaltung meines Lebensmittelvorrats bauen.

* * *

Festgelegte Hardware:

Der zentrale Server läuft zu Hause auf:

-   Raspberry Pi 4
-   4 GB RAM
-   USB-3.0-SSD mit installiertem Home Assistant OS (es gibt keine SD karte)
-   24/7-Betrieb
-   derzeit ungefähr 6 Home-Assistant-Apps/Add-ons installiert
-   FRITZ!Box als Router
-   Zugriff von außen soll über VPN erfolgen

### **Phase 1 – Ist-Zustand und Vorbereitung**
*abgeschlossen*

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

### **Phase 2 – PostgreSQL installieren**
*abgeschlossen*

Expaso-App „TimeScaleDb“ als PostgreSQL-Basis unterstützt aarch64

- TimescaleDB **5.4.2**
- PostgreSQL **17.6**
- Datenbank **foodstock**
- App läuft
- Slurg: 77b2833f\_timescaledb
- PostgreSQL-Port **nicht nach außen veröffentlicht**
- **Verwaltung über pgAdmin4**


### **Phase 3 – FoodStock-Backend vorbereiten**
*vorbereiten*

- Unsere endgültige Serverstruktur definieren
- Was wir als Backend-Technik verwenden werden
- Speicher planen innerhalb von `/data`
