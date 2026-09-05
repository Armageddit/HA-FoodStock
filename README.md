
# Projekt: FoodStock – private Lebensmittelverwaltungs-App

FoodStock ist eine private, selbst gehostete Lebensmittelverwaltung für Home Assistant und Android. Die Daten bleiben auf dem Raspberry Pi: Die Android-App kommuniziert ausschließlich mit der FoodStock-API, die wiederum PostgreSQL verwendet.

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


### **Phase 3 – FoodStock-Backend und Home-Assistant-Oberfläche**
*implementiert – Installation und Funktionstest auf dem Raspberry Pi stehen noch aus*

Der aktuelle Add-on-Stand ist **1.0.1** und enthält:

* ✅ Home-Assistant-Add-on für ARM64 mit FastAPI und PostgreSQL-Verbindung.
* ✅ Benutzeranmeldung mit JWT, Benutzer- und Administratorrollen.
* ✅ Relationale Tabellen für Produkte, einzelne Bestandseinheiten, Lagerorte, Einkaufsliste und Änderungshistorie.
* ✅ FIFO-Verbrauch nach ältestem MHD, negative Bestände und zentrale Soll-/Idealbestandslogik.
* ✅ Automatische Einkaufsliste, Ablaufübersicht, Barcode-Suche mit Open Food Facts und persistente Produktbilder unter `/data/foodstock`.
* ✅ Home-Assistant-kompatible Weboberfläche unter `http://<home-assistant-ip>:8000/ui/`: Anmeldung, Übersicht, Einlagern, Verbrauch, Ablaufdaten, Einkaufsliste und „Für KI kopieren“.
* ✅ `GET /ai/prompt` erzeugt den kostenlosen strukturierten Rezept-KI-Prompt direkt aus dem Vorrat.
* ✅ Vollständiger FlutterFlow-Erstellungsauftrag in [KiPromptAndroidApp.md](KiPromptAndroidApp.md).

### Nächste Schritte bis zur fertigen App

1. **Add-on aktualisieren und testen:** FoodStock in Home Assistant auf 1.0.1 aktualisieren, sichere Datenbankdaten, ein eigenes JWT-Secret und den initialen Administrator gemäß [foodstock/README.md](foodstock/README.md) setzen. Danach `/health`, `/docs` und `/ui/` im Heimnetz testen.
2. **Datenbank und Bedienoberfläche testen:** mindestens einen Lagerort und ein Produkt anlegen, einen Bestand mit MHD einlagern, FIFO-Verbrauch und automatische Einkaufsliste prüfen. Erst danach reale Vorratsdaten übernehmen.
3. **Backup einrichten:** PostgreSQL-Dump und `/data/foodstock` automatisiert auf ein zweites Ziel sichern; anschließend eine Wiederherstellung testweise durchführen.
4. **Zugriff absichern:** Extern nur über das WireGuard-VPN der FRITZ!Box zugreifen, PostgreSQL niemals veröffentlichen und vor einer externen App-Verteilung HTTPS über einen geeigneten Reverse Proxy/Ingress einrichten.
5. **FlutterFlow-App bauen:** [KiPromptAndroidApp.md](KiPromptAndroidApp.md) verwenden, API-Basis-URL im Heimnetz/VPN konfigurieren und Anmelde-, Barcode-, OCR- sowie Offline-Synchronisationsablauf auf einem Android-Gerät testen.
6. **Spätere Ausbaustufen:** optionales Speichern von MHD-Fotos, direkte kostenpflichtige KI-Anbindung, Speiseplanung und Home-Assistant-Dashboard-/Benachrichtigungsintegration.
