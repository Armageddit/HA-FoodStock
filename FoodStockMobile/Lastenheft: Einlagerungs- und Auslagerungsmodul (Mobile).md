# Lastenheft: Einlagerungs- und Auslagerungsmodul (Mobile)

**Dokumententyp:** Lastenheft / Fachliche & Funktional-Systematische Spezifikation  
**Projekt:** HA-FoodStock Mobile  
**Worktree / Pfad:** `/home/arma/HA-FoodStock/worktrees/hep3/mobile`  
**Zieldatei:** `spec_t_lastenheft_inout_module.md`  
**Status:** In Review (Projektleiter-Prüfung)  
**Autor:** Hermine (Technical Lead)  
**Ziel-Repository:** HA-FoodStock Mobile (Separates Repository, getrennt vom Backend)  

---

## 1. Ziel und Abgrenzung des Moduls

### 1.1 Zielstellung
Das Einlagerungs- und Auslagerungsmodul bildet die zentrale operative Schnittstelle der HA-FoodStock Mobile-App zur physischen Bestandsführung von Lebensmitteln. Es ermöglicht Anwendern die effiziente, fehlerminimierte und benutzerfreundliche Erfassung von Zu- und Abgängen im Vorratslager.

Das Modul vereint automatische Erfassungsverfahren (EAN-13/8-Barcodescan via Kamera, Mindesthaltbarkeitsdatum [MHD] via Optical Character Recognition [OCR]) mit manuellen Eingabemöglichkeiten. Es stellt sicher, dass Bestände mit exakten Produktdaten, Mengenangaben, Verfallsdaten und Lagerorten erfasst und nach dem First Expire-First Out (FEFO)-Prinzip ausgemustert oder verbraucht werden können.

Das Modul soll das bisherige, iterativ gewachsene Scan- und Bestandsformular ablösen und durch eine konsistente, robuste und wartbare Neuentwicklung ersetzt werden.

### 1.2 System-Abgrenzung (Scope)
* **In Scope (Mobile App):**
  * Benutzeroberfläche und Bedienablauf für Einlagerung und Auslagerung (Inbound / Outbound Stock).
  * Kamera-gestützte Barcode-Scannung (EAN-8, EAN-13, UPC-A, UPC-E).
  * Kamera-gestützte OCR-Erfassung von Datumswerten (MHD) mit visuellem Zielrahmen (Region of Interest / ROI) und optionaler manueller Fehleingabekorrektur.
  * Dynamisches Umschalten zwischen Einlagern- und Auslagern-Betriebsmodus.
  * Produktstammdaten-Abfrage über den zentralen Scan-Endpoint (`GET /scan/{barcode}`).
  * Formularvalidierung, Fehlermeldungsaufbereitung und Offline-/Online-Zustandsbehandlung auf der Ebene des Mobile Clients.
  * Integrierter Diagnostik- / Debug-Modus für Entwickler und Tester (Visualisierung von Bildausschnitten, OCR-Rohtexten und Kamera-Status).
* **Out of Scope (Backend & Externe Systeme):**
  * Änderungen an Backend-APIs, Datenbank-Schemata oder Server-Logiken.
  * Änderung der Authentifizierungs- oder Autorisierungsarchitektur (Token-Verwaltung erfolgt über die bestehende Infrastruktur).
  * Zusammenführung von Mobile-Repo und Backend-Repo (Mobile bleibt als eigenständiger Worktree/Repository isoliert).
  * Physische Steuerung von Hardware-Scannern (ausschließlich integrierte Smartphone-Kamera wird unterstützt).

---

## 2. Rollen / Nutzergruppen

| Rolle | Beschreibung & Berechtigung im Modul | Hauptsächliches Nutzungsszenario |
| :--- | :--- | :--- |
| **Lagerhalter / Haushaltsanwender** | Standardnutzer der Mobile-App. Hat Lese- und Schreibrechte für Bestandsbuchungen im eigenen Haushalt. | Tägliches Scannen von Neueinkäufen (Einlagerung) und Entnahme von Lebensmitteln zum Kochen/Verbrauch (Auslagerung). |
| **Gast / Nur-Lese-Nutzer** | Eingeschränkter Nutzer ohne Schreibrechte. | Darf Bestände und Produktdaten einsehen und scannen, jedoch keine Ein- oder Auslagerungsbuchungen ausführen (Buttons deaktiviert). |
| **System-Administrator / Tester** | Technischer Anwender mit aktiviertem Debug-Modus. | Diagnose von OCR-Erkennungsfehlern, Prüfung von Kamera-Crops, Einblick in Rohdaten von API-Antworten. |

