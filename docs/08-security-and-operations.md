# Security and Operations

## 1\. Security Goals

FoodStock must protect:

-   Household inventory information
-   User credentials
-   Product data
-   Product and expiration images
-   Inventory transaction history
-   Database credentials
-   API access tokens
-   Application configuration and secrets

The backend is designed as a private, authenticated REST API intended to run within a trusted Home Assistant environment.

Security must be enforced by the backend and must never depend solely on client-side UI restrictions.

* * *

## 2\. PostgreSQL Security

PostgreSQL is the application's persistent database.

PostgreSQL should:

-   Remain on the private network
-   Never be exposed directly to the Internet
-   Never be directly accessible by FoodStock-Mobile
-   Use a dedicated FoodStock database
-   Use dedicated database credentials
-   Use the minimum required database permissions

FoodStock-Mobile communicates with the FoodStock API, not directly with PostgreSQL.

```text
FoodStock-Mobile
       |
       | HTTPS / private network / VPN
       v
FoodStock API
       |
       | PostgreSQL connection
       v
PostgreSQL
```

The FoodStock application does not configure the host firewall or PostgreSQL network exposure. These are deployment responsibilities.

* * *

## 3\. Home Assistant Deployment Security

FoodStock is intended to run as a Home Assistant application/add-on.

The deployment should follow Home Assistant security principles:

-   Avoid host networking unless explicitly required
-   Avoid privileged containers
-   Keep AppArmor protection enabled
-   Request only required directory mappings
-   Avoid unnecessary Home Assistant API permissions
-   Avoid Docker API access
-   Avoid unnecessary host filesystem access

These are deployment requirements rather than controls enforced by the FastAPI application itself.

The application should operate with the smallest practical set of permissions.

* * *

## 4\. Authentication

FoodStock authenticates users individually.

The current authentication endpoint is:

```text
POST /auth/token
```

The endpoint uses the OAuth2 password form:

```text
username
password
```

A successful authentication returns a JWT access token:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Authenticated requests use:

```text
Authorization: Bearer <JWT>
```

The current API does not implement refresh tokens or a separate logout endpoint.

* * *

## 5\. JWT Security

FoodStock uses signed JWT access tokens with the HS256 algorithm.

The token contains:

```text
sub
role
exp
```

Where:

-   `sub` identifies the authenticated user
-   `role` contains the user's current role at token creation time
-   `exp` defines the token expiration time

The token expiration period is configurable using:

```text
JWT_EXPIRES_HOURS
```

The default value is:

```text
168 hours
```

which corresponds to seven days.

Tokens must:

-   Be generated using a secure secret
-   Expire
-   Never be written to logs
-   Never be committed to source control
-   Never be transmitted as URL parameters

* * *

## 6\. JWT Secret Requirements

The application requires a custom JWT secret.

Startup is rejected if:

-   `JWT_SECRET` is missing
-   The default placeholder secret is used
-   The secret is shorter than 32 characters

The default placeholder value must never be used in a production deployment.

Example:

```text
JWT_SECRET=<random secret of at least 32 characters>
```

Secrets should be supplied through the deployment environment or an appropriate secret-management mechanism.

They must not be stored in the source repository.

* * *

## 7\. Authorization

Authorization is enforced server-side.

The current roles are:

```text
user
admin
```

The backend resolves the authenticated user from the JWT and then verifies that the user still exists and is active.

An inactive user cannot access authenticated endpoints even if they possess a previously issued token.

Administrator-only operations are checked by the backend.

Examples:

```text
USER
  can:
    - authenticate
    - access inventory
    - consume inventory
    - add inventory
    - create products

ADMIN
  can additionally:
    - manage users
    - modify users
    - manage storage locations
    - modify products
    - deactivate products
    - upload product images
    - correct inventory
    - view transaction history
```

The exact permissions are defined by the API implementation.

The mobile application may hide administrator functions, but hiding a UI element is never considered authorization.

* * *

## 8\. Password Storage

Passwords must never be stored in plaintext.

The current implementation uses Python's standard-library `scrypt` implementation.

The current parameters are:

```text
N = 16384
r = 8
p = 1
dklen = 32
salt = 16 random bytes
```

Stored hashes use the following format:

```text
scrypt$16384$8$1$<salt>$<digest>
```

Password verification uses a constant-time digest comparison.

Passwords must never appear in:

-   Logs
-   API responses
-   Database exports
-   Source control
-   Backup filenames
-   URLs

* * *

## 9\. User Password Requirements

The API requires passwords to contain at least 12 characters when users are created or passwords are changed.

The current API also limits passwords to a maximum of 128 characters.

The initial administrator account follows the same minimum password length requirement.

The first application startup requires an initial administrator username and a password of at least 12 characters when no users exist yet.

* * *

## 10\. Initial Administrator

The first administrator can be initialized through:

```text
INITIAL_ADMIN_USERNAME
INITIAL_ADMIN_PASSWORD
```

On startup:

1.  FoodStock checks whether users already exist.
2.  If no users exist, valid initial administrator credentials are required.
3.  The password is hashed using the application's scrypt implementation.
4.  The user is created with the `admin` role.

