# FoodStock Localization

## 1\. Scope

FoodStock has two application languages:

-   English
-   German

Technical documentation remains English-only.

## 2\. Application Names

The application names do not change with language.

Home Assistant:

```text
FoodStock-Home
```

Android:

```text
FoodStock-Mobile
```

## 3\. Default Language

The application should initially follow the Android/device language.

Supported application locales:

```text
en
de
```

If another device language is selected, English should be used as the fallback.

## 4\. Manual Language Selection

Settings must provide:

```text
Language

English
Deutsch
```

The selected language must persist.

## 5\. Translation Rules

All user-visible strings must be translatable.

Do not hardcode user-visible text inside custom Dart code where a localization mechanism can be used.

## 6\. Examples

| English          | German                   |   |   |   |
|------------------|--------------------------|---|---|---|
| Home             | Startseite               |   |   |   |
| Scan             | Scannen                  |   |   |   |
| Inventory        | Bestand                  |   |   |   |
| Expiring Soon    | Bald ablaufend           |   |   |   |
| Shopping List    | Einkaufsliste            |   |   |   |
| Locations        | Lagerorte                |   |   |   |
| Settings         | Einstellungen            |   |   |   |
| Administration   | Administration           |   |   |   |
| Product          | Produkt                  |   |   |   |
| Manufacturer     | Hersteller               |   |   |   |
| Expiration Date  | Mindesthaltbarkeitsdatum |   |   |   |
| Storage Location | Lagerort                 |   |   |   |
| Quantity         | Menge                    |   |   |   |
| Consume          | Verbrauchen              |   |   |   |
| Add to Inventory | In Bestand übernehmen    |   |   |   |
| Purchased        | Gekauft                  |   |   |   |
| Needed           | Benötigt                 |   |   |   |
| Use Date         | Datum übernehmen         |   |   |   |
| Change           | Ändern                   |   |   |   |
| Save             | Speichern                |   |   |   |
| Cancel           | Abbrechen                |   |   |   |
| Unknown Product  | Unbekanntes Produkt      |   |   |   |
| Expired          | Abgelaufen               |   |   |   |
| Urgent           | Dringend                 |   |   |   |
| Soon             | Bald                     |   |   |   |
| Upcoming         | Demnächst                |   |   |   |

## 7\. German Terminology

The application should use:

```text
MHD
```

where appropriate for familiar German users.

For explanatory text:

```text
Mindesthaltbarkeitsdatum (MHD)
```

The German application must not use awkward literal translations.

## 8\. English Terminology

The preferred English term is:

```text
expiration date
```

rather than repeatedly using technical terminology such as:

```text
expiry timestamp
```

because the value is a date rather than a timestamp.

## 9\. Translation Testing

Every release must be tested in:

-   English
-   German

Testing must include:

-   Long German labels
-   Buttons
-   Dialogs
-   Error messages
-   Dates
-   Empty states
-   Permission explanations
-   Admin pages

## 10\. Backend Language Policy

API error codes should be language-neutral.

Example:

```text
PRODUCT_NOT_FOUND
```

The mobile application may translate the error code into the user's language.

This prevents backend localization from becoming coupled to the mobile UI.

## 11\. Documentation

All technical documentation, source comments intended for developers, API documentation and architecture documentation are written in English.
