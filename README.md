# FoodStock

FoodStock is a private, self-hosted food inventory management system for households.

The system is designed to manage food products, individual inventory units, expiration dates, storage locations, shopping lists and future recipe-assistance features.

The primary goals are:

-   Self-hosted operation
-   No mandatory cloud database
-   No Firebase dependency
-   Low recurring cost
-   Multiple household users
-   Secure remote access through VPN
-   Local barcode scanning
-   Local expiration-date OCR
-   Centralized server-side business logic
-   Reliable inventory transactions
-   English and German mobile application UI
-   English-only technical documentation
-   Long-term maintainability

## Application Names

The project consists of two clearly separated applications.

### FoodStock-Home

`FoodStock-Home` is the Home Assistant App running on the Raspberry Pi.

It contains the FoodStock backend and provides:

-   REST API
-   Business logic
-   Authentication and authorization
-   PostgreSQL connectivity
-   Product management
-   Inventory management
-   Shopping-list logic
-   Expiration-date calculations
-   Audit logging
-   File storage
-   Future Home Assistant integration

### FoodStock-Mobile

`FoodStock-Mobile` is the Android application used by household members.

It provides:

-   Barcode scanning
-   Product lookup
-   Product creation
-   Local OCR
-   Inventory management
-   Expiration-date management
-   Shopping-list management
-   Recipe prompt generation
-   Offline-first functionality
-   English and German UI

## Server

The server is a Raspberry Pi 4 with:

-   4 GB RAM
-   USB 3 SSD
-   Home Assistant OS
-   24/7 operation

The existing Home Assistant installation must remain unaffected.

FoodStock must not install a conventional Docker environment directly on the Home Assistant OS host.

## Database

PostgreSQL is the central relational database.

The current installation uses the existing PostgreSQL/TimescaleDB Home Assistant App.

FoodStock does not depend on Timescale-specific features during the initial implementation.

## Backend

The backend is implemented with FastAPI.

The backend is the only component allowed to communicate directly with PostgreSQL.

The Android application must never connect directly to PostgreSQL.

## Mobile Architecture

```text
FoodStock-Mobile
       |
       | HTTP
       |
       v
FoodStock-Home
       |
       v
FoodStock Backend
       |
       v
PostgreSQL
```

Barcode recognition and OCR happen locally on the Android device.

## Remote Access

Remote access is intended to use VPN.

Preferred initial model:

```text
Android
   |
   v
WireGuard / FRITZ!Box VPN
   |
   v
Home Network
   |
   v
Raspberry Pi
   |
   v
FoodStock-Home
```

No PostgreSQL port may be exposed to the Internet.

## Documentation Language

All technical documentation is written in English.

The mobile application supports:

-   English
-   German

The application language must be independent from the documentation language.

## Development Principle

FoodStock is developed incrementally.

No large batch of installation instructions should be given to the user.

Each implementation step follows:

1.  Goal
2.  What to click
3.  What to enter
4.  Expected result
5.  Test
6.  Only then continue to the next step

## Current Project Status

### Completed

-   Home Assistant OS environment assessed
-   PostgreSQL/TimescaleDB installed
-   Database `foodstock` created
-   PostgreSQL is not externally exposed
-   pgAdmin4 available for administration
-   GitHub repository operational
-   Home Assistant recognizes the FoodStock repository
-   FoodStock Home Assistant App installs successfully
-   ARM64 works
-   FastAPI starts
-   `/health` endpoint works
-   Database configuration works
-   PostgreSQL connectivity works
-   `SELECT 1` works
-   Beta update from `0.1.0` to `0.1.1` works

### Current Phase

## Phase 3 – FoodStock Backend and Home Assistant Interface

**Implemented – installation and functional testing on the Raspberry Pi are still pending.**

The current add-on version is **1.0.2** and includes:

-   ✅ **Home Assistant add-on for ARM64** with FastAPI and PostgreSQL connectivity.
-   ✅ **User authentication with JWT**, including user and administrator roles.
-   ✅ **Relational database tables** for products, individual stock units, storage locations, shopping lists, and change history.
-   ✅ **FIFO consumption** based on the earliest best-before date, support for negative stock levels, and centralized target/ideal stock-level logic.
-   ✅ **Automatic shopping list generation**, expiration overview, barcode lookup via Open Food Facts, and persistent product images stored under `/data/foodstock`.
-   ✅ **Home Assistant-compatible web interface** available at `http://<home-assistant-ip>:8000/ui/`, including login, dashboard, stock intake, consumption, expiration dates, shopping list, and **“Copy for AI”** functionality.
-   ✅ **`GET /ai/prompt`** generates a structured, free recipe-AI prompt directly from the current inventory.
-   ✅ **Complete FlutterFlow development specification** documented in `KiPromptAndroidApp.md`.

## Next Steps to Complete the App

### 1\. Update and test the add-on

Update FoodStock to version **1.0.2** in Home Assistant and configure secure database credentials, a dedicated JWT secret, and the initial administrator account according to `foodstock/README.md`.

Then test the following endpoints from the home network:

-   `/health`
-   `/docs`
-   `/ui/`

### 2\. Test the database and user interface

At minimum:

-   Create one storage location.
-   Create one product.
-   Add a stock unit with a best-before date.
-   Verify FIFO consumption.
-   Verify automatic shopping list generation.

Only after these tests have been completed should the real inventory data be entered.

### 3\. Set up backups

Configure automated backups of the PostgreSQL database dump and `/data/foodstock` to a second storage target.

Afterwards, perform a **test restoration** to verify that the backup can actually be recovered successfully.

### 4\. Secure external access

External access should only be provided through the **FRITZ!Box WireGuard VPN**.

PostgreSQL must **never be exposed directly to the internet**. Before distributing the external app, HTTPS should be configured through a suitable reverse proxy or ingress.

### 5\. Build the FlutterFlow app

Use `KiPromptAndroidApp.md` as the development specification.

Configure the API base URL for access through the home network/VPN and test the following workflows on an Android device:

-   Login
-   Barcode scanning
-   OCR
-   Offline synchronization

### 6\. Future enhancements

Possible later extensions include:

-   Optional storage of photos of best-before dates.
-   Direct integration with a paid AI service.
-   Meal planning.
-   Home Assistant dashboard and notification integration.

## Project Rule

The architecture defined in the project specification is binding.

Any fundamental architectural change requires explicit approval before implementation.

A proposed change must explain:

1.  What is changing
2.  Why it is better
3.  Advantages
4.  Disadvantages
5.  Additional costs
6.  Migration impact
