# Phase 3 - Core Application and Automatic Data Saving

Updated: 12 November 2026. **In progress:** P3.1 reviewed and merged into dev (PR #4); P3.2 implemented locally and awaiting review; P3.3 pending.

## Purpose and dependencies

Build models/storage, the reusable API/save service and the analytical engine. Reviewed P2.1-P2.4 are the start gate. Asier verifies P2.5 using P3.1/P3.2 after they are connected; require that check for Phase 3 acceptance, not before constructing the components.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P3.1 | Models, catalog loading and persistence | Alejandra | Christian | P2.4 | Validated models with useful special method/computed property; safe CSV append/reload, preserved genuine records and meaningful tests. | Awaiting Phase 3 acceptance: approved by Christian and merged into dev (PR #4, 12 November 2026); P2.5 verification pending; Christian's separate P2.4 review still outstanding |
| P3.2 | Production API and request/save service | Gabriel | Alejandra | P2.4; integration after P3.1 | Generic/provider inheritance and deliberate encapsulation; safe credentials, normalization, partial failures, pacing/cache, single automatic save path and tests. | In progress: implemented and tested locally on gabrielstec/feature; bounded live check passed; awaiting PR and Alejandra's review |
| P3.3 | Analytics and ranking engine | Christian | Selin | P2.4; real-data integration after P3.1 + P3.2 | Complete coverage/time/filter/scoring/tie rules, three analyses and independently checked tests on synthetic and genuine inputs. | Pending |

## Implementation and acceptance

Use the shared objects, methods, CSV header and worked example in P2.4. Alejandra owns models.py/storage.py; Gabriel client.py/config.py/service.py; Christian analytics.py. Keep analytics pure and credential-free. Extend the existing lazy get_api_key helper rather than duplicating configuration. Retain valid dated records; new successes save automatically, cache reads do not. A failed save is not analytical success. No scheduler or second verification client/store.

Read [Phase 2](PHASE2_SCOPE.md) for product rules, shared schema and the worked example; [API contract](WEATHER_API_CONTRACT.md) for provider behavior; [roles](TEAMROLES.MD) for ownership. Each owner includes tests/docs/fixes. Follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance) when decisions change. The instructor README governs final acceptance; plans are not proof of completed functionality.

## Task prompt

```text
Work on <task ID> in PHASE3_CORE_DATA.md as <actual requester>.
Read the task, shared specification and actual prerequisite files first.
Complete the whole assigned deliverable within its owned files, using existing
components rather than duplicating them. Keep secrets private and synthetic
test inputs separate from genuine data. Run relevant checks and record actual
results, limitations and the next dependency in this phase. Update affected
plans when rules change. Record substantial AI assistance accurately in
PROMPTS.md; do not invent teammate work or approval. Do not commit, push,
request review, merge or submit without the relevant authorization.
```

## Phase progress log

| Date | Task | Actual result and evidence | Status |
| --- | --- | --- | --- |
| 12 November 2026 | P3.1 | Alejandra/Claude Code implemented `models.py` (validated frozen `Destination`, `SearchPreferences`, `WeatherRecord`; `drive_hours`, `horizon`, `lead_time`, `key` properties; `__str__`/`__repr__`, chronological `__lt__`; exact CSV round-trip) and `storage.py` (`load_destinations`, `WeatherStore.append/load/latest_forecast`, `CatalogError`, `StorageError`). Saves copy the existing file byte-for-byte to a temporary file, append, fsync and atomically replace; retries are idempotent on (fetch_id, city_id, kind, valid_at_utc); conflicting values raise `ValueError`; damaged files raise `StorageError` and are never appended to; writes are serialized per file within the process. `tests/test_models.py` and `tests/test_storage.py` add 82 offline tests using temporary files only; the full suite passes (107). The real catalog loads 83 rows (14/26/43 sizes, Lugo values unchanged). No `weather_records.csv` was created and no live request was made. | In progress; awaiting PR and Christian's review |
| 12 November 2026 | P3.1 review | Christian approved PR #4 and merged it into dev (`7ac93c1`). This approval covers P3.1 only, not the separate P2.4/catalog review. | Reviewed; Phase 3 acceptance waits for P2.5 |
| 12 November 2026 | P3.2 | Gabriel/Claude Code implemented `client.py` (generic `JSONAPIClient` base: name-mangled key and parameter name, masked `__repr__`, context manager, `request_count` property, paced HTTPS GET with (5, 20) s timeouts, no redirects, one retry for timeouts/connection/5xx only, distinct `APIError` subclasses per code, errors raised `from None`; shared 40-calls/minute `RateLimiter`; `OpenWeatherClient` subclass: coordinate or Lugo city-ID parameters, `units=metric`, `lang=en`, location checks (ES, catalog name or approved alias, expected provider ID, within the 10 km tolerance used by P2.3), mapping to `WeatherRecord` with wind x 3.6, pop x 100, missing/malformed/out-of-range metrics as None, receipt time separate from valid time, one fetch_id per response, duplicate forecast times rejected; public `map_current`/`map_forecast` for deliberate replay/import), `service.py` (`WeatherService.current/forecast/forecast_many`: P2.4 result dictionaries, save-once-then-cache through `WeatherStore`, 30-minute current TTL plus 2-hour observation age, 3-hour forecast TTL with equality allowed, reuse of the newest fresh stored group after restart, storage failures reported as `storage` with no records and the batch kept for retry, conflicts as `invalid_data`, batches that skip ordinary failures and stop on authentication/quota/storage with explicit results for the rest, progress callback) and `config.py` (`load_product_defaults()`, `load_location_overrides()` with validation). Tests: `tests/test_client.py`, `tests/test_service.py`, new loader tests in `tests/test_config.py` and offline doubles in `tests/weather_fakes.py` (synthetic weather only; real `WeatherStore` on temporary files). The full suite passes (172; 65 new). A read-only replay maps all 168 retained genuine responses (82 cities: 84 current, 3,360 forecast periods) and passes every location check, with no HTTP. | In progress; awaiting PR and Alejandra's review |
| 12 November 2026 | P3.2 live check | With Gabriel's local key, `WeatherService.from_environment()` fetched Toledo current conditions and forecast at about 10:28 UTC: 2 HTTP requests, no errors, provider 2510409 Toledo, 1 current and 40 forecast records under one fetch_id, every period with a precipitation probability, retrieval time stored separately from valid time. `data/weather/weather_records.csv` was created with 41 genuine rows; `latest_forecast` read back the same 40 records. Repeat calls and a new service instance were served from cache/store with no further HTTP and no new rows. | Passed; P2.5 remains Asier's verification |
| 12 November 2026 | P3.2 decisions and limits | Unit conversions are rounded to nine decimals to remove binary noise (0.3 x 100 is otherwise 30.000000000000004 and would fail a "<= 30 %" preference at its boundary); provider values have at most two decimals. A response that does not identify the requested destination is `invalid_data`, matching the analytics reason code. Stored fresh groups are reused by city_id after a restart; they were identity-checked when fetched. The in-memory cache is per service instance, so the app should create one shared service (P4.3). Importing the retained JSONL evidence into `weather_records.csv` is still not done; the mapping now exists, and whether to import is a team decision. | Open |
| 12 November 2026 | P3.1 limits | Importing the retained JSONL evidence is not done: it needs the provider-to-record mapping from P3.2 and must keep original retrieval times. Two records with the same key but different values in one batch are rejected rather than stored, so a provider duplicate surfaces as an invalid-data save error. Single writing process per clone, as specified. | Open; revisit with Gabriel at P3.2 integration |

## Next action

Gabriel opens a P3.2 PR for Alejandra's review. Christian completes the outstanding P2.4/catalog review and builds P3.3. After P3.2 is merged, Asier runs P2.5 through `WeatherService.from_environment()` and `WeatherStore`; then verify analytical results on the saved data.
