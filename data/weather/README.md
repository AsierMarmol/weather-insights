# Saved weather data

## Weather dataset license — 14 November 2026

The requester confirmed the Free Current Weather + 5-day/3-hour Forecast plan.
Weather data is provided by [OpenWeather](https://openweathermap.org/).
The retained JSONL responses and normalized `weather_records.csv` are made
available under the [Open Data Commons Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/),
as specified in OpenWeather's [published plan terms](https://openweathermap.org/full-price).
Keep attribution and applicable share-alike notices when redistributing the
database. Normalization converts units and field names and adds retrieval and
catalog identifiers; it does not turn predictions into observed outcomes.
This notice covers weather data, not the application code, branding or other
third-party assets. The app retains the required visible provider credit.

This resolves the earlier unconfirmed-plan item below using the requester's
confirmation and public plan terms; historical evidence retains its dates.


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


## Provider credit and delivery review - 12 November 2026

This historical review's unconfirmed-plan item is superseded by the
[dataset licence notice](#weather-dataset-license--14-november-2026) above.
The original evidence below retains its date and scope.

Weather data provided by [OpenWeather](https://openweathermap.org/). Its [attribution guidance](https://openweathermap.org/faq#license) specifies visible provider text, a website link and its logo for plans requiring attribution. The application now displays these in the shared sidebar using the unmodified master RGB logo from the [official archive](https://openweathermap.org/payload/api/files/file/logo_files.zip). The logo is stored at `assets/openweather-logo.jpg` in the repository.

Public attribution guidance was checked during P6.1 preparation. The team's account-specific permission to store and redistribute the retained responses has not been independently confirmed; Asier and Gabriel must resolve that delivery gate before submission. Do not remove or fabricate the genuine dataset to bypass the instructor's requirement. Current and forecast records remain distinguishable, with retrieval timestamps separate from provider valid times.

## Dashboard experiment collection — 13 November 2026

The authorized live Dashboard check collected 82 fresh forecast groups through
the normal validated service/save path. Barcelona's coordinate response named
Eixample and was rejected. A subsequent verified city-ID request saved 40
Barcelona forecast periods. The checkpoint contains **11,324 genuine records**
across all 83 destinations: all earlier 8,004 records plus 3,320 forecast rows.
Searcher reused the fresh saved batches without duplicate successful saves.
Read-only analysis of the saved snapshot gave complete 1/3/5-day coverage at
the verification time; this is not a promise of permanent freshness.

SHA256 of the frozen automated-test copy:
`70e161e45f722b257859fb3de3d7d3722a12984059274d0382ee76c01b5762ff`.
The user confirmed concurrent normal app use. Further genuine records may be
added; preserve them and validate the selected publication snapshot separately.
No synthetic weather was written to this file.

Scoring is defined in [SCORING.md](../../SCORING.md); source data is kept
separate from computed scores and synthetic test fixtures.


## Checkpoint 6 frozen audit — 13 November 2026

Validated **15,607 genuine records**: 87 current and 15,520 forecast records,
83 destinations and 475 coherent fetch groups. Latest retrieval:
`2026-11-13T15:31:08.745753+00:00`. Model/schema, unique keys, catalogue
membership and fetch identities passed; all previously committed rows remain.
SHA256: `d567fc974f589e1ec0f42096371b2f8e6e4416988f7767cae9d88c4569b83f82`.
The active CSV was byte-identical after the VS Code preview checks; those
loads reported saved-forecast reuse. Offline stress rows stayed in temporary
files. This count describes a frozen checkpoint, not a permanent constraint.
See [validation for this checkpoint](../../PHASE5_QUALITY_REVIEW.md#checkpoint-6-validation--13-november-2026).


## Feature integration snapshot — 14 November 2026

The asier/feature integration preserves both genuine histories: the validated
22,487-record candidate and the main working folder's 8,284 records. Their
shared record keys had identical values. The main folder contributed 280
additional records, producing **22,767 unique records** (87 current, 22,680
forecast), 83 destinations and 654 fetch groups. Original timestamps, provider
identities and earlier observations are preserved; no synthetic rows, revised
scores or replacement timestamps were introduced. Rows need not be globally
chronological; analytics selects batches using their timestamps.

WeatherStore validation and the full offline suite passed on this union.
This count describes the integration snapshot, not a fixed expected future
size or a guarantee that forecasts remain fresh. Later genuine appends should
be preserved and reviewed before publication.