---

## 3. Fachlicher Gesamtprozess

```
                    [ Start Modul: Scan-Tab ]
                                |
                   [ Modus-Wahl in AppBar ]
                     /                  \
            ( "Einlagern" )         ( "Auslagern" )
                   |                       |
          [ Barcode scannen ]     [ Barcode scannen ]
          [ / manuell EAN ]       [ / manuell EAN ]
                   |                       |
          [ GET /scan/{ean} ]     [ GET /scan/{ean} ]
                   |                       |
        +----------+----------+            +-------+-------+
        |                     |                    |
  (Gefunden)            (Nicht gef.)           (Gefunden)
        |                     |                    |
  [ MHD via OCR         [ MHD via OCR         [ Bestände & MHDs
    / Kalender ]          / Kalender ]          FEFO anzeigen ]
        |                     |                    |
  [ Produktdaten        [ Stammdaten          [ Menge & MHD
    anzeigen ]            manuell anlegen ]     wählen ]
        |                     |                    |
  [ Lagerort &          [ Lagerort &         [ Verbrauchen oder
    Menge ]               Menge ]              öffnen wählen ]
        |                     |                    |
  [ "Einlagern"         [ "Einlagern"        [ "Auslagern"
    bestätigen ]          bestätigen ]         bestätigen ]
        |                     |                    |
  [ POST /inventory ]   [ POST /inventory ]  [ POST /inventory/consume ]
        |                     |                    |
        +---------------------+--------------------+
                              |
                    [ Erfolgs-Feedback &
                       Formular-Reset ]
```

---

## 4. Detaillierte Benutzerabläufe

### 4.1 Einlagern (Inbound Stock Workflow)
1. **Moduswahl:** Anwender befindet sich im Modus "Einlagern" (Standard bei Modulaufruf).
2. **Barcode-Erfassung:** Anwender richtet die Kamera auf den EAN-Barcode des Produkts oder gibt die EAN manuell ein.
3. **MHD-Erfassung:**
   * **Kamera/OCR (Standard):** Der Anwender zielt mit der Kamera im MHD-Modus auf das aufgedruckte Haltbarkeitsdatum. Das erkannte Datum wird automatisch in das Formularfeld übernommen.
   * **Manuelle Datumsauswahl (Alternative):** Der Anwender tippt auf den Kalender-Picker oder das Datumsfeld und wählt ein Datum manuell aus.
4. **Stammdatenabfrage:** Die App ruft `GET /scan/{barcode}` auf.
   * **Fall A (Produkt bekannt):** Produktname, Kategorie, Standard-Lagerort und Produktbild (falls vorhanden) werden geladen und im Formular vorausgefüllt.
   * **Fall B (Produkt neu / nicht im Stamm):** Die App meldet *"Neues Produkt"* und schaltet die Felder für Produktname, Marke, Standard-Lagerort, Kategorie und Produktbild zur manuellen Ersteingabe frei.
5. **Lagerort- & Mengenauswahl:**
   * Lagerort aus Dropdown wählen (Standard-Lagerort des Produkts ist vorausgewählt).
   * Menge eingeben oder per `+`/`-` Tasten anpassen (Standardwert: 1).
6. **Bestätigung:** Anwender tippt auf *"Einlagern"*.
7. **Abschluss:** Erfolgsmeldung (Toast/Snackbar) erscheint, Formular setzt sich zurück, Kamera ist bereit für den nächsten Scan.

