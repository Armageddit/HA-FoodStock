# KI-Prompt: FlutterFlow-Android-App für FoodStock

Kopiere den folgenden Prompt vollständig in dein KI-Werkzeug für die Erstellung der FlutterFlow-App.

---

Erstelle eine **Android-App mit FlutterFlow** namens **FoodStock** für eine Familie. Die App ist ausschließlich ein Client für ein bereits vorhandenes, selbst gehostetes FoodStock-Backend. **Kein Firebase, keine direkte PostgreSQL-Verbindung und keine lokale Cloud-Datenbank verwenden.**

## API-Vertrag

Die konfigurierbare Basis-URL lautet `https://<foodstock-host>:8000`. Für die Entwicklung kann sie als App-State-Variable `apiBaseUrl` gespeichert werden. Alle geschützten API-Aufrufe verwenden den Header `Authorization: Bearer <accessToken>`.

Anmeldung:

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
username=<Benutzername>&password=<Passwort>
```

Die Antwort enthält `access_token`. Speichere ihn verschlüsselt/lokal als `accessToken`. Prüfe beim App-Start `GET /auth/me`; bei HTTP 401 lösche das Token und zeige die Anmeldung.

Wichtige Endpunkte:

* `GET /dashboard` → Kennzahlen `inventory_units`, `expiring.expired`, `expiring.urgent`, `expiring.soon`, `expiring.upcoming`, `shopping_items`.
* `GET /products` → Produkte inklusive abgeleitetem Feld `stock`.
* `GET /scan/{barcode}` → erst lokale Produktdatenbank, sonst Vorschlag von Open Food Facts.
* `POST /products` → neues Produkt.
* `POST /inventory` → `{product_id, quantity, expiration_date, storage_location_id, client_operation_id}`.
* `POST /products/{id}/consume` → `{quantity, reason, client_operation_id}`. Nie einen neuen Gesamtbestand berechnen oder an die API senden.
* `GET /expiring?days=14` → aktive Einzelbestände mit MHD.
* `GET/PATCH /shopping-list` → automatische Einkaufsliste und Status `needed`, `on_list`, `purchased`, `stocked`.
* `GET /storage-locations` → auswählbare Lagerorte.
* `GET /ai/prompt` → `{prompt}` für die Zwischenablage.

Für **jede schreibende Offline-Aktion** erzeugt die App vorher eine UUID als `client_operation_id`. Speichere die Anfrage bei Verbindungsfehler lokal in einer Warteschlange und sende sie bei nächster Verbindung mit derselben UUID erneut. Dadurch ist die Wiederholung sicher und wird auf dem Server nicht doppelt gebucht.

## Seiten und Navigation

Erstelle eine Material-3-Oberfläche auf Deutsch mit einer Bottom Navigation:

1. **Startseite**: große Scan-Schaltfläche, Karten für Anzahl Lebensmittel, abgelaufene/dringende Lebensmittel und Einkaufsartikel. Daten aus `/dashboard`.
2. **Scannen**: Barcode wird auf dem Smartphone lokal mit der Kamera erkannt. Übergib nur die Barcode-Ziffern an `GET /scan/{barcode}`. Bei bekanntem Produkt: Produktname, Menge (Standard 1), vorgeschlagener Lagerort, MHD-Schritt und Speichern. Bei unbekanntem Produkt: vorausgefülltes Formular mit Open-Food-Facts-Vorschlag und manueller Produktanlage.
3. **Bestand**: Suchbares Produktverzeichnis, aktueller Bestand, Produktdetail und gut sichtbare Schaltfläche **„Verbraucht“**. Diese ruft immer `POST /products/{id}/consume` auf. Der Server verwendet FIFO nach ältestem MHD.
4. **Bald ablaufend**: Liste aus `/expiring?days=14`, mit Farbcodes: abgelaufen rot, 0–3 Tage rot/orange, 4–7 Tage orange, 8–14 Tage gelb.
5. **Einkaufsliste**: Menge, Einheit, Status und Checkbox/Auswahl. Änderung per `PATCH /shopping-list/{product_id}`. Der Bedarf und die Menge werden nicht in FlutterFlow berechnet.
6. **Rezeptvorschläge**: Button **„Für KI kopieren“**, lädt `/ai/prompt` und kopiert exakt das Feld `prompt` in die Zwischenablage. Keine kostenpflichtige KI-API in Version 1.
7. **Einstellungen**: API-Basis-URL, Abmelden und Anzeige des angemeldeten Benutzers.

Für Admins (Feld `role == "admin"` aus `/auth/me`) zeige zusätzlich eine Admin-Seite mit Produkt-, Lagerort- und Benutzerverwaltung.

## Scan- und MHD-Ablauf

Der optimale Ablauf lautet: **Barcode scannen → Produkt prüfen → Menge → MHD fotografieren → Datum bestätigen → Lagerort → Speichern**.

Barcode-Erkennung und OCR laufen ausschließlich lokal auf dem Android-Smartphone. Verwende für OCR eine FlutterFlow Custom Action mit Google ML Kit Text Recognition. Zeige über dem Kamerabild einen rechteckigen MHD-Rahmen. Suche im erkannten Text deutsche Datumsformen wie `15.09.2026`, `15/09/26` und `2026-09-15`.

**OCR-Datum niemals automatisch speichern.** Zeige immer „Erkanntes Datum: …“ mit **Übernehmen** und **Ändern**. Bei unsicherer oder fehlender Erkennung öffne sofort einen manuellen Date Picker. Das Original-MHD-Foto wird standardmäßig verworfen. Eine spätere optionale Upload-Funktion ist möglich, aber nicht Bestandteil der ersten FlutterFlow-Version.

## Offline- und UX-Regeln

* Cache lokal: zuletzt geladene Produkte, Lagerorte, Bestand, Einkaufslisten- und Dashboarddaten.
* Scanner und OCR funktionieren ohne Netzwerk.
* Zeige bei Offline-Modus klar „Wird synchronisiert“ und die Anzahl wartender Aktionen.
* Verwende keine direkte Bestandsüberschreibung. Jede Änderung ist ein Befehl an den Server (`inventory`, `consume`, `correct`).
* Bei HTTP 401 zur Anmeldung zurückkehren; bei anderen Fehlern eine verständliche deutsche Fehlermeldung mit Wiederholen-Schaltfläche anbieten.
* Der externe Zugriff erfolgt über VPN; die App speichert niemals PostgreSQL-Zugangsdaten oder das JWT-Secret.

Erstelle die API-Calls, App-State-Variablen, Seiten, Formulare, Validierungen und die Offline-Warteschlangen-Struktur so, dass die App sofort mit diesem FoodStock-Backend verbunden werden kann.

