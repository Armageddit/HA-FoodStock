# Localization

## Language Policy

Technical documentation is English only.

The mobile application should support:

-   English
-   German

Application language must be independent from documentation language.

## User Interface

User-visible strings must not be hard-coded into business logic.

The mobile application should use Android/Flutter localization mechanisms.

Examples:

```text
inventory
expiration date
storage location
shopping list
consume
add stock
correct stock
```

must have localized resources.

## Dates

Dates shown to users must follow the selected locale.

The API should use machine-readable ISO date formats.

For example:

```text
2026-09-20
```

The client is responsible for locale-specific display formatting.

## Units

The product `unit` is currently stored as a string.

The current backend default is:

```text
Stück
```

If the mobile application introduces a controlled unit system, this should be treated as a future data-model decision rather than silently assuming a fixed enum today.

## Error Messages

Clients should not use server error text as localization keys.

Server errors are technical responses.

The mobile application should map stable HTTP status codes and, when introduced, stable application error codes to localized messages.
