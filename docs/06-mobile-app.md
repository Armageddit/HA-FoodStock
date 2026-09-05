# FoodStock-Mobile

## 1\. Purpose

FoodStock-Mobile is the Android client for the FoodStock system.

The application is designed for fast household use.

## 2\. Technology

FlutterFlow is the primary UI development environment.

Custom Dart code may be used where FlutterFlow's standard functionality is insufficient.

Typical custom-code areas include:

-   Barcode integration
-   OCR integration
-   Offline queue
-   Secure token handling
-   Specialized camera UI
-   Synchronization

FlutterFlow supports Custom Actions and native integrations for such extensions.

## 3\. Application Name

The Android application name is:

```text
FoodStock-Mobile
```

The Home Assistant application must remain clearly separate:

```text
FoodStock-Home
```

## 4\. Main Navigation

Recommended navigation:

```text
Home
Scan
Inventory
Expiring
Shopping List
Recipes
Locations
Settings
```

Administrators additionally see:

```text
Admin
```

## 5\. Home Screen

The home screen should prioritize actions rather than information density.

Recommended layout:

```text
My Food Stock

[ Scan Product ]

126 items
4 expiring soon
8 shopping-list items

[ Inventory ]
[ Shopping List ]

[ Expiring Soon ]
[ Recipe Suggestions ]
```

The exact visual design may evolve during UX implementation.

## 6\. Scan Workflow

Normal workflow:

```text
Scan barcode
    |
    v
Product recognized
    |
    v
Quantity
    |
    v
Expiration date
    |
    v
Confirm date
    |
    v
Storage location
    |
    v
Save
```

For known products:

```text
Barcode
  |
  v
Known product
  |
  v
Default storage location
  |
  v
Expiration date
  |
  v
Save
```

## 7\. Barcode Scanning

Barcode recognition occurs on-device.

Only the barcode value is sent to the server.

The backend does not receive the camera stream.

## 8\. OCR Workflow

The expiration-date camera should provide a visual guide.

Example:

```text
+-----------------------------+
|                             |
|     Place expiration date   |
|          here               |
|                             |
|      +---------------+      |
|      | 15.09.2026    |      |
|      +---------------+      |
|                             |
|            [Camera]         |
+-----------------------------+
```

OCR analyzes the captured image locally.

## 9\. OCR Confirmation

If OCR detects:

```text
15.09.2026
```

the application displays:

```text
Detected expiration date

15.09.2026

[Use date]
[Change]
```

If recognition is uncertain:

```text
The expiration date could not be recognized reliably.

[Select date manually]
```

The user must always be able to correct the date.

## 10\. Expiration Images

The default behavior is:

```text
Capture
 -> OCR
 -> Confirm
 -> Delete image
```

The user may explicitly choose to keep the original image.

## 11\. Unknown Products

If the barcode is unknown:

```text
Unknown product

Product name
Manufacturer
Product image
Storage location
Minimum stock
Ideal stock

[Save Product]
```

The new product becomes part of the local FoodStock product database.

## 12\. Offline Mode

The application should cache:

-   Products
-   Storage locations
-   Relevant inventory
-   Shopping list
-   User settings

Barcode scanning and OCR remain local.

Mutating operations are placed into an offline queue if the server is unavailable.

## 13\. Offline Queue

Example:

```text
Operation ID
Operation type
Entity ID
Payload
Created at
Retry count
Status
```

The queue is synchronized when connectivity returns.

## 14\. Conflict Handling

Absolute quantity replacement must not be used for concurrent inventory mutations.

Bad:

```text
Set quantity = 4
```

Good:

```text
Consume one unit
```

The backend processes the operation transactionally.

## 15\. Language Support

The application supports:

```text
English
German
```

The user's preferred language should persist across sessions.

## 16\. Localized Dates

Dates must respect the selected locale.

The underlying API representation remains unambiguous.

Expiration dates should be represented as date-only values.

## 17\. Recipe Export

The first recipe feature is:

```text
Generate recipe prompt
        |
        v
Copy to clipboard
```

No external AI service is required.

## 18\. Permissions

The application requests permissions only when necessary.

Potential permissions:

-   Camera
-   Photo access

The application must explain why a permission is required before requesting it where appropriate.

## 19\. Security

The application must not store:

-   PostgreSQL credentials
-   Backend database credentials
-   Administrative passwords

Access tokens must be stored using an appropriate secure mobile mechanism.

## 20\. UX Principle

The most common task should be possible with minimal interaction:

```text
Scan
 -> confirm
 -> save
```

The application should avoid unnecessary forms and repeated questions.
