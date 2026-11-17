# Google Reviews Intelligence API

## 1. Project Overview

### Purpose

A scraping-as-a-service API platform, modelled on SerpApi, that lets clients retrieve structured, real-time data from Google Maps (businesses, place details, and reviews) through a single, simple HTTP API.

Clients send a request with an `engine` and query parameters. The platform handles everything difficult behind the scenes — browser automation, proxies, anti-bot measures, CAPTCHAs, parsing, retries, and caching — and returns clean, predictable JSON.

The first release focuses on Google Maps. The architecture is engine-based so that additional sources (Google Search, Google Shopping, other review sites) can be added later without rewriting the core platform.

### Primary Goals

- Provide a SerpApi-style REST API built with FastAPI.
- Support a pluggable **engine** system, starting with Google Maps search, place details, and reviews.
- Run scraping work in **background workers**, separate from the API process.
- Handle proxies, browser fingerprinting, rate limiting, retries, and CAPTCHA detection reliably.
- Return normalized, validated JSON with consistent metadata for every request.
- Cache results to make repeated queries fast and cheap.
- Authenticate clients with **API keys**, and meter and limit usage per plan.
- Keep a **search archive** so clients can retrieve past results by ID.
- Provide rating analytics on top of collected reviews.
- Containerize, deploy, and monitor the platform.

## 2. Scope

### Included in Version 1

- Engine framework (a common interface for all data sources).
- Google Maps engines: search, place details, reviews.
- Synchronous and asynchronous request modes.
- Job queue and worker pool.
- Proxy management and anti-bot handling.
- Result parsing, normalization, and validation.
- Result caching.
- Search archive (retrieve past results by search ID).
- API key authentication.
- Usage metering, monthly quotas, and rate limits.
- Account endpoint (plan, usage, remaining credits).
- Rating analytics for collected reviews.
- PostgreSQL persistence, Redis for queue and cache.
- Docker-based deployment and basic monitoring.

### Out of Scope for Version 1

- Payment processing and self-serve signup (API keys are issued manually at first).
- Customer-facing web dashboard and interactive playground.
- Engines other than Google Maps.
- Official client libraries (SDKs).

### Legal and Compliance Position

Google's Terms of Service restrict automated access to its services. Like SerpApi, this platform collects **publicly visible** data. Before going public, the team must:

- Decide and document the legal position, and get legal advice if the platform will be offered commercially.
- Collect only publicly available data, and never data behind a login.
- Minimize personal data: reviewer names and profile links are returned only as they appear publicly, and can be disabled per deployment.
- Define a data retention period for the search archive and cache.
- Publish clear Terms of Use and an acceptable use policy for clients.

## 3. How the API Works

### 3.1 Request Model

Every request goes to a single search endpoint. The `engine` parameter selects the data source; the remaining parameters depend on the engine.

```
GET /api/v1/search?engine=google_maps&q=coffee+berlin&api_key=XXXX
GET /api/v1/search?engine=google_maps_place&place_id=ChIJ...&api_key=XXXX
GET /api/v1/search?engine=google_maps_reviews&place_id=ChIJ...&sort_by=newest&api_key=XXXX
```

Common parameters for all engines:

| Parameter | Purpose |
|---|---|
| `engine` | Which engine to use (required) |
| `api_key` | Client API key (or `Authorization: Bearer` header) |
| `hl` | Interface language, e.g. `en`, `de` |
| `gl` | Country, e.g. `us`, `de` |
| `no_cache` | Force a fresh scrape, ignoring cached results |
| `async` | Return immediately with a search ID instead of waiting for results |
| `output` | `json` (default) or `html` (raw page, for debugging) |

### 3.2 Synchronous and Asynchronous Modes

- **Synchronous (default):** the API places a job on the queue, waits for a worker to finish (up to a timeout), and returns the result in the same response.
- **Asynchronous (`async=true`):** the API returns a `search_id` right away. The client fetches the result later from the search archive, or receives a webhook when the job finishes.

Both modes use the same queue and workers, so the API process never scrapes directly.

### 3.3 Response Structure

Every response has the same top-level shape:

