# Weather API contract

P2.3 owner: Asier. Reviewer: Gabriel. Access checked on 11 November 2026; foundation reviewed by Gabriel in PR #3 on 12 November 2026. Production API/service accepted through P5.2 (PR #14). This document owns provider mapping and request rules. [Phase 2](PHASE2_SCOPE.md) owns product/scoring rules and the shared application schema.

## Requests and mapping

HTTPS GET `https://api.openweathermap.org/data/2.5/weather` and `/forecast`, with `units=metric`, `lang=en` and local `appid`. Request the full forecast without a reduced `cnt`. Normally use catalog latitude/longitude; apply [provider overrides](data/reference/weather_location_overrides.json). The stable ES- catalog ID is not a provider city ID. Lugo uses provider ID 3117814; changing CSV coordinates alone does not remove that requirement. Validate country ES, identity/approved aliases and plausible proximity before using a response. Display catalog names consistently.

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
- Use one queue capped at 40 calls/minute including failures/retries; verify the actual account allowance before live use. Forecast cache: three hours; current cache: 30 minutes. Current provider age above two hours is also stale. Cache by product, actual parameters, units and language.
- Apply activity/size filters before fetching. Reuse raw forecasts for preferences/window changes, recomputing coverage at the common search time. A missing fifth-day period makes that choice unavailable; do not shorten it silently.
- A cold 83-city forecast batch can take several minutes. Show progress and partial results. Fetch current conditions only when the app needs them rather than automatically doubling every search's requests.
- Save each fresh successful request once before analytical use; then cache it. Surface storage failures and retain recoverable data. Cache reads never manufacture extra fetches. The client maps responses; the service owns the single save path.

## Verification and scope

Historical access checks covered all 83 cities and resolved provider naming. Subsequent offline replay covered all five day choices at the original run time, not arbitrary future run times. Invalid-key/unknown-city diagnostics returned 401/404. No current freshness or completed production behavior is implied. The cleaned [data record](data/weather/README.md) explains the retained 82-city evidence and removed investigation data.

```powershell
uv run --locked python scripts/verify_weather_access.py
uv run --locked python scripts/verify_weather_access.py --all-cities
```

These are optional live commands: up to six requests by default or 166 for the whole catalog. They append genuine data. Offline pytest does not call the API. Location-review flags are reported separately from successful access; review them even when the diagnostic exits successfully. The script is a development check, not the production API or a scheduler.

Gabriel implemented the generic JSON base/provider subclass, mapping, caching and save integration in P3.2 using Alejandra's P3.1 store. P2.5 is Asier's verification of that same path, not a second implementation.


## Storage recovery follow-up - 13 November 2026

The service keeps its records/from_cache/error result shape. Storage errors additionally carry `storage_guidance`, a fixed safe explanation (optionally an OS error number), not raw exception or CSV contents. Destinations not attempted after a batch-stopping failure carry `skipped: true` inside error. Existing error codes remain unchanged. Searcher/Dashboard retain a separate summary of the first storage failure and skipped count for display.

Before cache lookup or fresh HTTP, retry any retained unsaved batches. Once saved, reuse a still-fresh forecast normally; do not fetch it again merely to recover a failed save. If saving still fails, return storage failure without another HTTP request. Explicit force refresh and stale-data rules remain unchanged. Pending records live only in the current session; the UI explains why not to close it before recovery.

File reads and atomic replacement retry Windows errors 5 (access denied, including an open handle), 32 and 33 at most three times, waiting 0.1 then 0.2 seconds. Other errors fail immediately. Permanent access denial remains an error after the bounded retry. Invalid CSVs are never silently repaired, overwritten or discarded. Existing atomic replacement, process-local locking and save-before-ranking rules remain in force.
