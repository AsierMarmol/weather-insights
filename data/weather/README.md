# Saved weather data

| File | Contents |
| --- | --- |
| api_verification_fetches.jsonl | Genuine current/forecast responses with catalog ID, retrieval UTC and provider timestamps |
| api_verification_runs.jsonl | Safe summaries of the original verification runs |
| weather_records.csv | Normalized records saved automatically by the application service (P2.4 schema version 1) |

The retained initial dataset has **168 responses for 82 cities**: 84 current observations and 84 forecasts containing 3,360 prediction periods. Repeated cities are genuine separate fetches. These are dated development records, not currently fresh forecasts or an implemented application store.

At the user's request, city-specific investigation files and all 12 Lugo trial responses were removed. Its corrected reference remains in the destination catalog and provider override; there is no retained weather response for that city in this initial dataset. Every other raw response is preserved unchanged. Run summaries retain original request counts and explicitly identify filtered retained counts; they do not imply another live run.

Every successful fresh application fetch must append automatically with retrieval and valid/observation timestamps. Cache display and filter changes must not add records. Predictions and observations remain distinguishable; synthetic tests never enter this directory. Include genuine accumulated data in the final Git submission. No scheduler or historical chart is required.

The normalized application store is `weather_records.csv`, defined in [P2.4](../../PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). It was created on 12 November 2026 by the first genuine fetch through the P3.2 service (Toledo current and forecast, 41 rows) and grows with every fresh successful request; cache reuse adds no rows. The store refuses to read or extend the file if two rows share a record key (fetch_id, city_id, kind, valid_at_utc) with different values, for example after a bad manual edit or Git merge; resolve such a file from Git history. Exact repeated rows are read once and left unchanged. Alejandra implements saving/reloading; Gabriel connects successful requests; Asier verifies the connected path in P2.5.

The optional [verification script](../../scripts/verify_weather_access.py) still supports two-city or full-catalog checks and appends new successful responses to these logs. Do not run it merely to reproduce old reports. [API rules](../../WEATHER_API_CONTRACT.md) explain fields and limits. Source: [OpenWeather](https://openweathermap.org/); retain attribution and verify applicable redistribution terms before final delivery.
