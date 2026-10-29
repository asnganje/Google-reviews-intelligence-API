# Google Reviews Intelligence API

## 1. Project Overview

### Purpose

A backend-only API project that accepts requests for business review data, collect available data from a configured and authorized source, normalize the results, perform rating analytics, and return structured JSON responses.

The system will focus on backend API design and development, data collection, web scraping, data processing and storage.

### Primary Goals

- Develop a professional REST API using FastAPI.
- Implement a modular data collection system using Scrapy and Playwright where appropriate.
- Accept business identifiers, names, locations, and supported listing URLs.
- Extract and normalize available business and review information.
- Calculate rating distributions from accessible individual review records.
- Support review filtering and structured responses.
- Document and test the API through Swagger.
- Containerize and deploy the application when the core functionality is stable.

## 2. Initial Scope

### Included

- Business identification and lookup.
- Configurable data-source integration.
- Review collection and parsing.
- Rating validation and normalization.
- Business rating statistics.
- Review search and filtering.
- Pagination.
- Collection status and error reporting.
- API authentication and usage limits in a later milestone.
- PostgreSQL integration where appropriate and permitted.
- Docker support and deployment.

## 3. Proposed API Functionalities

### 3.1 Business Lookup

Allow clients to identify a business using supported identifiers.

Potential inputs:

- Business name.
- Location.
- Google Maps URL.
- Place identifier.

Expected output:

- Business name.
- Address or location, when available.
- Geographic coordinates, when available.
- Source identifier.
- Source listing URL.
- Overall rating, when available.
- Total review count, when available.

### 3.2 Review Collection

Collect review records from the configured source.

Potential review fields:

- Source review identifier.
- Rating.
- Review text.
- Publication date.
- Language, when available.
- Reviewer metadata, when permitted and available.
- Source URL.

The collector must distinguish between missing information and information that genuinely does not exist.

### 3.3 Rating Analytics

Calculate statistics from the review records available to the application.

Potential metrics:

- Average rating of the collected review sample.
- Number of collected five-star reviews.
- Number of collected four-star reviews.
- Number of collected three-star reviews.
- Number of collected two-star reviews.
- Number of collected one-star reviews.
- Total number of collected records.
- Rating percentages.

The API must distinguish between statistics calculated from collected records and aggregate statistics reported by the source.

A partial collection must never be presented as a complete representation of all reviews.

### 3.4 Review Search and Filtering

Support filters where the configured source and collected data permit them.

Potential filters:

- Minimum and maximum rating.
- Star rating.
- Publication date range.
- Search keywords.
- Language.
- Review sorting.

### 3.5 Collection Status

Provide information about collection operations.

Potential fields:

- Collection identifier.
- Business identifier.
- Collection status.
- Start time.
- Completion time.
- Number of records collected.
- Error details, where appropriate.

Possible statuses:

- Pending.
- Running.
- Completed.
- Partially completed.
- Failed.

### 3.6 API Responses

All endpoints should return predictable JSON structures.

Responses should distinguish between:

- Successful requests.
- Invalid parameters.
- Business not found.
- Unsupported data source.
- Rate limits.
- Collection failures.
- Temporary source unavailability.

## 4. Proposed API Endpoints

The final endpoint design will be confirmed during implementation.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Check API health |
| GET | `/api/v1/businesses/search` | Search for a business |
| GET | `/api/v1/businesses/{business_id}` | Retrieve business information |
| POST | `/api/v1/collections` | Request a review collection |
| GET | `/api/v1/collections/{collection_id}` | Check collection status |
| GET | `/api/v1/businesses/{business_id}/reviews` | Retrieve available reviews |
| GET | `/api/v1/businesses/{business_id}/analytics` | Retrieve rating statistics |

Collection requests may initially run synchronously for small workloads. A background job system can be introduced if collection operations take too long for a normal HTTP request.

## 5. Proposed Architecture

### API Layer

Responsibilities:

- Receive HTTP requests.
- Validate query parameters.
- Apply authentication when introduced.
- Invoke application services.
- Return structured responses.

Technology: FastAPI and Pydantic.

### Service Layer

Responsibilities:

- Coordinate collection requests.
- Apply business rules.
- Invoke the configured data provider.
- Normalize results.
- Trigger analytics.
- Handle application-level errors.

### Collection Layer

Responsibilities:

- Coordinate data collection.
- Manage crawling and extraction workflows.
- Handle pagination when supported.
- Apply appropriate request limits.
- Record collection outcomes.