```json
{
  "search_metadata": {
    "id": "6f1c...",
    "status": "Success",
    "created_at": "2026-10-29T10:00:00Z",
    "processed_at": "2026-10-29T10:00:04Z",
    "total_time_taken": 4.12,
    "cached": false,
    "json_endpoint": "/api/v1/searches/6f1c..."
  },
  "search_parameters": {
    "engine": "google_maps_reviews",
    "place_id": "ChIJ...",
    "hl": "en"
  },
  "place_info": { },
  "reviews": [ ],
  "pagination": {
    "next_page_token": "...",
    "next": "/api/v1/search?engine=google_maps_reviews&place_id=ChIJ...&next_page_token=..."
  }
}
```

Possible values of `search_metadata.status`: `Queued`, `Processing`, `Success`, `Error`.

### 3.4 Error Responses

Errors use standard HTTP status codes and a consistent body:

```json
{ "error": "Invalid API key.", "code": "invalid_api_key" }
```

| Status | Meaning |
|---|---|
| 400 | Missing or invalid parameters, unsupported engine |
| 401 | Missing or invalid API key |
| 404 | Search ID or place not found |
| 429 | Rate limit or monthly quota exceeded |
| 502 | Source returned an unexpected page or parsing failed |
| 503 | Source temporarily unavailable or blocked after all retries |
| 504 | Synchronous request timed out (the job continues and can be fetched by ID) |

Failed searches do **not** consume a client's credits.

## 4. Engines (Version 1)

### 4.1 `google_maps` — Business Search

Inputs: `q` (search text), optional `ll` (coordinates and zoom, e.g. `@52.52,13.40,14z`), `start` (pagination offset).

Output per result: position, title, `place_id`, `data_id`, address, coordinates, rating, review count, price level, category/type, phone, website, opening hours, thumbnail, and a link to the listing.

### 4.2 `google_maps_place` — Place Details

Inputs: `place_id` or `data_id`, or a Google Maps URL.

Output: full place information — name, address, coordinates, rating, review count, rating histogram (as reported by Google), categories, phone, website, opening hours, popular times (when shown), photos, and attributes.

### 4.3 `google_maps_reviews` — Reviews

Inputs: `place_id` or `data_id`, `sort_by` (`relevance`, `newest`, `highest`, `lowest`), optional `topic_id` or `query` (keyword filter), `next_page_token`.

Output per review: review ID, rating, text, original-language text, publication date (relative and parsed ISO date), language, likes, photos, owner response and its date, reviewer name, reviewer profile link, reviewer review count, and Local Guide status.

Each page returns a `next_page_token` until no more reviews are available.

### 4.4 Data Honesty Rules

These rules apply to every engine:

- Missing fields are omitted or set to `null`. They are never guessed or invented.
- Figures **reported by Google** (total review count, rating histogram) are kept separate from figures **calculated from collected records**.
- A partial collection is always marked as partial and is never presented as complete.

## 5. Analytics

The analytics endpoint works on reviews that the platform has already collected for a place.

```
GET /api/v1/places/{place_id}/analytics?api_key=XXXX
```

Metrics:

- Rating distribution (count and percentage for 1–5 stars) of the collected sample.
- Average rating of the collected sample.
- Google-reported rating and review count, shown separately for comparison.
- Sample coverage: collected reviews as a share of the Google-reported total.
- Review volume over time (by month).
- Owner response rate and average response time.

Future analytics (Milestone 11): sentiment, topic extraction, recurring complaints, and summaries.

## 6. Platform Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Health check (API, database, Redis, workers) |
| GET | `/api/v1/search` | Run a search with any engine (sync or async) |
| GET | `/api/v1/searches/{search_id}` | Fetch a past or pending result from the archive |
| GET | `/api/v1/places/{place_id}/analytics` | Rating analytics for collected reviews |
| GET | `/api/v1/account` | Client plan, usage this month, remaining credits |
| GET | `/api/v1/engines` | List available engines and their parameters |

Webhooks: clients can register a callback URL on their account, or pass `webhook_url` per request, to be notified when an async search finishes.

## 7. Architecture

```
            ┌──────────────┐
 Client ──▶ │  FastAPI API │ ── auth, quota, validation, cache lookup
            └──────┬───────┘
                   │ enqueue job / read result
            ┌──────▼───────┐        ┌────────────┐
            │    Redis     │◀──────▶│   Cache    │
            │ (job queue)  │        └────────────┘
            └──────┬───────┘
                   │
         ┌─────────▼──────────┐
         │   Worker pool      │ ── engines, browsers, proxies, parsers
         └─────────┬──────────┘
                   │
            ┌──────▼───────┐
            │  PostgreSQL  │ ── accounts, API keys, usage, search archive,
            └──────────────┘    places, reviews
```