### 4.2 Auslagern (Outbound Stock Workflow)
1. **Moduswahl:** Anwender schaltet in der AppBar auf den Modus "Auslagern" um.
2. **Barcode-Erfassung:** Anwender scannte den Barcode des zu entnehmenden Produkts.
3. **Bestandsprüfung:** Die App fragt `GET /scan/{barcode}` bzw. die spezifische Bestandsübersicht des Produkts ab.
   * **Fall A (Kein Bestand im Lager):** Die App zeigt den klaren Hinweis: *"Dieses Produkt ist aktuell nicht eingelagert."* Der Auslagern-Button bleibt deaktiviert.
   * **Fall B (Bestand vorhanden):** Die App listet die vorhandenen Bestandschargen mit ihren jeweiligen MHDs auf. 
4. **Mengenbestimmung:**
   * Der Anwender wählt die auszulagernde Menge.
   * **Validierung:** Die wählbare Menge ist strikt durch den tatsächlich verfügbaren Gesamtbestand des Produkts (bzw. der gewählten Charge) gedeckelt. Die `+`-Taste deaktiviert sich bei Erreichen der Höchstmenge.
5. **MHD- & Chargenauswahl (FEFO-Prinzip):**
   * Die Charge mit dem frühesten MHD wird automatisch als erste Charge ausgewählt.
   * Für jede zusätzlich benötigte Menge wird automatisch ein weiteres Dropdown-Feld zur Chargenauswahl eingeblendet.
   * Der Anwender kann die automatisch vorgeschlagene Charge bei Bedarf manuell über das jeweilige Dropdown ändern.
   * Dabei gelten folgende Regeln:
      - Eine Charge bzw. ein MHD darf nicht mehrfach ausgewählt werden, sofern davon nur ein Bestand vorhanden ist.
      - Bereits in einem anderen Dropdown ausgewählte Bestände werden in den übrigen Dropdowns nicht erneut angeboten.
      - Existieren mehrere Bestände mit demselben MHD, dürfen diese entsprechend ihrer tatsächlich vorhandenen Anzahl mehrfach ausgewählt werden.
      - Die Anzahl der auswählbaren Einträge ist stets durch den tatsächlich vorhandenen Bestand begrenzt.
      - Die automatische Vorauswahl erfolgt weiterhin nach dem FEFO-Prinzip, sofern mehrere Chargen zur Verfügung stehen.
6. **Aktion auswählen:** Der Anwender kann zwischen **„Auslagern“** und **„Öffnen“** wählen.
7. **Fall A – Auslagern:** Bei Auswahl von **„Auslagern“** wird der normale Auslagerungsvorgang fortgesetzt und anschließend abgeschlossen.
8. **Fall B – Öffnen:** Bei Auswahl von **„Öffnen“** erscheint ein Popup mit der Frage:
   > „Wie viele Tage ist das Produkt nach dem Öffnen haltbar?“
   Der Anwender gibt die gewünschte Anzahl an Tagen ein und bestätigt mit **„OK“**.
   Anschließend wird das Produkt zunächst ausgelagert und direkt wieder mit dem neu berechneten MHD eingelagert.
   Dabei wird geprüft, ob das neu berechnete MHD **nach dem ursprünglichen MHD** liegt.
   - **Neues MHD liegt nicht nach dem ursprünglichen MHD:**  
     Der Vorgang kann fortgesetzt und die neue Einlagerung durchgeführt werden.
   - **Neues MHD liegt nach dem ursprünglichen MHD:**  
     Der Vorgang wird unterbrochen und folgende Fehlermeldung angezeigt:
     > „Produkt kann nicht länger haltbar gemacht werden.“
     Anschließend stehen dem Anwender zwei Optionen zur Verfügung:
     - **„Anpassen“:** Die Anzahl der Tage kann erneut eingegeben werden.
     - **„Abbrechen“:** Der Vorgang wird beendet und das Formular zurückgesetzt.
9. **Abschluss:** Bei einer normalen Auslagerung wird die Buchung über `POST /inventory/consume` bzw. einen entsprechenden Batch-Consume-Request an das Backend übermittelt.
   Nach erfolgreicher Verarbeitung:
   - wird die Bestandsänderung bestätigt,
   - wird der aktualisierte Bestand übernommen,
   - und das Formular wird zurückgesetzt.
   Beim Vorgang **„Öffnen“** wird nach erfolgreicher Auslagerung zusätzlich die erneute Einlagerung mit dem berechneten MHD durchgeführt. Erst nach erfolgreicher Verarbeitung beider Vorgänge gilt der Prozess als abgeschlossen.

