# Security and Operations

## Threat Model

FoodStock is intended for private household use.

The primary security goals are:

-   protect household inventory data
-   prevent unauthorized inventory changes
-   protect user credentials
-   prevent direct database access
-   avoid exposing secrets
-   prevent accidental Internet exposure

## Network Security

PostgreSQL must not be exposed to the Internet.

Remote application access should use:

-   VPN
-   or another explicitly secured HTTPS access layer

The application should not assume that a private LAN is automatically secure.

## Authentication

Authentication uses JWT access tokens.

Tokens must:

-   have an expiration time
-   be transmitted only over a trusted connection
-   never be logged
-   never be stored in source control

The JWT secret must be unique to the installation.

## Password Security

Passwords are stored as hashes.

Passwords must never appear in:

-   logs
-   API responses
-   database dumps in plain text
-   configuration examples
-   source code

## Configuration Secrets

Database credentials and JWT secrets must be supplied through protected configuration.

The default placeholder JWT secret must never be used for a real installation.

A future hardening step should explicitly reject known placeholder secrets during startup.

## Product Image Uploads

The current API accepts:

-   JPEG
-   PNG
-   WebP

The upload size is limited to 10 MB.

Files are stored under the FoodStock data directory using generated product-based filenames.

The current implementation validates the declared MIME type.

Content-level image validation is a future hardening improvement.

## Database Security

The FoodStock database user should have only the permissions required by the application.

PostgreSQL administration credentials must not be used by the application.

## Backups

A production household installation should back up:

1.  PostgreSQL data
2.  FoodStock image files

Backups must be stored separately from the primary storage.

A restore test is required.

A backup that has never been restored successfully must not be considered verified.

## Logging

Logs must not expose:

-   passwords
-   JWT secrets
-   bearer tokens
-   database passwords
-   complete sensitive request bodies

Structured logging and request IDs are recommended future improvements.

## Operational Health

Current health endpoint:

```text
GET /health
```

A future readiness endpoint may distinguish:

```text
process is running
```

from:

```text
database is ready
```