### 7.1 API Layer

- Receives HTTP requests and validates parameters with Pydantic.
- Authenticates API keys and checks rate limits and quotas.
- Checks the cache before enqueuing work.
- Enqueues jobs and waits (sync) or returns a search ID (async).
- Never performs scraping itself.

Technology: FastAPI, Pydantic, Uvicorn.

### 7.2 Job Queue and Workers

- Jobs are placed on a Redis-backed queue.
- Workers run as separate processes/containers and can be scaled independently of the API.
- Each job has a timeout, a retry policy with exponential backoff, and a final status.
- Results are written to the search archive and the cache.

Technology: Redis with Arq (async-native, fits FastAPI well). Celery is the fallback if more complex workflows are needed.

### 7.3 Engine Layer

Every engine implements the same interface:

- `validate_params(params)` — check engine-specific inputs.
- `fetch(params, context)` — retrieve the raw page or data using the scraping infrastructure.
- `parse(raw)` — extract fields into the engine's response schema.
- `cache_key(params)` — build a stable key for caching.

Engines are registered in an engine registry. Adding a new source means adding a new engine, with no changes to the API, queue, or billing code.

### 7.4 Scraping Infrastructure

Shared by all engines:

- **HTTP client** (httpx) for requests that don't need a browser, such as Google's internal JSON endpoints.
- **Headless browser pool** (Playwright) for pages that require JavaScript, with reusable browser contexts.
- **Proxy manager:** rotating residential/datacenter proxies, per-country selection (matches `gl`), health tracking, and automatic removal of blocked proxies.
- **Fingerprinting:** realistic and varied user agents, headers, viewport, locale, and timezone.
- **Block and CAPTCHA detection:** recognize consent pages, CAPTCHAs, and unusual-traffic pages; retry with a new proxy; optionally integrate a CAPTCHA-solving service.
- **Rate limiting toward the source**, to avoid getting proxies banned.

### 7.5 Parsing and Normalization

- Parsers are isolated per engine and tested against saved HTML/JSON fixtures.
- Dates, ratings, counts, and coordinates are normalized into consistent types.
- All output is validated against Pydantic response schemas before it is returned.
- Parser failures are logged with the raw page saved for debugging, so layout changes on Google's side are detected quickly.

### 7.6 Caching

- Results are cached in Redis, keyed by engine and normalized parameters.
- Default cache lifetime: 1 hour (configurable per engine).
- Cached responses are free for clients and are marked `"cached": true`.
- `no_cache=true` forces a fresh scrape.

### 7.7 Accounts, API Keys, and Metering

- Accounts have a plan with a monthly search quota and a requests-per-second limit.
- API keys are stored hashed, can be rotated, and can be revoked.
- Every successful non-cached search is recorded as one credit of usage.
- Rate limiting uses Redis counters.

### 7.8 Persistence

PostgreSQL stores:

- Accounts, plans, API keys.
- Usage records.
- Search archive (parameters, status, timings, result JSON, errors).
- Places and reviews (to support analytics and deduplication).

Technology: SQLAlchemy 2 and Alembic for migrations.

### 7.9 Observability

- Structured JSON logging with a search ID on every log line.
- Metrics: success rate per engine, average latency, block rate per proxy, queue length, worker utilization.
- Error tracking (e.g. Sentry).
- Alerts when an engine's success rate drops, which usually means Google changed its page layout.

## 8. Technology Stack

| Area | Technology |
|---|---|
| API | FastAPI, Pydantic, Uvicorn |
| Queue / workers | Redis, Arq |
| Scraping | httpx, Playwright, selectolax/lxml for parsing |
| Database | PostgreSQL, SQLAlchemy 2, Alembic |
| Cache / rate limits | Redis |
| Testing | pytest, pytest-asyncio, saved fixtures |
| Deployment | Docker, Docker Compose (API, worker, Postgres, Redis) |
| Monitoring | Structured logs, Prometheus/Grafana or a hosted alternative, Sentry |

## 9. Development Milestones

### Milestone 1: Project Planning — *in progress*

- Define the product as a SerpApi-style platform.
- Agree the request/response model and the first engines.
- Document the legal and compliance position.
- Choose a proxy provider.

Deliverable: Approved project plan.

### Milestone 2: Project Foundation — *partly done*