### 4.3 Barcode-Erfassung (Camera Barcode Scanning)
* **Kamera-Ansicht:** Zeigt einen zentrierten Sucherrahmen für Barcodes.
* **Scan-Verhalten:**
  * Unterstützte Formate: EAN-13, EAN-8, UPC-A, UPC-E.
  * Nach erfolgreicher Erkennung ertönt ein optisches/haptisches Signal (kurze Vibration/Flash).
  * Der erkannte Code wird im EAN-Eingabefeld eingetragen.
  * Die Kamera friert den Barcode-Stream ein oder geht nahtlos in die MHD-Phase über (konfigurierbarer Workflow).
* **Manuelle Re-Triggerung:** Neben dem EAN-Eingabefeld befindet sich ein Kamera-Button, um den Barcode-Scan jederzeit neu zu starten.

### 4.4 MHD-Erfassung per Kamera / OCR
* **Kamera-Ansicht:** Bietet einen schmalen, horizontal ausgerichteten Zielrahmen (Region of Interest / ROI) speziell für Datumsaufdrucke (z. B. `31.12.2026`, `2026-10-15`, `05/27`).
* **Erkennungslogik:**
  * Der Bildausschnitt im ROI wird auf gängige Datumsformate analysiert (`TT.MM.JJJJ`, `TT.MM.JJ`, `JJJJ-MM-TT`, `MM/YY`).
  * Sobald ein valides Datum erkannt wurde, wird es im Formular mit einem Bestätigungs-Checkmark angezeigt.
* **Vorschau- & Re-Scan:** Das aufgenommene MHD-Crop-Bild wird als kleine Vorschaukarte im Formular angezeigt. Ein Tap darauf öffnet die Kamera erneut zur Korrektur.

### 4.5 Produktabfrage und Produktanzeige
* **Live-Feedback:** Bei gültiger EAN (EAN-8 oder EAN-13 Format) startet die Abfrage automatisch (Debounce 300ms bei manueller Tippeingabe).
* **Ladezustand:** Während der API-Abfrage wird im Formular ein diskreter Lade-Spinner angezeigt.
* **Produktkarte:** Zeigt Produktbild, Produktname, Marke, Kategorie und die aktuelle Gesamtmenge im Lager an.

### 4.6 Manuelle Eingaben
* Jedes automatisch befüllte Feld (EAN, Produktname, MHD, Lagerort, Menge) muss vom Anwender jederzeit manuell überschreibbar sein.
* Für das MHD steht ein Kalender-Modal (DatePicker) zur Verfügung.
* Für Mengen stehen präzise Zahlenfelder und Inkrement/Dekrement-Buttons (`-` / `+`) bereit.

### 4.7 Debug-Modus
* **Aktivierung:** Über Einstellungen oder Entwickler-Toggle in der AppBar.
* **Funktionalitäten im Modul:**
  * Anzeige des rohen OCR-Erkennungstextes unterhalb des MHD-Feldes.
  * Einblendung der exakten Crop-Metriken (Auflösung, Bounding-Box, Skalierungsfaktor) des Kamera-Frames.
  * Anzeige des API-Response-Status (HTTP Status, Latenz, Endpoint-URL).
  * [Annahme] Im Debug-Modus können Test-EANs per Schnellwahl-Buttons eingegeben werden.

---

## 5. Datenmodell und benötigte Felder

### 5.1 Formulardaten (Client State: `InOutFormState`)

| Feldname | Datentyp | Pflichtfeld | Beschreibung |
| :--- | :--- | :--- | :--- |
| `mode` | Enum (`inbound`, `outbound`) | Ja | Aktueller Betriebsmodus des Moduls. |
| `ean` | String | Ja | Barcode (8 bis 14 Ziffern, alphanumerisch für Sondercodes). |
| `productName` | String | Ja (bei Einlagerung) | Name des Produkts. |
| `brand` | String | Nein | Marke / Hersteller. |
| `categoryId` | String / Int | Nein | Zuweisung der Produktkategorie. |
| `mhd` | DateTime / String | Ja (bei Einlagerung) | Mindesthaltbarkeitsdatum (`YYYY-MM-DD`). |
| `storageLocationId` | String / Int | Ja | ID des Ziel- oder Quell-Lagerorts. |
| `quantity` | Integer / Double | Ja | Ein- oder auszulagernde Stückzahl/Menge (Mindestens 1). |
| `productImagePath` | String (URI/Path) | Nein | Pfad oder URL zum Produktbild. |
| `mhdCropImagePath` | String (Local Path) | Nein | Pfad zum lokal erfassten OCR-Ausschnittbild für Debug/Kontrolle. |
| `selectedInventoryEntryId`| String / Int | Ja (bei Auslagerung) | ID der spezifischen Bestandscharge für die Entnahme. |

