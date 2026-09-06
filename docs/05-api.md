-   #### ChatGPT:
    
    Yes. I checked **`docs/05-api.md` directly against the current FastAPI implementation**. This file is quite outdated, especially regarding the API prefix and several endpoint names.
    
    # `docs/05-api.md`
    
    ## 1\. API Base Path
    
    ### Current documentation
    
    The document currently states:
    
    ```text
    /api/v1/
    ```
    
    for all endpoints.
    
    ### Current implementation
    
    The FastAPI application currently defines the endpoints **without an `/api/v1` prefix**.
    
    For example:
    
    ```text
    GET /health
    GET /dashboard
    GET /products
    GET /inventory
    POST /auth/token
    ```
    
    The application itself is created without a global `/api/v1` router prefix. 
    
    ### Required change
    
    The documentation must remove `/api/v1` from all current endpoint paths.
    
    This is the single biggest issue in `05-api.md`.
    
    * * *
    
    # 2\. System Endpoints
    
    The documentation currently lists:
    
    ```text
    GET /api/v1/health
    GET /api/v1/ready
    ```
    
    The actual implementation provides:
    
    ```text
    GET /
    GET /health
    GET /database-configured
    GET /dashboard
    ```
    
    There is currently **no `/ready` endpoint**.
    
    ### Current behavior
    
    ```text
    GET /
    ```
    
    returns application information and API version.
    
    ```text
    GET /health
    ```
    
    also verifies database connectivity.
    
    ```text
    GET /database-configured
    ```
    
    is a compatibility endpoint used during initial add-on setup and returns database connection information, but never passwords. 
    
    This needs to be documented.
    
    * * *
    
    # 3\. Authentication
    
    The current documentation describes:
    
    ```text
    POST /auth/login
    POST /auth/refresh
    POST /auth/logout
    GET  /auth/me
    ```
    
    This is incorrect.
    
    The actual endpoints are:
    
    ```text
    POST /auth/token
    GET  /auth/me
    ```
    
    The login endpoint uses FastAPI's OAuth2 password form:
    
    ```text
    username
    password
    ```
    
    and returns a JWT access token.
    
    There is currently **no refresh-token endpoint** and **no logout endpoint**.
    
    ### Correct flow
    
    ```text
    POST /auth/token
            ↓
    JWT access token
            ↓
    Authorization: Bearer <token>
            ↓
    Protected endpoints
    ```
    
    * * *
    
    # 4\. Token Lifetime
    
    The current implementation uses:
    
    ```text
    JWT_EXPIRES_HOURS
    ```
    
    with a default of:
    
    ```text
    168 hours
    ```
    
    which equals seven days.
    
    This is useful API documentation and should be included.
    
    The documentation should also mention that the JWT contains:
    
    ```text
    sub
    role
    exp
    ```
    
    * * *
    
    # 5\. Users API
    
    The current implementation provides:
    
    ```text
    GET   /users
    POST  /users
    PATCH /users/{user_id}
    ```
    
    There is currently **no**:
    
    ```text
    GET /users/{id}
    DELETE /users/{id}
    ```
    
    endpoint.
    
    User listing and modification are administrator-only.
    
    Creating a user is also administrator-only.
    
    The update endpoint can modify:
    
    -   password
    -   role
    -   active state
    
    There is also a protection preventing an administrator from deactivating their own account.
    
    * * *
    
    # 6\. Storage Locations
    
    The documentation currently lists:
    
    ```text
    GET    /storage-locations
    POST   /storage-locations
    GET    /storage-locations/{id}
    PATCH  /storage-locations/{id}
    DELETE /storage-locations/{id}
    ```
    
    The actual implementation provides:
    
    ```text
    GET   /storage-locations
    POST  /storage-locations
    PATCH /storage-locations/{location_id}
    ```
    
    There is currently **no GET-by-ID endpoint** and **no DELETE endpoint**.
    
    The GET endpoint only returns active storage locations.
    
    Creating and modifying storage locations requires administrator privileges.
    
    * * *
    
    # 7\. Products API
    
    The product section is mostly correct in concept, but the paths need to lose `/api/v1`.
    
    The current endpoints are:
    
    ```text
    GET    /products
    GET    /products/{product_id}
    POST   /products
    PATCH  /products/{product_id}
    DELETE /products/{product_id}
    ```
    
    There is also:
    
    ```text
    POST /products/{product_id}/image
    ```
    
    which is missing from the current API documentation. 
    
    ### Authorization
    
    The current implementation has an important distinction:
    
    ```text
    GET products        → authenticated user
    POST products       → authenticated user
    PATCH product       → admin
    DELETE product      → admin
    POST product image  → admin
    ```
    
    The documentation should reflect this.
    
    * * *
    
    # 8\. Product Deletion
    
    The current `DELETE /products/{product_id}` endpoint does **not** physically delete the product.
    
    It sets:
    
    ```text
    active = false
    ```
    
    and returns:
    
    ```json
    {
      "status": "deactivated",
      "id": 123
    }
    ```
    
    So the existing documentation's statement about deactivation is correct in principle.
    
    It should simply be updated to the actual endpoint and response behavior.
    
    * * *
    
    # 9\. Barcode Lookup
    
    The current documentation describes:
    
    ```text
    POST /barcodes/lookup
    ```
    
    This endpoint does not exist.
    
    The actual endpoint is:
    
    ```text
    GET /scan/{barcode}
    ```
    
    The request therefore looks like:
    
    ```text
    GET /scan/4001234567890
    ```
    
    rather than a JSON POST body.
    
    * * *
    
    # 10\. External Product Lookup
    
    The documented:
    
    ```text
    POST /products/enrich
    ```
    
    endpoint does not exist.
    
    External enrichment is currently integrated directly into:
    
    ```text
    GET /scan/{barcode}
    ```
    
    The lookup process is:
    
    ```text
    Barcode
       ↓
    Local Product Lookup
       │
       ├── Found → return local product
       │
       └── Not found
              ↓
         Open Food Facts
              ↓
          Suggestion
    ```
    
    The external result is returned as a suggestion and does not automatically create a local product.
    
    * * *
    
    # 11\. Product Images
    
    The current implementation supports:
    
    ```text
    POST /products/{product_id}/image
    ```
    
    Only administrators can upload product images.
    
    Supported content types are:
    
    ```text
    image/jpeg
    image/png
    image/webp
    ```
    
    The maximum upload size is:
    
    ```text
    10 MB
    ```
    
    The image is stored under the configured FoodStock data directory, and the relative path is stored in the product record. 
    
    This should be added to `05-api.md`.
    
    * * *
    
    # 12\. Inventory API
    
    The current documentation contains:
    
    ```text
    GET  /inventory
    GET  /inventory/{id}
    POST /inventory
    ```
    
    The actual implementation only provides:
    
    ```text
    GET  /inventory
    POST /inventory
    ```
    
    There is currently no:
    
    ```text
    GET /inventory/{id}
    ```
    
    endpoint.
    
    * * *
    
    # 13\. Inventory Filtering
    
    The current:
    
    ```text
    GET /inventory
    ```
    
    endpoint supports:
    
    ```text
    status_filter
    ```
    
    with the default:
    
    ```text
    active
    ```
    
    For example:
    
    ```text
    GET /inventory?status_filter=consumed
    ```
    
    This should be documented because it is part of the actual API.
    
    The returned inventory data includes:
    
    ```text
    id
    product_id
    product_name
    unit
    quantity
    expiration_date
    storage_location_id
    status
    ```
    
    
    
    * * *
    
    # 14\. Inventory Consumption
    
    The documented endpoint:
    
    ```text
    POST /inventory/consume
    ```
    
    does not exist.
    
    The actual endpoint is:
    
    ```text
    POST /products/{product_id}/consume
    ```
    
    
    
    Example:
    
    ```text
    POST /products/42/consume
    ```
    
    with a request body containing the consumption information.
    
    The server performs FEFO selection and locks the relevant inventory rows during the operation.
    
    * * *
    
    # 15\. Inventory Correction
    
    The documented:
    
    ```text
    POST /inventory/corrections
    ```
    
    does not exist.
    
    The actual endpoint is:
    
    ```text
    POST /products/{product_id}/correct
    ```
    
    and it is administrator-only. 
    
    The correction uses a `quantity_delta`.
    
    For example:
    
    ```json
    {
      "quantity_delta": 3,
      "reason": "Physical stock count"
    }
    ```
    
    or:
    
    ```json
    {
      "quantity_delta": -2,
      "reason": "Damaged products"
    }
    ```
    
    A correction of zero is rejected.
    
    * * *
    
    # 16\. Idempotency
    
    This section needs an important correction.
    
    The current API does **not** use:
    
    ```text
    Idempotency-Key
    ```
    
    as documented.
    
    Instead, the request schemas use:
    
    ```text
    client_operation_id
    ```
    
    The backend checks whether that operation has already been processed.
    
    So the documentation should use:
    
    ```json
    {
      "client_operation_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    
    rather than:
    
    ```text
    Idempotency-Key: ...
    ```
    
    This distinction is important because it is part of the actual request body/API model.
    
    * * *
    
    # 17\. Expiring Inventory
    
    The current endpoint is:
    
    ```text
    GET /expiring
    ```
    
    not:
    
    ```text
    GET /inventory/expiring
    ```
    
    It supports:
    
    ```text
    days
    ```
    
    with:
    
    ```text
    default = 14
    minimum = 0
    maximum = 365
    ```
    
    
    Example:
    
    ```text
    GET /expiring?days=30
    ```
    
    The results contain active inventory with an expiration date within the requested period.
    
    * * *
    
    # 18\. Shopping List
    
    The current API provides:
    
    ```text
    GET /shopping-list
    PATCH /shopping-list/{product_id}
    ```
    
    There are no current endpoints for:
    
    ```text
    POST /shopping-list/items
    DELETE /shopping-list/items/{id}
    POST /shopping-list/items/{id}/purchase
    POST /shopping-list/items/{id}/add-to-inventory
    ```
    
    The shopping list is therefore considerably simpler than the API currently documented.
    
    The PATCH endpoint changes the status of the product's shopping-list entry.
    
    * * *
    
    # 19\. Transactions
    
    The old documentation describes a generic audit API:
    
    ```text
    GET /audit-events
    GET /audit-events/{id}
    ```
    
    This does not exist.
    
    The actual endpoint is:
    
    ```text
    GET /transactions
    ```
    
    It supports:
    
    ```text
    limit
    ```
    
    with:
    
    ```text
    default = 100
    minimum = 1
    maximum = 500
    ```
    
    Example:
    
    ```text
    GET /transactions?limit=200
    ```
    
    The response contains transaction information together with product and username information.
    
    * * *
    
    # 20\. Files API
    
    The documented:
    
    ```text
    POST   /files
    GET    /files/{id}
    DELETE /files/{id}
    ```
    
    does not exist.
    
    There is no generic file API in the current implementation.
    
    Product images are handled specifically through:
    
    ```text
    POST /products/{product_id}/image
    ```
    
    Therefore the generic Files section should be removed from the current API documentation.
    
    * * *
    
    # 21\. AI / Recipe Endpoint
    
    The current documentation completely misses an implemented endpoint:
    
    ```text
    GET /ai/prompt
    ```
    
    It requires authentication and returns:
    
    ```json
    {
      "prompt": "..."
    }
    ```
    
    The prompt is generated server-side from the current inventory.
    
    This endpoint definitely belongs in `05-api.md`.
    
    * * *
    
    # 22\. Dashboard Endpoint
    
    Another missing endpoint is:
    
    ```text
    GET /dashboard
    ```
    
    It is authenticated and returns dashboard-oriented information including:
    
    ```text
    inventory_units
    expiring
    shopping_items
    ```
    
    The expiration information is divided into:
    
    ```text
    expired
    urgent
    soon
    upcoming
    ```
    
    The current implementation evaluates expiration information for the next 14 days.
    
    This should be documented.
    
    * * *
    
    # 23\. Response Format
    
    The old documentation proposes a universal response structure:
    
    ```json
    {
      "error": {
        "code": "INVALID_REQUEST",
        "message": "The request is invalid."
      }
    }
    ```
    
    That is **not the current API contract**.
    
    The implementation uses FastAPI's `HTTPException` behavior and returns normal JSON response models/dictionaries depending on the endpoint. 
    
    We should therefore **not document a universal custom error envelope** unless we implement one first.
    
    * * *
    
    # 24\. Synchronization API
    
    The current documentation lists:
    
    ```text
    GET /sync
    POST /sync/operations
    ```
    
    Neither endpoint exists.
    
    The backend currently provides `client_operation_id`\-based idempotency, but **does not implement a synchronization API**.
    
    Therefore this entire section should be moved to:
    
    ```text
    Future API
    ```
    
    or removed.
    
    * * *
    
    # 25\. Current API Overview
    
    The final API documentation should reflect approximately this endpoint structure:
    
    ```text
    System
    GET    /
    GET    /health
    GET    /database-configured
    GET    /dashboard
    
    Authentication
    POST   /auth/token
    GET    /auth/me
    
    Users
    GET    /users
    POST   /users
    PATCH  /users/{user_id}
    
    Storage Locations
    GET    /storage-locations
    POST   /storage-locations
    PATCH  /storage-locations/{location_id}
    
    Products
    GET    /products
    GET    /products/{product_id}
    POST   /products
    PATCH  /products/{product_id}
    DELETE /products/{product_id}
    POST   /products/{product_id}/image
    
    Barcode
    GET    /scan/{barcode}
    
    Inventory
    GET    /inventory
    POST   /inventory
    POST   /products/{product_id}/consume
    POST   /products/{product_id}/correct
    GET    /expiring
    
    Shopping List
    GET    /shopping-list
    PATCH  /shopping-list/{product_id}
    
    Transactions
    GET    /transactions
    
    AI
    GET    /ai/prompt
    ```
    
    This reflects the current FastAPI route definitions.
