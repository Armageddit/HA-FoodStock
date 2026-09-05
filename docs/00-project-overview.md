# FoodStock Project Overview

## 1\. Purpose

FoodStock is a private household food inventory management system.

The system maintains a central inventory shared by multiple household users.

The application is designed to answer:

-   What food do we have?
-   Where is it stored?
-   How many units are available?
-   What expires soon?
-   What has already expired?
-   What needs to be purchased?
-   What should be consumed first?
-   Which products should be added to the shopping list?
-   Which foods can be used for recipes?

## 2\. Primary Goals

The system must:

-   Be self-hosted
-   Store household data locally
-   Avoid mandatory cloud databases
-   Support multiple users
-   Provide secure authentication
-   Support role-based authorization
-   Support barcode scanning
-   Support local OCR
-   Support expiration-date confirmation
-   Support individual inventory units
-   Support storage locations
-   Support shopping lists
-   Support negative inventory
-   Provide audit history
-   Support offline mobile operation
-   Support future Home Assistant integration
-   Support future direct AI integration

## 3\. Non-Goals for the Initial Release

The following are deliberately postponed:

-   Direct paid AI integration
-   Automatic meal planning
-   Advanced nutritional analysis
-   Public sharing of inventory
-   Multi-household cloud synchronization
-   Internet-facing PostgreSQL
-   Complex Home Assistant dashboards
-   Automatic image recognition of food without barcode scanning

## 4\. Product Names

| Component |	Official Name |
|-----------|-----------|
| Home Assistant App |	FoodStock-Home |
| Android Application |	FoodStock-Mobile |
| Backend |	FoodStock Backend |
| Database |	PostgreSQL|
| Repository |	FoodStock |


## 5\. Language Policy

Technical documentation:

-   English only

Mobile application:

-   English
-   German

The application should initially follow the Android/device language.

Users must also be able to select the language manually.

## 6\. Design Principles

### Server-side business logic

Inventory calculations, shopping-list calculations, permissions and transactional inventory operations belong to the backend.

The mobile client must not duplicate critical business rules.

### Offline-first mobile behavior

The mobile application should remain useful when the server is temporarily unavailable.

Local operations are queued and synchronized later.

### Transactional inventory

Inventory modifications must be represented as server-side operations rather than blind client-side quantity replacements.

### Minimal user interaction

The normal scan workflow should require as few user interactions as possible.

### Safe automation

OCR must never silently create an expiration date without user confirmation.

### Privacy

Food inventory data remains under household control.

No external cloud service is required for normal operation.

## 7\. Current State

The backend foundation is already functional.

Phase 3 therefore focuses on structure and maintainability rather than replacing the existing backend.