---

## 6. Validierungsregeln

1. **EAN-Validierung:**
   * Darf nicht leer sein, wenn eine Buchung durchgeführt werden soll.
   * Muss eine gültige Länge besitzen (EAN-8: 8 Zeichen, EAN-13: 13 Zeichen, UPC-A: 12 Zeichen) oder ein freies Textformat im Falle interner Barcodes aufweisen.
2. **MHD-Validierung (Einlagerung):**
   * Muss ein valides Kalenderdatum sein.
   * Warnhinweis (kein Block): Wenn das eingegebene MHD in der Vergangenheit liegt oder am selben Tag abläuft.
3. **Mengen-Validierung:**
   * `quantity` muss eine Ganzzahl $> 0$ sein.
   * **Einlagerung:** Keine Obergrenze.
   * **Auslagerung:** `quantity` $\le$ `verfügbarer Gesamtbestand` des Produkts bzw. der ausgewählten Charge.
4. **Lagerort-Validierung:**
   * Es muss ein gültiger Lagerort aus der Liste der verfügbaren Lagerorte ausgewählt sein.
5. **Produktname (Einlagerung bei neuem Produkt):**
   * Mindestens 2 Zeichen, darf nicht nur aus Leerzeichen bestehen.

---

## 7. Fehlerfälle und erwartetes Verhalten

| Fehlerfall | Ursache | Erwartetes Systemverhalten (UI / Client) |
| :--- | :--- | :--- |
| **HTTP 404 (Produkt nicht gefunden)** | Barcode ist dem Backend unbekannt (`GET /scan/{ean}`). | Formular schaltet automatisch in den Modus "Neues Produkt anlegen". Eingabefeld für Produktname wird fokussiert. Kein Absturz. |
| **HTTP 401 / Auth Token abgelaufen** | Session ungültig. | Abfangen durch zentralen HTTP-Client, automatischer Re-Auth-Versuch oder Weiterleitung auf Login-Screen mit Erhalt der Formulareingaben. |
| **Kein Netz / Backend offline** | Verbindungsabbruch. | Anzeige eines "Offline"-Banners. Speicherung der Buchung im lokalen Queue-Speicher (Offline-Support) [Annahme: sofern Offline-Queue aktiv] oder deutliche Fehlermeldung mit Wiederholen-Button. |
| **Kamera-Rechte verweigert** | Anwender sperrt Kamera-Berechtigung. | Statt Kamera-Preview wird ein Hinweistext mit Button "Berechtigung in Einstellungen öffnen" und direkter Umschaltung auf manuelle EAN-Eingabe angezeigt. |
| **OCR erkennt kein Datum / unleserlich** | Verschwommenes Aufdruck-Bild. | Nach 3 Sekunden erfolglosem OCR-Scan zeigt das UI den Hinweis: *"Datum unleserlich – bitte manuell wählen"* und öffnet den DatePicker. |
| **Auslagermenge > Bestand** | Anwender gibt manuell höhere Zahl ein. | Das Eingabefeld wird rot markiert, der "Auslagern"-Button wird deaktiviert. Meldung: *"Menge übersteigt aktuellen Bestand (Max: X)"*. |

---

## 8. UI-Prinzipien und Bedienabläufe

1. **Ein-Hand-Bedienung & Ergonomie:**
   * Haupt-Aktionsbuttons ("Einlagern", "Auslagern") befinden sich im untersten Drittel des Bildschirms (Thumb Zone).
   * Große Touch-Targets (mindestens 48x48 dp) für alle Buttons.
