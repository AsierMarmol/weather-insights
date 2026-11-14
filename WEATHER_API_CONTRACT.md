# Weather API contract

> **Current testing specification:** [Scoring model comfort-v2](SCORING.md) defines the approved seasonal Dashboard, preferred-range Searcher, gradual scores and driving penalties. Earlier dated progress records describe historical behavior; they are not the current formula.

P2.3 owner: Asier. Reviewer: Gabriel. Access checked on 11 November 2026; foundation reviewed by Gabriel in PR #3 on 12 November 2026. Production API/service accepted through P5.2 (PR #14). This document owns provider mapping and request rules. [Phase 2](PHASE2_SCOPE.md) owns product rules and the shared application schema; [SCORING.md](SCORING.md) owns the current formulas.

## Requests and mapping

HTTPS GET `https://api.openweathermap.org/data/2.5/weather` and `/forecast`, with `units=metric`, `lang=en` and local `appid`. Request the full forecast without a reduced `cnt`. Use the verified provider city ID for every catalog destination from the [shared mapping](data/reference/weather_location_overrides.json). A missing mapping fails before HTTP; there is no automatic coordinate fallback. The stable ES- catalog ID is not a provider city ID. Lugo uses provider ID 3117814; changing CSV coordinates alone does not remove that requirement. Validate country ES, identity/approved aliases and plausible proximity before using a response. Display catalog names consistently.

| Normalized field | Provider field | Conversion |
| --- | --- | --- |
| temperature_c | main.temp | Celsius, unchanged |
| wind_kmh | wind.speed | m/s multiplied by 3.6 |
| precipitation_probability_pct | forecast list[].pop | 0-1 multiplied by 100; current conditions have no corresponding probability |
| humidity_pct | main.humidity | Percent |
| cloud_pct | clouds.all | Percent |
| valid_at_utc | dt, or forecast list[].dt | Unix UTC to aware datetime |
| retrieved_at_utc | Actual response receipt | Separate from provider timestamp |
| provider_city_id/name | Current id/name or forecast city.id/name | Preserve separately from canonical catalog identity |

