# FoodStock Backend 1.0.2

Dieses Add-on stellt die private, authentifizierte REST-API für FoodStock bereit.
PostgreSQL bleibt ausschließlich innerhalb des Home-Assistant-Add-on-Netzwerks; die Android-App spricht nur diese API an.

## Einmalige Add-on-Konfiguration

Öffne **Einstellungen → Add-ons → FoodStock → Konfiguration** und ersetze vor dem Start mindestens diese Werte:

```yaml
database_host: 77b2833f-timescaledb
database_port: 5432
database_name: foodstock
database_user: foodstock_app
database_password: <PostgreSQL-Passwort>
jwt_secret: <zufälliger-geheimer-Wert-mit-mindestens-32-Zeichen>
initial_admin_username: admin
initial_admin_password: <neues-Admin-Passwort-mit-mindestens-12-Zeichen>
jwt_expires_hours: 168
```

Erzeuge den `jwt_secret` zum Beispiel auf dem Windows-Entwicklungsrechner mit `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Der Start wird absichtlich abgebrochen, solange der Secret-Wert kürzer als 32 Zeichen ist. Nach dem ersten erfolgreichen Start ist der Bootstrap-Administrator in der Datenbank angelegt. Setze anschließend `initial_admin_password` wieder auf einen leeren Wert und starte das Add-on neu; dies verhindert, dass dieses Passwort weiter in der Add-on-Konfiguration liegt.

Version 1.0.2 verwendet für neue Passwörter den sicheren, in Python enthaltenen `scrypt`-Algorithmus. Dadurch besteht keine Abhängigkeit von `passlib`/`bcrypt`, die mit dem aktuellen Python-3.14-Image nicht kompatibel sind. Da der bisherige Add-on-Start beim ersten Administrator fehlgeschlagen ist, wurden dabei noch keine alten Benutzerpasswörter angelegt.

## Persistenter Speicher

Das Add-on nutzt ausschließlich das von Home Assistant vorgesehene, persistente `/data`-Verzeichnis. Die integrierte Verwaltungsoberfläche ist nach dem Start direkt im Home-Assistant-Menü **FoodStock** (Ingress) und im Heimnetz unter `http://<Home-Assistant-IP>:8000/ui/` erreichbar:

```
/data/foodstock/products/
/data/foodstock/expiration-images/
/data/foodstock/backups/
/data/foodstock/exports/
```

Produktbilder werden mit `POST /products/{id}/image` als JPEG, PNG oder WebP hochgeladen. MHD-Fotos werden in Version 1.0 bewusst noch nicht hochgeladen: die OCR bleibt auf dem Smartphone und ein Foto wird standardmäßig verworfen.

## API und App-Vertrag

Nach `POST /auth/token` (Formfelder `username`, `password`) muss jede App-Anfrage den Header `Authorization: Bearer <access_token>` tragen. Die interaktive vollständige OpenAPI-Dokumentation steht unter `/docs` bereit.

Wichtige Endpunkte: `GET/POST/PATCH /products`, `DELETE /products/{id}` (Deaktivierung), `GET /scan/{barcode}`, `POST /inventory`, `POST /products/{id}/consume`, `POST /products/{id}/correct`, `GET/PATCH /shopping-list`, `GET /expiring`, `GET/POST/PATCH /storage-locations`, `GET/POST/PATCH /users` und `GET /transactions` (Admin).

Für offline gespeicherte schreibende Vorgänge sendet die App eine eigene UUID als `client_operation_id`. Derselbe Vorgang kann damit sicher wiederholt werden, ohne den Bestand zweimal zu verändern. Verbrauch und Korrekturen sind serverseitige Transaktionen; der Server wählt beim Verbrauch die aktive Einheit mit dem frühesten MHD und erzeugt bei Bedarf eine `missing`-Einheit, wodurch negative Bestände korrekt dargestellt werden.

## Sicherheitsbetrieb

* PostgreSQL-Port nicht veröffentlichen; die Datenbank ist nur für FoodStock im Add-on-Netzwerk bestimmt.
* Den API-Port nur im Heimnetz und extern ausschließlich über das WireGuard-VPN der FRITZ!Box verwenden. Für den Produktivbetrieb vor der Android-Verteilung HTTPS über einen geeigneten Home-Assistant-Ingress/Reverse-Proxy aktivieren.
* Sichere Passwörter, regelmäßig aktualisierte Add-ons und mindestens ein externes Backup der PostgreSQL-Datenbank **und** von `/data/foodstock` verwenden. Eine Wiederherstellung regelmäßig testen.