2. **Klares visuelles Feedback:**
   * Unterscheidbare Farbcodierung für die Modi:
     * **Einlagern:** Grüne/Blauakzente im Aktions-Button.
     * **Auslagern:** Orange/Warme Akzente im Aktions-Button.
   * Eindeutiges Lade-Feedback (Disable des Buttons + Progress Indicator während des Sendevorgangs, um Doppelbuchungen zu verhindern).
3. **Fokus-Steuerung & Auto-Advance:**
   * Nach erfolgreichem EAN-Scan springt der visuelle Fokus automatisch zum nächsten leeren Pflichtfeld (z. B. MHD oder Produktname).
4. **Kamera-Integration:**
   * Die Kamera wird als kollabierbares Modul im oberen Bereich der Seite dargestellt.
   * Nach vollständiger Datenerfassung klappt die Kamera ein, um den maximalen Platz für das Formular freizugeben.

---

## 9. Schnittstellen / Datenflüsse

Der Mobile Client kommuniziert ausschließlich über REST/JSON mit dem Backend. Das Modul nutzt folgende Endpunkte:

1. **`GET /scan/{barcode}`**
   * *Zweck:* Zentrale Produkt- & Bestandsabfrage für Barcode.
   * *Rückgabe:* Produktdaten (ID, Name, Bild-URL) + Auflistung bestehender Inventory-Entries (IDs, MHDs, Mengen, Lagerorte).
2. **`GET /storage-locations`**
   * *Zweck:* Laden der verfügbaren Lagerorte für Dropdowns.
3. **`POST /inventory`**
   * *Zweck:* Buchen einer neuen Einlagerung.
   * *Payload:* `{ product_id/ean, storage_location_id, mhd, quantity }`
4. **`POST /inventory/consume` oder `POST /inventory/entry/{id}/consume`**
   * *Zweck:* Buchen einer Auslagerung/Entnahme.
   * *Payload:* `{ inventory_entry_id / product_id, quantity, mhd }`

---

## 10. Akzeptanzkriterien pro Hauptfunktion

### AC-1: Barcode-Scan & Einlagerung bekanntes Produkt
* **GIVEN:** Das Produkt mit EAN `4001234567890` existiert im Backend Stamm.
* **WHEN:** Der Anwender scannt den Barcode im Modus "Einlagern", wählt das MHD `2027-06-30` via Kamera/OCR und klickt "Einlagern".
* **THEN:**
  1. Produktname und Bild werden korrekt geladen.
  2. `POST /inventory` wird mit den genauen Daten aufgerufen.
  3. Eine Erfolgsmeldung wird angezeigt.
  4. Das Formular wird geleert und steht für den nächsten Scan bereit.

### AC-2: Einlagerung neues Produkt (Ersterfassung)
* **GIVEN:** Der Barcode `9999999999999` ist dem Backend unbekannt (HTTP 404 auf `/scan/9999999999999`).
* **WHEN:** Der Anwender scannt den Barcode, gibt als Namen "Bio Hafermilch 1L" ein, wählt MHD und Lagerort und klickt "Einlagern".
* **THEN:**
  1. Das System zeigt ohne Absturz das Ersterfassungsformular.
  2. Das Produkt und der Bestand werden im Backend angelegt.
  3. Die App kehrt in den Bereitschaftszustand zurück.

### AC-3: Auslagerung nach FEFO-Prinzip
* **GIVEN:** Für Produkt X sind zwei Chargen vorhanden: Charge A (MHD: 10.10.2026, Menge: 2) und Charge B (MHD: 15.12.2026, Menge: 5).
* **WHEN:** Anwender schaltet auf "Auslagern" und scannt Produkt X.
* **THEN:**
  1. Das System schlägt automatisch Charge A (MHD 10.10.2026) vor.
  2. Die maximal auswählbare Menge ist auf 7 (Gesamtbestand) beschränkt.
  3. Nach verbrauchen Betätigung von Menge 1 wird genau 1 Stück von Charge A ausgebucht.

