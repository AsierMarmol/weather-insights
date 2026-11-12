# Saved weather data

| File | Contents |
| --- | --- |
| api_verification_fetches.jsonl | Genuine current/forecast responses with catalog ID, retrieval UTC and provider timestamps |
| api_verification_runs.jsonl | Safe summaries of the original verification runs |
| weather_records.csv | Normalized records saved automatically by the application service (P2.4 schema version 1) |

The retained initial dataset has **168 responses for 82 cities**: 84 current observations and 84 forecasts containing 3,360 prediction periods. Repeated cities are genuine separate fetches. These are dated development records, not currently fresh forecasts; the application uses the separate normalized CSV described below.

At the user's request, city-specific investigation files and all 12 Lugo trial responses were removed. Its corrected reference remains in the destination catalog and provider override; there is no retained weather response for that city in this initial dataset. Every other raw response is preserved unchanged. Run summaries retain original request counts and explicitly identify filtered retained counts; they do not imply another live run.

Every successful fresh application fetch must append automatically with retrieval and valid/observation timestamps. Cache display and filter changes must not add records. Predictions and observations remain distinguishable; synthetic tests never enter this directory. Include genuine accumulated data in the final Git submission. No scheduler or historical chart is required.

The normalized application store is `weather_records.csv`, defined in [P2.4](../../PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). It was created on 12 November 2026 by the first genuine fetch through the P3.2 service (Toledo current and forecast, 41 rows) and grows with every fresh successful request; cache reuse adds no rows. The store refuses to read or extend the file if two rows share a record key (fetch_id, city_id, kind, valid_at_utc) with different values, for example after a bad manual edit or Git merge; resolve such a file from Git history. Exact repeated rows are read once and left unchanged. Alejandra implemented saving/reloading and Gabriel connected successful requests. Asier/Codex verified P2.5 on 12 November 2026: six fresh requests for Toledo, Segovia and Seville added 123 records (3 current + 120 forecast), bringing the store to 164 rows. Readback, restart/cache reuse and idempotent saves passed without duplicate records. See [P2.5 evidence](../../PHASE2_SCOPE.md#p25-verification---12-november-2026) for exact fetch IDs and the offline replay. Gabriel and Christian approved P2.5 in merged PR #9. P4.1 tests replay this sample read-only; no new live records were added during interface implementation.

The optional [verification script](../../scripts/verify_weather_access.py) still supports two-city or full-catalog checks and appends new successful responses to these logs. Do not run it merely to reproduce old reports. [API rules](../../WEATHER_API_CONTRACT.md) explain fields and limits. Source: [OpenWeather](https://openweathermap.org/); retain attribution and verify applicable redistribution terms before final delivery.

## Accumulated application forecasts - 12 November 2026

At the 12:37 UTC snapshot, the saved application CSV contained **3,324 records across 82 catalog destinations**. The additional 3,160 forecast records form 79 fetch groups of 40 forecast slots each, retrieved between 12:36:27 and 12:37:35 UTC on 12 November 2026. The original 164 records are preserved. Barcelona has no saved application records in this snapshot; this is not a claim of complete 83-destination weather coverage.

Pre-publication validation passed using the application record loader: schema and value validation, catalog membership, unique record keys, coherent city/kind/retrieval time within each new fetch group, and preservation of the original rows. These are dated forecasts, not observations of future weather. No live requests or synthetic records were added during publication. The absence of Barcelona records does not establish the cause of the missing fetch.

Further genuine searches during the P5.5 review append newer fetch groups to the same CSV. The counts above describe the original dated snapshot, not a permanent row-count constraint. Validate newly collected groups through WeatherStore before committing; retain earlier records.


## Normal app use during P5.5 - 12 November 2026

At 17:35:30 UTC the CSV contained **6,604 records across all 83 destinations**, including Barcelona. Asier confirmed he was running the app during the review. Compared with the earlier snapshot, 82 new genuine forecast groups added 3,280 rows; all original 3,324 rows are preserved in order. A frozen copy passed WeatherStore schema/model validation, catalog membership, unique record keys and coherent city/kind/retrieval time within each group. Review tests did not create these records or make live requests. These counts are a dated checkpoint and may grow during subsequent use.
