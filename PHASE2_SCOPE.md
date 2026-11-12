# Phase 2 - Scope and Data Preparation

Updated: 12 November 2026.

## Current checkpoint

Phase 1 is complete. The Phase 2 foundation was approved by Gabriel and Christian in PR #3. Production models/storage, API/service and analytics are merged, including PR #7 integration and PR #8 validation fixes. P2.5 passed on a genuine three-city sample and was approved by Gabriel and Christian in merged PR #9. P4.1 Searcher and P4.2 Dashboard are approved and merged; P4.3 integration is implemented locally and awaits Gabriel review. Catalog/source limitations remain documented in the reference notes.

## Deliverables

| Step | Deliverable | Owner | Reviewer | Depends on | Finish condition / status |
| --- | --- | --- | --- | --- | --- |
| P2.1 | Product specification and two-view outline | Asier | Gabriel | Phase 1 | Rules and rubric mapping below prepared; user decisions approved; reviewed by Gabriel (12 November 2026) |
| P2.2 | Complete destination catalog and sources | Asier | Christian | P2.1 | 83 rows/nine columns checked; Christian approved the catalog foundation in PR #3; retain documented source/access limitations |
| P2.3 | Weather access and provider contract | Asier | Gabriel | P2.1 | Historical live checks passed; WEATHER_API_CONTRACT.md prepared; reviewed by Gabriel (12 November 2026) |
| P2.4 | Shared data and calculation specification | Asier | Christian | P2.1 + P2.2 + P2.3 | Schema, component inputs/outputs and worked example approved by Christian in PR #3 |
| P2.5 | Verify the shared fetch/save/readback path | Asier | Gabriel | P3.1 + P3.2 | Verification passed: 3 cities, 123 new genuine records; reload/cache/idempotence and 1-5-day replay passed; approved by Gabriel and Christian, merged in PR #9 |

Reviewed P2.1-P2.4 allow component development. P2.5 is a deferred integration check after the Phase 3 components exist; it does not block their construction or require a second client/store. Complete it before accepting Phase 3 and starting live UI integration. Keep task IDs for continuity.

## Product rules

A local Streamlit application recommends mainland-Spain destinations for car trips from Madrid. Use the existing [nine-column catalog](data/reference/destinations.csv) and [source notes](data/reference/README.md). No flights, trains, booking or departure-date picker.

Users select the next **1-5 rolling days from use**, default **3**. Capture a common aware UTC search time. Evaluate native three-hour timestamps with `run_at < valid_at <= run_at + 24 * days hours`, keeping Europe/Madrid local daytime **09:00 inclusive to 18:00 exclusive**. All expected daytime periods must exist; no interpolation or shortened fifth day.

Initial settings come from [product_defaults.json](data/reference/product_defaults.json): winter 10-18 C, spring 18-26 C, summer 22-30 C, autumn 16-24 C; precipitation probability <=30%; wind <=25 km/h. Seasons use Europe/Madrid months (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov). These are editable preferences, not climate averages. Initialize on first use or explicit reset only; preserve manual choices across navigation, reruns and season boundaries. Apply identical preferences to all destinations.

Activities: Coast, Nature, History and heritage, Food and gastronomy, Urban experiences. Sizes: Large city, Medium city, Small city or town. Both selectors visibly default to **All** and derive available values from the catalog. Match ANY selected activity and ANY selected size; combine the two groups with AND. Empty internal selections mean All. These are eligibility filters, not score weights.

For each complete forecast period, award one check for temperature within the inclusive range, one for probability <= limit and one for wind <= limit. Imperfect weather remains eligible. Missing values/coverage make a destination unavailable, not a zero-score success.

```text
weather_match = 100 * passed_checks / (3 * evaluated_periods)
travel_penalty = min(car_duration_min / 60, 5)
final_score = max(weather_match - travel_penalty, 0)
all_preferences_pct = 100 * suitable_period_count / evaluated_periods
```

Suitable periods satisfy all three preferences simultaneously. This explanatory percentage adds no extra score weight. Sort unrounded final score descending, weather match descending, driving minutes ascending, then city_id ascending. Distance is informational, not a second penalty.

## Views and analyses