Technology: Scrapy, with Playwright where permitted and technically necessary.

### Provider Layer

Responsibilities:

- Isolate source-specific behavior.
- Define a consistent interface for collecting business and review data.
- Convert provider responses into a common internal representation.
- Allow a different authorized provider to be introduced without rewriting the API.

### Analytics Layer

Responsibilities:

- Calculate rating distributions.
- Calculate statistics from collected reviews.
- Apply review filters.
- Identify data completeness limitations.

### Persistence Layer

Responsibilities:

- Manage application database access.
- Store business records and collection metadata.
- Store review records or permitted snapshots where the selected source and applicable terms allow it.
- Track collection history where appropriate.

Technology: PostgreSQL and SQLAlchemy.

Alembic will manage database migrations.

## 6. Development Milestones

### Milestone 1: Project Planning

- Define the product scope.
- Document expected functionality.
- Identify the initial data source.
- Confirm the source's access, pagination, retention, and usage restrictions.
- Define the initial API contract.

Deliverable: Approved project plan.

### Milestone 2: Project Foundation

- Establish the application package structure.
- Configure FastAPI.
- Configure environment variables.
- Set up logging and application configuration.
- Establish testing conventions.
- Verify the development environment.

Deliverable: A running, organized FastAPI application.

### Milestone 3: Business and Review Models

- Define the business data model.
- Define the review data model if individual reviews will be collected.
- Define collection metadata.
- Configure SQLAlchemy.
- Configure Alembic migrations.
- Test the database structure.

The final models will depend on the data available from the selected source.

Deliverable: Tested database infrastructure and initial migrations.

### Milestone 4: Data Collection

- Implement the provider interface.
- Implement one supported data-source integration.
- Implement collection and parsing logic.
- Handle pagination where available.
- Validate extracted fields.
- Handle missing data, timeouts, and source errors.
- Test against permitted sample data or fixtures.

Deliverable: A working collector that returns normalized records.

### Milestone 5: API Integration

- Implement business lookup.
- Implement collection requests.
- Implement collection status.
- Implement review retrieval.
- Implement filtering and pagination.
- Implement consistent response schemas.
- Add meaningful HTTP error responses.

Deliverable: A functional review-data API.

### Milestone 6: Rating Analytics

- Calculate rating distributions.
- Calculate average ratings for the collected sample.
- Calculate rating percentages.
- Distinguish collected-sample statistics from source-reported totals.
- Test calculations against known datasets.

Deliverable: Reliable rating analytics endpoints.

### Milestone 7: Testing and Reliability

- Unit-test parsers and analytics.
- Integration-test API endpoints.
- Test database operations.
- Test invalid input and missing fields.
- Test collection failures.
- Test pagination and duplicate handling.
- Add structured logging.

Deliverable: A tested and maintainable backend.

### Milestone 8: Deployment

- Create a Dockerfile.
- Configure production environment variables.
- Add deployment instructions.
- Deploy the API.
- Verify the production health endpoint.
- Test the deployed API through Swagger.

Deliverable: A publicly accessible API, subject to deployment configuration and data-source credentials.

### Milestone 9: Future Enhancements

Potential future features:

- Sentiment classification.
- Topic extraction.
- Recurring complaint detection.
- Positive and negative review summaries.
- Review trend analysis.
- Background collection jobs.
- API keys and usage quotas.
- Additional authorized data providers.

## 7. Engineering Principles

- Keep API endpoints thin.
- Separate collection, parsing, persistence, and analytics.
- Validate all external data.
- Do not assume that all reviews are accessible.
- Do not invent missing rating counts.
- Distinguish source-reported totals from collected-record totals.
- Make pagination and collection limits explicit.
- Avoid storing data beyond what the selected source permits.
- Keep credentials and secrets outside source control.
- Use Alembic for database schema changes.
- Test individual components before integrating them.
- Maintain clear Git history and use feature branches.

## 8. Definition of Done for Version 1

The first release is considered complete when:

1. The API starts reliably.
2. A client can identify a supported business.
3. The configured provider can collect available review data.
4. The collector returns validated, normalized records.
5. The API exposes structured review responses.
6. Rating statistics are calculated correctly from the relevant available data.
7. Missing or inaccessible information is represented honestly.
8. Errors are handled consistently.
9. Automated tests cover the core functionality.
10. Swagger documents the endpoints.
11. Deployment instructions are available.
12. The project has a clear README explaining setup, supported functionality, limitations, and usage.