Missing metrics are None, never zero. Do not substitute rain volume, cloud cover, gust or feels-like for a different scoring field. Reference: [current weather](https://openweathermap.org/api/current), [three-hour forecast](https://openweathermap.org/api/forecast5).

## Request and save behavior

- Read `OPENWEATHER_API_KEY` through `config.get_api_key()` and python-dotenv only when needed. Environment variables take precedence over the ignored file. Never print keys, full request URLs, raw request exceptions or error bodies.
- Validate inputs before HTTP. Use timeouts, TLS verification and no unapproved redirects. Distinguish input, authentication, location, quota, network/server, invalid-data and storage errors.
- Skip ordinary failed locations; stop a batch on authentication/access, quota or storage failure. A transient network/5xx error may have one paced retry in production.
- Use one queue capped at 55 calls/minute including failures/retries; verify the actual account allowance before live use. Forecast cache: three hours; current cache: 30 minutes. Current provider age above two hours is also stale. Cache by product, actual parameters, units and language.
- Apply activity/size filters before fetching. Reuse raw forecasts for preferences/window changes, recomputing coverage at the common search time. A missing fifth-day period makes that choice unavailable; do not shorten it silently.
- A cold 83-city forecast batch can take several minutes. Show progress and partial results. Fetch current conditions only when the app needs them rather than automatically doubling every search's requests.
- Save each fresh successful request once before analytical use; then cache it. Surface storage failures and retain recoverable data. Cache reads never manufacture extra fetches. The client maps responses; the service owns the single save path.

## Verification and scope

Historical access checks covered all 83 cities and resolved provider naming. Subsequent offline replay covered all five day choices at the original run time, not arbitrary future run times. Invalid-key/unknown-city diagnostics returned 401/404. No current freshness or completed production behavior is implied. The cleaned [data record](data/weather/README.md) explains the retained 82-city evidence and removed investigation data.

```powershell
uv run --locked python scripts/verify_weather_access.py
uv run --locked python scripts/verify_weather_access.py --all-cities
```

These are optional live commands: up to six requests by default or 166 for the whole catalog. They append genuine data. Offline pytest does not call the API. Success requires access, required fields/coverage, expected error diagnostics and passing location checks. A wrong name, provider ID, country, coordinate match or missing location check makes the command exit nonzero. The summary exposes `location_checks_pass` and `overall_pass`; successful HTTP response evidence is retained even when location review fails. The script is a development check, not the production API or a scheduler.

Gabriel implemented the generic JSON base/provider subclass, mapping, caching and save integration in P3.2 using Alejandra's P3.1 store. P2.5 is Asier's verification of that same path, not a second implementation.


## Storage recovery follow-up - 13 November 2026

The service keeps its records/from_cache/error result shape. Storage errors additionally carry `storage_guidance`, a fixed safe explanation (optionally an OS error number), not raw exception or CSV contents. Destinations not attempted after a batch-stopping failure carry `skipped: true` inside error. Existing error codes remain unchanged. Searcher/Dashboard retain a separate summary of the first storage failure and skipped count for display.

Before cache lookup or fresh HTTP, retry any retained unsaved batches. Once saved, reuse a still-fresh forecast normally; do not fetch it again merely to recover a failed save. If saving still fails, return storage failure without another HTTP request. Explicit force refresh and stale-data rules remain unchanged. Pending records live only in the current session; the UI explains why not to close it before recovery.

File reads and atomic replacement retry Windows errors 5 (access denied, including an open handle), 32 and 33 at most three times, waiting 0.1 then 0.2 seconds. Other errors fail immediately. Permanent access denial remains an error after the bounded retry. Invalid CSVs are never silently repaired, overwritten or discarded. Existing atomic replacement, process-local locking and save-before-ranking rules remain in force.

## Testing-branch follow-up — 13 November 2026

Barcelona uses verified provider ID 3128760 through the existing location
override mechanism; see [reference evidence](data/reference/README.md#barcelona-identity-follow-up--13-november-2026).
An Eixample coordinate response is rejected, not silently relabeled. Successful
validated fetches still pass through the single save path.

The search coordinator also returns `forecasts`, mapping city IDs to the exact
successfully saved WeatherRecord batches used for its analysis. Failed/unsaved
responses supply no usable records. Dashboard computes its daily cells from
that snapshot, without new fetches or a different provider. The persisted CSV
schema and request pacing are unchanged.


Valladolid now uses verified provider ID 3106672 because its coordinate request
returned Delicias. See the [reference evidence](data/reference/README.md#valladolid-identity-follow-up--13-november-2026).
Identity/name/country/proximity validation is unchanged. Restart a running app
to recreate its client after updating location overrides.


All 83 provider IDs were verified on 13 November 2026 against both current and
forecast endpoints (166 successful responses, 3,403 saved records). See the
[complete mapping evidence and maintenance rules](data/reference/README.md#complete-provider-city-id-mapping--13-november-2026).
Earlier city-specific corrections above describe how this policy developed.

## Current reuse and scoring boundary

Request/save the full five-day response, then select 1–5 days locally. Rain and
wind preferences affect scoring, not the provider query. Full response identity,
timestamps and metrics remain validated. A forecast cache hit at age exactly three hours
is valid only when every record matches the currently requested provider city ID.
This identity rule also applies to current-weather cache reuse. A changed mapping
causes a fresh validated request rather than reuse of the old identity; earlier
records stay unchanged. A failed replacement fetch returns an error, never the
old identity as a fallback. Older or incomplete required coverage refreshes
through the same path.
There is no periodic background collector. Code reload replacement retries
pending saves first and retains the old service if recovery fails. Process
shutdown can lose unsaved in-memory batches; resolve storage guidance first.


## Request-cap update — 14 November 2026

The approved local cap is now **55 requests per rolling 60 seconds**, including
retries/failures, shared by clients within one process. OpenWeather publicly
lists 60 calls/minute and 1,000,000/month for the free current/five-day forecast
service: https://openweathermap.org/price (checked 14 November 2026).
Its FAQ says usage is combined across all keys on an account:
https://openweathermap.org/faq. This is public-plan evidence, not inspection
of the team's private subscription. Independent app processes do not coordinate
their limiters; do not treat separate keys on one account as separate quotas.

This changes the cap only. The existing sliding-window queue can still pause
after a burst; smoother pacing and explicit waiting/retry progress messages
remain a separate UI improvement. Restart Streamlit after current work finishes
to replace the process-wide limiter reliably. Forecast reuse stays three hours.

### Batch-stop consistency — 14 November 2026

The automatic second pass for incomplete cached coverage obeys the original
batch's authentication, quota and storage stops. It must not make new requests
after any of those stops, even if an earlier cached destination needs more
slots. The incomplete cache remains unavailable with its actual reason, and
the original failure remains visible. Retry only through a later user action
after resolving the problem. This applies to both views' shared search path.