- **Searcher (Asier):** shared editable days/weather/activity/size controls; up to five available recommendations plus the full eligible ranking; distances, drive times, score explanation, coverage and unavailable states.
- **Dashboard (Selin):** interactive destination/activity/size filters and shared day/preferences controls. Consume the same results rather than recalculating scores or fetching separately. *Superseded by P4.4 (12 November 2026):* the Dashboard is an independent weather overview of all 83 destinations on a map with its own 1-5-day window and Load/refresh, seasonal default criteria and a weather-only ranking (weather match %, no driving penalty, shared ranks for ties). It still uses the same service, cache, save path and analytics; see [Phase 4](PHASE4_ANALYTICS_UI.md#p44-independent-spain-weather-dashboard---12-november-2026).
- Three analyses: suitability ranking; cross-city weather comparison (mean temperature, maximum precipitation probability and maximum wind over the same daytime periods); count/percentage of periods meeting all preferences. Label aggregations and units explicitly: maximum period probability is not whole-trip probability, and forecast periods are not guaranteed good-weather hours.
- At least two labeled charts must use genuine fetched/logged data. Save every fresh successful request with retrieval and provider timestamps. Cache displays do not create new records. No historical-trend chart, forecast-versus-reality feature or continuous collector is required.

## P2.4 shared data and calculation specification

Use standard-library dataclasses, one normalized weather CSV and simple result dictionaries. This specification is implemented by the merged Phase 3 components; the normalized dataset exists and is verified below.

| Object / output | Contract |
| --- | --- |
| Destination | Nine catalog fields; numeric coordinates/route values; activities tuple; computed drive_hours and useful repr/str |
| SearchPreferences | days, temperature_min_c, temperature_max_c, max_precipitation_probability_pct, max_wind_kmh, activities tuple, destination_sizes tuple; empty tuples mean All |
| WeatherRecord | Exactly the CSV fields below; aware UTC datetimes internally; optional numeric metrics are None; one UUID fetch_id for each fresh HTTP response |
| Service result | records list, from_cache bool, error None or safe code/message; codes: invalid_input, authentication, location_not_found, rate_limited, network, provider, invalid_data, storage |
| Analysis result | city_id, status, reason, run_at_utc, days, forecast_retrieved_at_utc, expected_periods, evaluated_periods, temperature_passes, precipitation_passes, wind_passes, weather_match_pct, travel_penalty, final_score, suitable_period_count, all_preferences_pct, mean_temperature_c, max_precipitation_probability_pct, max_wind_kmh |

Application store: `data/weather/weather_records.csv`, created by P3.2 and extended by P2.5:

```text
schema_version,fetch_id,city_id,kind,retrieved_at_utc,valid_at_utc,latitude,longitude,temperature_c,wind_kmh,precipitation_probability_pct,humidity_pct,cloud_pct,provider_city_id,provider_city_name
```

Schema version 1; kind current/forecast; coordinates and provider identity describe the returned weather location. Keep catalog identity separate. UTC ISO timestamps in CSV/results; blank numeric cells represent None, not zero. Current precipitation probability is None. Validate finite values, coordinate ranges, preference bounds and tags before use.

| Owner / module | Shared entry points |
| --- | --- |
| Alejandra: models.py, storage.py | load_destinations(path) -> list[Destination]; WeatherStore(path).append(records), .load(city_id=None, kind=None), .latest_forecast(city_id) |
| Gabriel: client.py, config.py, service.py | JSONAPIClient._get_json(path, params); derived OpenWeatherClient.current(destination)/.forecast(destination); WeatherService.current/forecast(destination, force_refresh=False) and .forecast_many(destinations, force_refresh=False); config.get_api_key() and future load_product_defaults() |
| Christian: analytics.py | analyse_destinations(destinations, forecasts_by_city, preferences, run_at_utc) -> full ordered list of result dictionaries |
| Asier: searcher.py, app.py | initial_preferences(now_utc, defaults), shared controls/search state and service wiring |
| Selin: dashboard.py | render_dashboard(analysis_rows, catalog_rows); catalog dictionaries use activity lists and canonical names. Since P4.4: render_dashboard_page() over the full catalog, with overview_preferences, weather_ranks, map_points/map_figure |

Store a whole forecast response as one fetch group. Latest forecast must be one newest group, never stitched from different issues. Repeated saves of the same (fetch_id, city_id, kind, valid_at_utc) are idempotent; a distinct fresh response gets a new fetch_id. Serialize writes per local process; handle failed/partial writes explicitly. The service saves once, then caches. Do not claim analytical success after failed persistence. Initial JSONL evidence can be imported deliberately without inventing retrieval times; do not mix synthetic fixtures into it.

Analytics is pure: no network, credentials, file writes, UI or implicit clock. Reject invalid preferences and naive/non-UTC run times. Forecast staleness is max(0, run_at - retrieved_at) > three hours; equality is allowed and fresh batch receipts can follow run_at. Unavailable reasons: fetch_failed, invalid_data, stale_forecast, duplicate_periods, missing_periods, missing_metrics (in that precedence). Unavailable rows follow ranked rows, sorted by city_id, with null metrics/pass counts, expected periods retained and evaluated periods zero. No fetch means retrieval time None. Filtered-out cities are omitted.

Shared UI state: search_preferences, search_run_at_utc, search_analysis_rows. The app owns updates; Dashboard filters do not reset preferences. Since P4.4 the Dashboard keeps separate dashboard_* state and never reads or changes search_* results. A new search recomputes coverage for its common time, using cached forecasts only when usable.

### Small worked example

Synthetic test inputs only, not real weather history: one day, three complete daytime periods, temperature 16-24 C, probability <=30%, wind <=25 km/h. Each tuple below is (temperature C, probability %, wind km/h).

| City | Three period inputs | Passed checks / 9 | All-three periods / 3 | Drive minutes | Final score |
| --- | --- | --- | --- | --- | --- |
| Toledo | (16,30,25); (20,0,10); (24,30,25) | 9 | 3 | 61 | 100 - 61/60 = 98.983333... |
| Segovia | (25,20,20); (20,31,20); (20,20,26) | 6 | 0 | 75 | 200/3 - 75/60 = 65.416666... |
| Seville | (16,0,0); (24,30,25); (25,31,26) | 6 | 2 | 351 | 200/3 - 5 = 61.666666... |

Segovia and Seville have identical weather points but different simultaneous suitability (0% vs 66.666...%). Christian turns this example and threshold, tie, missing/fifth-day, stale and clock-change cases into tests of the actual engine. No separate example-checking application is required.

## Teacher requirements

| Requirement | Owned work and acceptance |
| --- | --- |
| Reusable inheritance, deliberate public/protected/private members | Gabriel P3.2; P5.2 |
| Meaningful special method and computed property | Alejandra P3.1; P5.1 |
| dotenv, input validation, safe distinct failures and partial batches | Gabriel P3.2; P5.2 |
| Timestamp every fresh fetch; submit genuine accumulated data | P3.1/P3.2; Asier P2.5 verification; P6.1 |
| Three analyses in comparison and derived categories | Christian P3.3; P5.3 |
| Two interactive views and two labeled real-data charts | Asier/Selin P4; P5.4/P5.5 |
| Installable src package, clean-clone README, accurate AI record/trailers | Existing setup, component work and P6 |
| Actual contributions from all five; explain whole application | Individual component commits/reviews and P5.5/P6 |

The instructor README is authoritative; summary examples are guidance. Planned coverage is not a claim of completed rubric requirements.

## Task prompt

```text
Complete <P2 task> as its named owner. Read PHASE2_SCOPE.md, TEAMROLES.MD,
the provider contract and actual inputs. Work on the whole deliverable, preserve
the nine-column catalog and real data, and keep credentials private. Verify
the result, update the task status/progress and affected dependent steps.
Record substantive AI work with the actual requester/tool. Do not invent peer
approval or commit/push/merge without authorization.
```

## Phase progress log

| Date | Task | Actual result | Remaining work |
| --- | --- | --- | --- |
| 11 November 2026 | P2.1 | Group product decisions documented: car-only mainland Spain, rolling 1-5 days, seasonal editable defaults, All filters, three trip analyses and automatic saving | Gabriel review |
| 11 November 2026 | P2.2 | Asier/Codex prepared 83-city catalog; nine-column schema, categories, sizes and API-standard labels checked; corrected Lugo values already present | Source/activity/access and Christian review |
| 11 November 2026 | P2.3 | Initial two-city and full-catalog access checks completed; failure diagnostics returned 401/404; saved real responses; later replay checked all five windows at original run time | Gabriel review; cleaned retained data described in data/weather/README.md |
| 11 November 2026 | P2.4 | Shared schema, component boundaries, safe defaults, worked calculations and phase dependencies documented here; lazy credential loading and safe diagnostic failures verified with 25 offline tests; both starter views pass AppTest; no production model/store/engine claimed | Christian review and remaining P2.1-P2.3 reviews |
| 12 November 2026 | P2.1, P2.3 review | Gabriel reported his review of the product specification and the provider contract as complete; no corrections were raised. | Done for Gabriel's part; Christian's P2.2/P2.4 review still pending |
| 12 November 2026 | Foundation review | GitHub PR #3 contains Gabriel and Christian approvals; historical pending notes above describe their earlier state | Preserve source limitations; approval is not proof of every external source claim |
| 12 November 2026 | P2.5 | Three-city fetch/save/readback/cache verification passed; evidence below | Gabriel review pending |

## Next action

P2.5 was accepted in PR #9. Continue with P4.1 Searcher (Asier, reviewed by Gabriel), P4.2 Dashboard (Selin, reviewed by Asier), then P4.3 integration. Keep review status honest using [plan maintenance](PROJECT_PHASES.md#plan-maintenance).

### P2.5 verification - 12 November 2026

Asier / OpenAI Codex ran the production `WeatherService.from_environment()` and `WeatherStore` on dev `6b0a901`, using Toledo, Segovia and Seville. Six successful live requests (current + forecast per city) at approximately 11:29 UTC appended **123 genuine records** (3 observations + 120 forecast periods). The normalized store grew from **41 to 164 rows**, with 164 unique record keys; previous observations were retained. Local UTC matched the independent clock check, and provider response-date checks passed within 30 seconds.

Readback exactly matched the returned records and newest forecast groups. Repeating both endpoints through the original service and a new instance used saved/cache data; HTTP was blocked during these assertions. Cache reads and re-appending the same records left the CSV unchanged. No pending unsaved records remained. No synthetic data was written to the genuine store.

Replayed the sample at `2026-11-12T11:29:04.669987+00:00` with autumn preferences (16-24 C, probability <=30%, wind <=25 km/h, All filters). All three cities had complete 1-5-day daytime coverage (3/6/9/12/15 periods). Service and reloaded records produced identical results. Independent calculations checked thresholds, all-preference percentages, temperature means, maxima, travel penalties and ranking. Three-day scores: Seville 83.888889, Toledo 50.835185, Segovia 46.898148.

| City | Current fetch ID | Forecast fetch ID |
| --- | --- | --- |
| Toledo | 3fe32003-9542-4a44-9c4a-52ec861a2c48 | 5f188094-18a9-471c-9155-81a82d6caae3 |
| Segovia | 46aac75a-52a8-4b53-bbe1-d0e82d14b7cc | 93c655ea-1a12-4b06-bb42-cda59497238c |
| Seville | 3f1176b1-a29b-44fc-aace-58e4e996f8ca | 9bb6a9d5-dd22-482d-ae30-85db8ed1b51b |

`tests/test_analytics_integration.py::test_p25_genuine_multi_city_replay` replays these fixed groups offline for all five windows; later appends will not change the evidence. The one-off live harness stayed outside the repository. Its initial positional constructor call was corrected to keyword arguments, and the resumed baseline comparison accounted for Git's Windows line endings; no additional API fetch was needed and production code was unchanged.

**Validation:** full offline suite 237 passed; whitespace checks passed; credentials remain excluded.

**Status: approved by Gabriel and Christian and merged in PR #9 (12 November 2026).** The multi-city evidence remains replayable without fetching again. Optional historical JSONL import remains deferred: original evidence is retained separately and the actual application CSV now accumulates genuine data. No UI feature or final rubric acceptance is claimed.


### P2.5 pre-commit validation - 12 November 2026

Rechecked against the instructor's README and the phase acceptance map. Full offline suite: 237 passed; both existing starter views passed headless AppTest. Tests left all reference/weather data unchanged. The catalog loads 83 unique destinations; the normalized store loads 164 unique records across three cities and preserves the original committed data. All 18 Python files parse, local Markdown file links resolve and source/test/data/script folders contain no empty directories. Dependency lock validation and installed-package compatibility passed; source distribution and wheel build successfully. This checks package construction, not the later clean-clone or finished UI acceptance.

The configured key was absent from tracked working-tree files; the credential file is untracked/ignored and its example is blank. No extra live request was made. Corrected stale catalog-review wording, documented read-only genuine-data tests and made the development clone command select `dev`. The existing `.gitignore` edit remains untouched and is not part of P2.5. No blocking defect was found for this checkpoint; Gabriel review and Christian's multi-city analytical acceptance remain pending before Phase 4 acceptance. No commit or push was made.

P2.5 pre-commit lint follow-up: the initial validation did not include Flake8. After Asier flagged the editor diagnostics, a full scan found 529 formatting findings, including 517 long lines. Wrapped code/comments/docstrings and corrected whitespace in 17 Python files. All 18 Python syntax trees match the pre-format version after normalizing docstring whitespace; Flake8 now reports zero findings and all 237 tests pass. Added Flake8 to locked development dependencies and the README verification commands. No data, business-rule or `.gitignore` change was made by this cleanup; review remains pending.

12 November acceptance update: PR #9 was approved by Gabriel and Christian and merged into dev as f61c850. The P2.5 review gate is complete; earlier pending-review notes are historical.
