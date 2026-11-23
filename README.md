# Heroes REST API

The Heroes REST API is a cloud-native service for managing information about heroes and figures from mythological, literary, and historical sources. It provides the ability to create, retrieve, update, delete, purge, and count hero records through HTTP requests.

The API was developed using Python and Azure Functions, with Azure SQL Database used for persistent data storage. It is designed to provide a centralized way of managing hero information while incorporating authentication, administrator authorization, automated validation, and application monitoring.

**Deployed API:**  
https://midtermappferna-hpaue6aqe5fvgkej.northcentralus-01.azurewebsites.net/api

**GitHub Repository:**  
https://github.com/fernandesjakem-a11y/Heroes-REST-API

## Features

- **CRUD Operations:** Create, retrieve, update, and delete individual hero records.
- **Persistent Storage:** Uses Azure SQL Database to store information across application restarts.
- **Authentication:** Uses Azure Functions Function Keys and a separate API Key to authenticate requests.
- **Administrator Authorization:** Sensitive operations require an additional Admin API Key.
- **Batch Validation:** Automatically checks whether heroes have at least one associated literary or historical source.
- **Automated Execution:** Uses Azure Logic Apps to schedule validation operations and send email notifications.
- **Application Monitoring:** Uses Application Insights and OpenTelemetry to record API requests, failures, custom events, and database dependency activity.
- **Azure Dashboard:** Provides an overview of API health, request activity, security, automation, and incident investigation.

## Architecture

The application uses several Azure services that work together to handle requests, store information, and monitor operations.

| Component | Purpose |
|---|---|
| Azure Functions | Hosts the Python REST API and handles HTTP requests. |
| Azure SQL Database | Stores hero records and their associated aliases and sources. |
| Azure Key Vault | Securely stores API credentials. |
| Managed Identity | Allows the Function App to access Key Vault without storing its access credentials in application code. |
| Azure Logic Apps | Automatically executes scheduled batch validation and sends notifications. |
| Application Insights | Records requests, failures, custom events, and dependency activity. |
| OpenTelemetry | Provides instrumentation and tracing for application operations. |
| Azure Dashboard | Displays application health, security, automation, and operational information. |

### Database Structure

The database uses primary keys, foreign keys, and relational constraints to maintain the relationships between records. It consists of four relational tables:

- **Heroes:** Stores the main hero information, including name, status, culture, historical period, description, and needs_review.
- **HeroAliases:** Stores alternative names associated with each hero.
- **Sources:** Stores unique literary and historical source titles.
- **HeroSources:** Connects heroes to their associated sources through foreign keys.

## Authentication and Security

All API endpoints require two authentication credentials. Sensitive administrative operations require an additional credential.

### 1. Azure Functions Function Key

The API uses Function-level authorization (`AuthLevel.FUNCTION`). Requests must include a valid Function Key through the `x-functions-key` HTTP header.

This credential is validated by the Azure Functions runtime before the request reaches the application.

### 2. API Key

A separate API Key must be supplied through the `x-api-key` HTTP header. The application retrieves the expected value from Azure Key Vault.

### 3. Admin API Key

The Admin API Key provides an additional authorization requirement for sensitive operations. It is required for:

- `DELETE /heroes/purge`
- `PATCH /heroes/validate`

Requests that provide valid standard authentication credentials but do not provide the required administrator credential are rejected with HTTP 403 Forbidden.

### Required Headers

```http
x-functions-key: YOUR_FUNCTION_KEY
x-api-key: YOUR_API_KEY
x-admin-api-key: YOUR_ADMIN_API_KEY
```

## API Endpoints

The API currently supports seven operations.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/heroes` | Creates a new hero record. |
| GET | `/heroes` | Retrieves all hero records or a specific hero. |
| PUT | `/heroes?id={id}` | Updates an existing hero. |
| DELETE | `/heroes?id={id}` | Deletes an individual hero. |
| DELETE | `/heroes/purge` | Deletes all hero records. |
| GET | `/heroes/counts` | Returns the total number of heroes. |
| PATCH | `/heroes/validate` | Performs batch validation on all hero records. |

### Hero Data Structure

Each hero is represented by a JSON object containing an ID and seven main fields.

```json
{
  "id": 1,
  "name": "Odysseus",
  "aliases": [
    "Ulysses",
    "King of Ithaca",
    "Son of Laertes"
  ],
  "status": "Mythical",
  "culture": "Ancient Greek",
  "sources": [
    "The Iliad by Homer",
    "The Odyssey by Homer"
  ],
  "historical_period": "Greek Mythological Heroic Age",
  "description": "Odysseus is the legendary king of Ithaca and a central hero of Homer's Odyssey."
}
```

The `needs_review` field is also maintained in the database and is used by the batch validation operation.

## Batch Validation

One of the main features of this project is the batch validation operation.

The `PATCH /heroes/validate` endpoint evaluates every hero record stored in the Azure SQL Database and checks whether it has at least one associated literary or historical source.

The validation rule works as follows:

- If a hero has no associated sources, `needs_review` is set to `true`.
- If a hero has at least one associated source, `needs_review` is set to `false`.

The endpoint returns the number of records that were modified, along with a UTC timestamp indicating when the validation operation completed.

Example response:

```json
{
  "updatedCount": 1,
  "timestamp": "2026-11-21T21:27:01Z"
}
```

This helps identify incomplete hero records and makes it easier to maintain supporting source information across the database.

The endpoint requires the Admin API Key because it performs batch modifications to database records.

## HTTP Response Codes

| Status Code | Meaning |
|---|---|
| 200 | Request completed successfully. |
| 201 | Resource successfully created. |
| 400 | Invalid request or JSON input. |
| 401 | Authentication failed. |
| 403 | Administrator authorization required or access forbidden. |
| 404 | Requested resource not found. |
| 500 | Internal server error. |