The initial password is never returned by the API.

After initialization, normal user management is performed through the authenticated API.

* * *

## 11\. HTTPS

Production API traffic should be protected by HTTPS.

The current FastAPI application does not itself provide a production TLS termination layer.

TLS should therefore be handled by the deployment architecture where required, for example through:

-   A reverse proxy
-   A Home Assistant ingress mechanism
-   A VPN/private network
-   Another trusted TLS termination layer

The exact deployment model depends on how FoodStock-Mobile accesses the API.

For remote access, unencrypted HTTP over the public Internet must not be used.

* * *

## 12\. VPN and Remote Access

Remote access should initially use a private VPN such as WireGuard.

A possible deployment model is:

```text
FoodStock-Mobile
       |
       | WireGuard VPN
       v
Private Home Network
       |
       v
FoodStock API
       |
       v
PostgreSQL
```

PostgreSQL must never be exposed directly to the Internet.

No port forwarding to PostgreSQL is allowed.

If the FoodStock API is exposed outside the private network, the deployment must provide appropriate transport security and access control.

* * *

## 13\. Firewall Principle

Only required services should be reachable.

The desired security boundary is:

```text
Internet
   |
   X
PostgreSQL


Internet
   |
   X
FoodStock API
   |
   | only if explicitly exposed
   v
TLS / VPN / trusted access layer
   |
   v
FoodStock API
   |
   v
PostgreSQL
```

The exact firewall rules are deployment-specific and are not configured by the FastAPI application.

* * *

## 14\. Database Credentials

Database credentials must be provided through configuration rather than hardcoded into the application source.

They must:

-   Not be committed to source control
-   Not be included in API responses
-   Not be written to application logs
-   Not be embedded in mobile application code
-   Be changed if they are accidentally exposed

The `/database-configured` endpoint intentionally exposes database connection metadata only.

It does not return the database password.

* * *

## 15\. Application Data

The application uses the configured:

```text
FOODSTOCK_DATA_DIR
```

directory.

The default is:

```text
/data/foodstock
```

The application creates these directories:

```text
/data/foodstock/products
/data/foodstock/expiration-images
/data/foodstock/backups
/data/foodstock/exports
```

Product images are stored under the product storage directory.

Application data should be protected using appropriate filesystem permissions.

* * *

## 16\. Image Upload Security

Product image uploads are restricted to:

```text
image/jpeg
image/png
image/webp
```

The maximum accepted image size is:

```text
10 MB
```

Unsupported media types are rejected.

Oversized uploads are rejected.

Uploaded files are stored in the FoodStock data directory and their relative path is stored with the product.

Image files must not be treated as executable application content.

* * *

## 17\. API Security

Authenticated API endpoints require a valid JWT.

The backend validates:

1.  Token signature
2.  Token expiration
3.  User identity
4.  User existence
5.  User active status
6.  Administrator role where required

Invalid or expired tokens result in an authentication failure.

Administrator-only operations return an authorization failure when performed by a normal user.

* * *

## 18\. Transaction and Inventory Integrity

Inventory changes are performed server-side.

Clients must not directly manipulate calculated stock values.

Operations such as:

```text
Add inventory
Consume inventory
Correct inventory
```

are handled by backend commands.

Inventory consumption uses database row locking when selecting active inventory records.

This prevents concurrent operations from incorrectly consuming the same inventory.

The resulting inventory change and transaction record are committed together.

* * *

## 19\. Idempotency

Inventory mutation requests can contain:

```text
client_operation_id
```

This value is a UUID generated by the client.

The backend stores the operation ID with the resulting transaction.

If the same operation ID is submitted again, the backend detects the previously processed operation and avoids applying the operation twice.

Example:

```text
Mobile Client
      |
      | client_operation_id = UUID
      v
FoodStock API
      |
      +-- Operation already processed?
      |        |
      |        +-- Yes → return already_applied
      |
      +-- No
           |
           v
      Apply operation
           |
           v
      Store transaction
```

This is particularly important for mobile applications that may retry requests after network failures.

* * *

## 20\. Inventory Transaction History

Inventory operations create transaction records.

Transactions contain information such as:

```text
product_id
inventory_id
user_id
event
quantity_delta
reason
client_operation_id
created_at
```

This provides an operational history of inventory changes.

This should not be confused with a generic application-wide audit system.

The current implementation does not provide a separate generic `audit_events` system.

* * *

## 21\. Backups

A complete backup should include all data required to restore the FoodStock installation.

At minimum:

-   PostgreSQL database
-   Product images
-   Expiration images, if used
-   Relevant FoodStock configuration
-   Important application data

The exact backup procedure depends on the deployment environment.

Database backups and filesystem backups should be coordinated so that a restore results in a consistent application state.

* * *

## 22\. Backup Locations

The Raspberry Pi SSD must not be the only copy of important FoodStock data.

A recommended setup is:

```text
Primary
   |
   +-- Raspberry Pi SSD

Secondary
   |
   +-- Separate physical storage

Optional
   |
   +-- Off-site or cloud backup
```