### AC-4: Auslagerung ohne Bestand
* **GIVEN:** Für Produkt Y existiert kein aktueller Bestand (Bestand = 0).
* **WHEN:** Anwender scannt Produkt Y im Modus "Auslagern".
* **THEN:**
  1. Das System zeigt den Hinweis *"Dieses Produkt ist aktuell nicht eingelagert"*.
  2. Der Button "Auslagern" ist deaktiviert.
  3. Es wird kein fehlerhafter API-Call ausgelöst.

### AC-5: OCR-Kamera-Verhalten & Korrektur
* **GIVEN:** Der Anwender befindet sich bei der MHD-Erfassung.
* **WHEN:** Die OCR-Erkennung liest ein falsches/unvollständiges Datum oder schlägt fehl.
* **THEN:**
  1. Der Anwender kann jederzeit das Datumsfeld antippen und im Kalender-Picker das korrekte Datum auswählen.
  2. Die manuelle Auswahl überschreibt den OCR-Wert vollständig.
 
### AC-6: Auslagerung mit Produktöffnung
* **GIVEN:** Für Produkt X sind zwei Chargen vorhanden: Charge A (MHD: 10.10.2026, Menge: 2) und Charge B (MHD: 15.12.2026, Menge: 5).
* **WHEN:** Anwender schaltet auf "Auslagern" und scannt Produkt X.
* **THEN:**
  1. Das System schlägt automatisch Charge A (MHD 10.10.2026) vor.
  2. Die maximal auswählbare Menge ist auf 7 (Gesamtbestand) beschränkt.
  3. Nach Öffnen Betätigung von Menge 1 und 3 Tage wird genau 1 Stück von Charge A ausgebucht.
  4. 1 Teil mit neuem Datum (MHD 13.10.2026) wird wieder eingelagert. Gesamtbestand unverändert auf 7

---

## 11. Offene Fragen / Annahmen

* **[Annahme 1]:** Das Backend liefert bei `GET /scan/{barcode}` bereits alle aktiven Chargen/Inventory-Entries des Produkts sortiert nach MHD mit, sodass der Mobile Client die FEFO-Auswahl ohne zusätzliche Folge-Requests berechnen kann.
* **[Annahme 2]:** Die Auslagerung von Mehrfachmengen über verschiedene MHD-Chargen hinweg (z. B. Entnahme von 3 Stück, wenn Charge A nur 1 Stück hat) wird vom Mobile Client in geordnete Einzelaufrufe aufgeteilt.
* **[Offene Frage 1]:** Soll nach einer erfolgreichen Ein- oder Auslagerung der Scan-Modus automatisch aktiv bleiben (Continuous Scanning for Einkaufsauspacken), oder ist eine explizite Bestätigung pro Artikel gewünscht? *(Spezifizierter Standard: Bestätigung + automatischer Formular-Reset im selben Modus)*.
* **[Offene Frage 2]:** Soll bei Auslagerung ein Grund für die Entnahme (z. B. "Verbraucht", "Abgelaufen/Müll", "Verschenkt") erfasst werden können? *(Aktuelle Spezifikation sieht vereinfachtes Auslagern ohne Pflichtgrund vor)*.

---

## 12. Abgrenzung zu Backend, Security und späterer Implementierung

1. **Keine Backend-Garantie im Client:** Der Mobile Client verlässt sich strikt auf die dokumentierten REST-Verträge. Fehlende oder abweichende Backend-Felder müssen gracefully abgefangen werden (Null-Safety, Fallbacks).
2. **Security & Governance:**
   * Sensible Daten (Passwörter, JWT-Tokens, API-Keys) dürfen unter keinen Umständen im UI, in Formular-States oder in Log-Outputs (Logcat/Console) ausgegeben oder gespeichert werden.
   * Der Debug-Modus zeigt ausschließlich technische Metadaten (Kamera, OCR-Text, HTTP-Status) und niemals Zugangsdaten.
3. **Implementierungs-Freigabe:**
   * Dieses Lastenheft dient als fachliche Grundlage für die nachfolgende Architektur-, Security- und QA-Bewertung (Apollo / Athena).
   * Keine Zeile Produktivcode im Mobile-Projekt wird vor der expliziten Freigabe dieses Lastenhefts durch den Projektleiter verändert.

---
*Ende des Lastenhefts `spec_t_lastenheft_inout_module.md`*