- Application package structure (`api`, `core`, `engines`, `scraping`, `workers`, `models`, `schemas`, `services`).
- FastAPI app, configuration via environment variables, logging.
- Database connection and Alembic (done).
- Docker Compose with API, worker, PostgreSQL, and Redis.
- Testing setup with pytest.

Deliverable: The API and a worker start together with one command.

### Milestone 3: Core Data Models

- Accounts, plans, API keys, usage records.
- Search archive.
- Places and reviews.
- Initial Alembic migrations and database tests.

Deliverable: Tested database schema.

### Milestone 4: Job Queue and Search Lifecycle

- Redis queue and Arq workers.
- `GET /search` in sync and async modes.
- `GET /searches/{search_id}`.
- Job timeouts, retries, and status tracking.
- A dummy "echo" engine to test the full flow end to end.

Deliverable: A request travels API → queue → worker → archive → response.

### Milestone 5: Scraping Infrastructure

- HTTP client and Playwright browser pool.
- Proxy manager with rotation and health checks.
- Fingerprinting and header management.
- Block and CAPTCHA detection with retry.
- Saving raw pages for debugging.

Deliverable: A reliable fetch layer that engines can use.

### Milestone 6: Google Maps Engines

- `google_maps` search engine with pagination.
- `google_maps_place` details engine.
- `google_maps_reviews` engine with sorting, filtering, and pagination.
- Parsers tested against saved fixtures.
- Data honesty rules from section 4.4 applied.

Deliverable: All three engines return validated JSON.

### Milestone 7: Authentication, Quotas, and Caching

- API key authentication (query parameter and header).
- Per-plan rate limits and monthly quotas.
- Usage metering (failed and cached searches are free).
- `GET /account`.
- Redis result caching and `no_cache`.

Deliverable: The API can safely be given to external clients.

### Milestone 8: Analytics and Webhooks

- Rating analytics endpoint.
- Clear separation of Google-reported figures from collected-sample figures.
- Webhook delivery for async searches, with retries.

Deliverable: Analytics and webhook features working and tested.

### Milestone 9: Testing and Reliability

- Unit tests for parsers, analytics, quotas, and cache keys.
- Integration tests for the full search lifecycle.
- Failure tests: blocks, timeouts, malformed pages, quota exceeded.
- Scheduled "canary" searches that detect when Google changes its layout.
- Structured logging and metrics.

Deliverable: A tested, observable platform.

### Milestone 10: Deployment

- Production Docker images for API and workers.
- Production configuration and secrets management.
- Deployment with separately scalable API and worker services.
- Monitoring dashboards and alerts.
- Public API documentation (Swagger plus per-engine docs with examples).

Deliverable: A publicly accessible, monitored API.

### Milestone 11: Future Enhancements

- More engines: Google Search, Google Shopping, Google Hotels, other review platforms.
- Customer dashboard, signup, and an interactive playground.
- Billing and payments (e.g. Stripe).
- Client SDKs (Python, JavaScript).
- AI analytics: sentiment, topics, recurring complaints, summaries.
- Scheduled monitoring of places with change notifications.
- Bulk jobs and dataset exports (CSV/JSON).

## 10. Engineering Principles

- The API process never scrapes; all scraping runs in workers.
- Every engine follows the same interface and response conventions.
- Keep API endpoints thin; put logic in services and engines.
- Validate all external data before returning it.
- Never invent missing data; separate source-reported figures from calculated ones.
- Expect Google's pages to change: isolate parsers, keep fixtures, and monitor success rates.
- Failed searches never cost the client credits.
- Keep credentials, proxy settings, and API keys out of source control.
- Use Alembic for all schema changes.
- Use feature branches and pull requests; keep a clear Git history.

## 11. Definition of Done for Version 1

Version 1 is complete when:

1. The API, workers, PostgreSQL, and Redis start reliably with Docker Compose.
2. Clients authenticate with API keys, and quotas and rate limits are enforced.
3. `google_maps`, `google_maps_place`, and `google_maps_reviews` return validated, normalized JSON.
4. Sync and async modes both work, and past searches can be retrieved by ID.
5. Results are cached, and cached responses are marked and free.
6. Blocks, timeouts, and parse failures are retried and reported with consistent errors.
7. Rating analytics are correct and separate collected-sample figures from Google-reported ones.
8. Engine success rates are monitored, and alerts fire when they drop.
9. Automated tests cover the core platform and all engines.
10. Swagger and per-engine documentation are published.
11. The legal and compliance position is documented.
12. The README explains setup, engines, limitations, and usage.