At least one backup copy should be stored separately from the primary system.

* * *

## 23\. Restore Testing

A backup is not considered reliable until it has been successfully restored.

Restore tests should verify:

-   PostgreSQL data
-   Product data
-   Inventory data
-   Shopping-list data
-   Transaction history
-   Product images
-   Application configuration

After restoration, verify that the API can start and authenticated users can access their data.

* * *

## 24\. Database Initialization and Recovery

The current application does not use Alembic migrations.

During application startup, SQLAlchemy initializes the database schema using:

```python
Base.metadata.create_all(engine)
```

Therefore the current recovery process must not include a step such as:

```text
Run database migrations
```

The current recovery flow is:

```text
Restore Home Assistant
        |
        v
Restore FoodStock application
        |
        v
Restore PostgreSQL
        |
        v
Restore FoodStock files
        |
        v
Start FoodStock
        |
        v
Verify database initialization
        |
        v
Verify API
        |
        v
Verify mobile application
```

If a versioned database migration system is introduced in the future, this procedure must be updated accordingly.

* * *

## 25\. Updates

Updates should follow this sequence:

```text
Backup
   |
   v
Record current version
   |
   v
Update
   |
   v
Start application
   |
   v
Health check
   |
   v
API test
   |
   v
Application test
```

Before an update, verify:

-   Home Assistant is operational
-   PostgreSQL is operational
-   FoodStock is operational
-   Sufficient disk space is available
-   Sufficient memory is available
-   A recent backup exists

After an update, verify:

-   Home Assistant
-   FoodStock
-   PostgreSQL
-   Authentication
-   Product access
-   Inventory access
-   Critical Home Assistant applications

* * *

## 26\. Home Assistant Protection

Before installing or updating FoodStock:

-   Verify that Home Assistant is operational.
-   Verify that critical existing applications are operational.
-   Record the current FoodStock version.
-   Record PostgreSQL status.
-   Check available storage.
-   Check available memory.
-   Confirm that a recent backup exists.

FoodStock changes should not unnecessarily modify unrelated Home Assistant services.

* * *

## 27\. Resource Monitoring

FoodStock is intended to run on resource-constrained hardware such as a Raspberry Pi.

The deployment should monitor:

-   RAM usage
-   CPU usage
-   SSD usage
-   Database size
-   Application logs
-   Container resource usage

Unnecessary services should not be added to the deployment.

The backend is intentionally designed as a small, self-contained FastAPI service.

* * *

## 28\. Logging

Production logging should remain reasonably small.

Logs must:

-   Rotate
-   Avoid unnecessary debug output
-   Avoid logging credentials
-   Avoid logging passwords
-   Avoid logging JWT access tokens
-   Avoid logging database passwords
-   Avoid logging other application secrets

Errors should contain enough information for troubleshooting without exposing sensitive data.

* * *

## 29\. Security Boundaries

The main security boundaries are:

```text
                    ┌──────────────────┐
                    │ FoodStock-Mobile │
                    └────────┬─────────┘
                             │
                             │ Authenticated API
                             v
                    ┌──────────────────┐
                    │   FoodStock API  │
                    │     FastAPI      │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │                  │
                    v                  v
             ┌──────────────┐   ┌──────────────┐
             │  PostgreSQL  │   │ File Storage │
             └──────────────┘   └──────────────┘
```

The mobile application never receives direct database credentials.

The mobile application never accesses PostgreSQL directly.

The backend is responsible for authentication, authorization, validation and inventory business logic.

* * *

## 30\. Security Principles

The following principles apply to all FoodStock components:

1.  Authentication must be server-side.
2.  Authorization must be server-side.
3.  Passwords must never be stored in plaintext.
4.  Secrets must never be committed to source control.
5.  JWT access tokens must expire.
6.  Tokens and passwords must never be logged.
7.  PostgreSQL must remain private.
8.  Client applications must never access PostgreSQL directly.
9.  Inventory mutations must be validated and executed by the backend.
10.  Inventory mutations should support safe retries through `client_operation_id`.
11.  Uploaded files must be validated and size-limited.
12.  Backups must be stored separately from the primary system.
13.  Backups must be tested through actual restoration.
14.  Operational security must not depend solely on client-side UI restrictions.

* * *

## 31\. Future Security Improvements

The following are not currently implemented and should therefore be treated as future improvements rather than current functionality:

-   Versioned database migrations
-   Generic application-wide audit logging
-   Refresh-token support
-   Dedicated session management
-   Centralized secret management
-   Automated backup scheduling
-   Automated restore testing
-   Automated security scanning
-   Formal rate limiting
-   Advanced role/permission management
-   Automated TLS certificate management

Future features must not be documented as current functionality until they are implemented and tested.

This version should now be used as the **replacement for `08-security-and-operations.md`**. It deliberately separates **current implementation** from **deployment/security requirements and future improvements**, so it should stay accurate as the project evolves.

G![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Fraw.githubusercontent.com&sz=128)Quellen
