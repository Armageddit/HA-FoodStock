# Security and Operations

## 1\. Security Goals

FoodStock must protect:

-   Household inventory information
-   User credentials
-   Product data
-   Images
-   Audit history
-   Database credentials
-   API tokens

## 2\. PostgreSQL

PostgreSQL must:

-   Remain internal
-   Not be Internet-facing
-   Not be directly reachable by FoodStock-Mobile
-   Use a dedicated FoodStock database
-   Use dedicated credentials
-   Use least-privilege permissions

## 3\. FoodStock-Home

The Home Assistant App should:

-   Avoid host networking
-   Avoid privileged mode
-   Keep AppArmor enabled
-   Request only required directory mappings
-   Avoid Home Assistant API permissions unless required
-   Avoid Docker API access
-   Avoid host filesystem access

Home Assistant's current app security guidance explicitly recommends avoiding host networking, using AppArmor and limiting mapped folders and API permissions.

## 4\. Authentication

Users authenticate individually.

There must be no shared hardcoded administrator password.

The backend must determine the user's role from authenticated server-side identity information.

## 5\. Authorization

Authorization is enforced server-side.

Examples:

```text
USER
  can consume inventory

ADMIN
  can correct inventory
```

The mobile UI may hide administrator functions, but hiding a button is never considered authorization.

## 6\. Password Storage

Passwords must be stored as secure password hashes.

Plaintext passwords are prohibited.

## 7\. Tokens

Access tokens:

-   Must be generated securely
-   Must expire
-   Must not be logged
-   Must not be stored in source control
-   Must not be included in URLs

## 8\. HTTPS

The production API should be accessed through HTTPS.

The exact certificate strategy will be finalized before external mobile access is enabled.

A reverse-proxy/TLS layer is a possible solution, but should not be added until required.

## 9\. VPN

Remote access should initially use the FRITZ!Box/WireGuard VPN.

No direct public PostgreSQL exposure is allowed.

No port forwarding to PostgreSQL is allowed.

## 10\. Firewall Principle

Only required services should be reachable.

Expected model:

```text
Internet
   X
PostgreSQL

Internet
   X
FoodStock API

VPN
   |
   v
FoodStock API
```

## 11\. Backups

Backups must include:

-   PostgreSQL database
-   Product images
-   Optional expiration images
-   FoodStock configuration
-   Important application data

## 12\. Backup Locations

The Raspberry Pi SSD must not be the only backup location.

Preferred:

```text
Primary:
Raspberry Pi SSD

Secondary:
Separate physical storage
```

An off-device backup is strongly recommended.

## 13\. Restore Testing

A backup is not considered reliable until it has been restored successfully.

Restore tests should be performed periodically.

## 14\. Updates

Updates must follow this order:

```text
Backup
   |
   v
Test
   |
   v
Update
   |
   v
Health check
   |
   v
Application test
```

## 15\. Existing Home Assistant Protection

Before FoodStock changes:

-   Verify Home Assistant is operational
-   Verify existing apps are operational
-   Record FoodStock version
-   Record PostgreSQL status
-   Record available storage
-   Record available memory

After each installation/update:

-   Check Home Assistant
-   Check FoodStock-Home
-   Check PostgreSQL
-   Check existing critical apps

## 16\. Resource Monitoring

The Raspberry Pi has only 4 GB RAM.

FoodStock must therefore avoid unnecessary services.

Monitor:

-   RAM
-   CPU
-   SSD usage
-   Database size
-   Application logs
-   Container resource usage

## 17\. Logging

Logs must rotate.

The application must not continuously write large debug logs in production.

## 18\. Disaster Recovery

The recovery procedure should eventually be documented as:

```text
Install Home Assistant OS
        |
        v
Restore Home Assistant
        |
        v
Restore FoodStock-Home
        |
        v
Restore PostgreSQL
        |
        v
Restore FoodStock files
        |
        v
Run database migrations
        |
        v
Verify API
        |
        v
Verify mobile application
```
