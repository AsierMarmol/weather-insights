# Phase 5 - Quality Review

Updated: 12 November 2026. **In progress:** P5.1 model/storage acceptance approved by Christian and merged in [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); P5.2 API/security/save acceptance merged in PR #14 with Selin's approval (Alejandra was the planned reviewer); P5.3 analytical acceptance approved by Selin and merged in [PR #17](https://github.com/AsierMarmol/weather-insights/pull/17) (dev `bfd9fd7`); P5.4 Dashboard/chart acceptance completed on `selin/feature` and awaiting Asier's review; P5.5 pending.

## Purpose and dependencies

Verify the integrated app against the teacher rubric. Component tests already belong to implementation; rerun affected checks and fix actual gaps rather than repeating development as new tasks.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Model/storage acceptance | Alejandra | Christian | P4.1-P4.3 merged | Validate catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity. | Completed locally: three gaps fixed, 21 new tests, 333 total pass, Flake8 clean; commit ac30f13, [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); approved by Christian and merged |
| P5.2 | API/security/save acceptance | Gabriel | Alejandra | P4.1-P4.3 merged | Exercise input/key/location/network/server/quota/malformed responses, partial batches, cache saves and safe failure messages. | Completed locally: one gap fixed (key file in another encoding), 43 new tests, 376 total pass, Flake8 clean; merged in PR #14 with Selin's approval (Alejandra was the planned reviewer) |
| P5.3 | Analytical acceptance | Christian | Selin | P4.1-P4.3 merged | Verify all day windows, clock changes, threshold boundaries, missing/stale metrics, driving cap, ties and three distinct analyses. | Completed locally: no analytical defect found, 22 new acceptance tests; 403 passed, 2 skipped, 2 failed (Dashboard timeouts from a storage lookup cost, reported to its owners); approved by Selin and merged in PR #17 (dev `bfd9fd7`) |
| P5.4 | Dashboard/chart acceptance | Selin | Asier | P4.4 merged | Validate the independent Dashboard: all 83 map markers, hover values, plotted inputs and units, weather-only ranks/ties, interactive filters, windows, freshness and empty/unavailable states against common results. | Completed on `selin/feature` from dev `bfd9fd7`: three Dashboard defects fixed (map centre, wheel zoom, hidden limit label) plus table wording; 3 new tests; 410 passed, 0 skipped (macOS), Flake8 clean; awaiting Asier's review |
| P5.5 | Searcher/integration and rubric walkthrough | Asier | Gabriel | P5.1-P5.4 | Validate seasonal/manual preference persistence, All options, top-five/full-table consistency, complete user journey, every rubric row and actual team contributions. | Pending |

## Implementation and acceptance

Use the Phase 2 rubric mapping and actual implementation. OOP: reusable inheritance, deliberate visibility, special method and property. API: dotenv, validation, distinct errors, graceful batches. Data: every successful fresh fetch saved with timestamps, genuine accumulated dataset, three analyses across comparison/derived metrics. UI: two interactive views and two correct labeled charts. Repo/team: installable clean clone, accurate README/AI records/trailers and meaningful work from all five. Do not infer approval or understanding from a role label. Required stubs must be implemented by delivery; an empty __init__.py is valid. Include `uv run --locked flake8 src tests scripts app.py` alongside the relevant tests before accepting changes; the shared default line limit is 79 characters.

Read [Phase 2](PHASE2_SCOPE.md) for product rules, shared schema and the worked example; [API contract](WEATHER_API_CONTRACT.md) for provider behavior; [roles](TEAMROLES.MD) for ownership. Each owner includes tests/docs/fixes. Follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance) when decisions change. The instructor README governs final acceptance; plans are not proof of completed functionality.

## Task prompt

```text
Work on <task ID> in PHASE5_QUALITY_REVIEW.md as <actual requester>.
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
| 12 November 2026 | Phase 5 start | Prerequisites checked on GitHub: P4.1 (PR #10, Gabriel), P4.2 (PR #11, Asier) and P4.3 (PR #12, approved by Gabriel and merged into dev `27e088e`). Baseline at `27e088e`: 312 passed, Flake8 zero findings. | Phase 4 accepted |
| 12 November 2026 | P5.1 | Alejandra/Claude Code accepted models/storage against catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity; three actual gaps found and fixed (details below). 333 passed; Flake8 zero findings; genuine CSV and catalog byte-identical and permissions unchanged; no live requests. | Awaiting Christian's review |
| 12 November 2026 | P5.2 | Gabriel/Claude Code accepted the API/security/save path through the connected app: credentials, input, location, network, server, quota and malformed responses, partial batches, cache saves and safe messages (details below). One actual gap found and fixed. 376 passed; Flake8 zero findings; genuine data byte-identical; no live requests. | Awaiting Alejandra's review |
| 12 November 2026 | P5.3 | Christian/Claude Code accepted the analytics against windows, daytime, clock changes, thresholds, scoring, ties, both rankings, the three analyses and missing/invalid/stale data, on dev `cda1cc2` (details below). No analytical defect found; 22 regression/acceptance tests added. 403 passed, 2 skipped, 2 failed (Windows; the two failures are Dashboard AppTest 60-second timeouts explained below, not analytical results); Flake8 zero findings; genuine data byte-identical; no live requests. | Awaiting Selin's review |
| 12 November 2026 | P5.3 review | Selin approved PR #17 and it was merged into dev `bfd9fd7`. Post-merge check with Claude Code on `bfd9fd7` (macOS): full suite 407 passed, 0 skipped; Flake8 zero findings; the new acceptance tests rerun, read and mutation-checked. No analytical defect found (details in the P5.4 section). | Merged |
| 12 November 2026 | P5.4 | Selin/Claude Code accepted the independent Dashboard on dev `bfd9fd7` against all P5.4 criteria with automated and visual checks (details below). Three visual defects and one wording gap fixed in `dashboard.py`; 3 tests added and 4 strengthened. 410 passed, 0 skipped; Flake8 zero findings; genuine data byte-identical; no live requests. | Awaiting Asier's review |

## Next action

P5.1, P5.2 and P5.3 are merged (PR #13, #14, #17). Selin's P5.4 Dashboard/chart acceptance is completed on `selin/feature` and awaits Asier's review. After P5.4 is accepted, Asier runs the connected walkthrough (P5.5) with Gabriel reviewing, recording failures and fixes with actual evidence. The storage lookup cost reported in P5.3 remains open for the storage/service owners (Alejandra/Gabriel). Phase 5 is not yet completed.

### P5.1 model/storage acceptance - 12 November 2026

Alejandra / Claude Code, on `Alejandra/feature` from dev `27e088e`. Acceptance reused the P3.1 component tests and added `tests/test_model_storage_acceptance.py` (17 tests) for the criteria they did not cover, plus 4 regression cases in `tests/test_models.py` and `tests/test_storage.py`.

Checked and passing without changes: the real 83-row catalog (also with Windows line endings and a byte-order mark); all 164 genuine weather rows reload with unique keys, catalog city IDs and provider coordinates within about 11 km of the catalog point; every fetch group has one city, kind and retrieval time; the latest genuine forecast for Toledo, Segovia and Seville is one 40-period fetch on a three-hour grid; every genuine row round-trips through the model. On a temporary copy of the genuine file, appending synthetic rows keeps every existing byte as a prefix, reloads through a new store instance, and a retry writes nothing. Failed fsync, failed replace and a failed mid-copy leave the previous file and no temporary files. OOP: frozen validated value objects with equality/hashing, computed properties, `__str__`/`__repr__`/`__lt__`, a private name-mangled lock shared per file and a read-only `path` property.

Three actual gaps were found and fixed in `models.py`/`storage.py`:

1. A catalog that is not valid UTF-8 raised a raw `UnicodeDecodeError` instead of `CatalogError`. It now reports `<file> is not valid UTF-8`.
2. Every save replaced `weather_records.csv` with a temporary file created owner-only (`0o600`), so a teammate's data file silently lost group/other read access (Git does not track this). Saves now keep the previous file's permissions, and a first file follows the user's umask. The temporary file is created exclusively, so a name clash can never remove another file.
3. A CSV row with missing cells was reported as "schema_version and provider_city_id must be integers". It is now reported as a column mismatch with its line number.

The new regression tests failed against the dev `27e088e` sources (permissions, non-UTF-8 catalog and short rows) and pass now. Full suite: **333 passed** (312 before); Flake8 zero findings. Tests read the genuine catalog and weather file only, and an autouse check confirms their bytes and permissions are unchanged; all writes use pytest temporary copies. The CSV schema, record key and public interfaces are unchanged.

Limitations: one writing process per clone remains the supported model (the lock is per process). A weather CSV saved with a byte-order mark (for example by a spreadsheet program) is reported as having an unexpected header and is not modified; it must be restored from Git. Permission checks are skipped on Windows. Importing the retained historical JSONL evidence remains deferred.

**Status:** committed (ac30f13) and submitted in [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13) into dev; review requested from Christian (christiansawaya-code). Not approved or merged.

### P5.2 API/security/save acceptance - 12 November 2026

Gabriel / Claude Code, on `gabrielstec/feature` from dev `bfa3f36`. Acceptance reused the P3.2 client/service tests and the P4.3 journeys, and added `tests/test_api_security_acceptance.py` (43 tests) that drive the real Streamlit app (AppTest), `WeatherService`, `OpenWeatherClient` and `WeatherStore` with fake HTTP and temporary files. Live HTTP is blocked and a fixture checks the genuine `data/` files are byte-identical after each app test.

Checked and passing without changes:

- **Credentials:** `variables.env` written on macOS or Windows (LF, CRLF, byte-order mark, quotes, `export`, inline comment) is read; a shell variable takes precedence; a missing or blank key shows the key message with no request, no cached service and no results. The key travels only as the `appid` parameter over HTTPS to `api.openweathermap.org`, with redirects disabled and (5, 20) s timeouts; it never appears in the page, tables, error objects, `repr` or exception chains, and provider error bodies are never echoed.
- **Location:** a forecast for a place about 50 km away, another country, another name or provider ID is `invalid_data`, is not saved, and the other cities continue; 404 is `location_not_found` without retry.
- **Network and server:** connection failures and timeouts retry once; 5xx retries once (recovering when the second answer succeeds); 400, redirects and unexpected statuses do not retry. Messages are the fixed Searcher texts; exception text with a URL and key is not shown.
- **Quota and batches:** 401 stops the batch after one request and saves nothing; 429 stops it with an explicit result for every remaining city, and the next search fetches only the missing cities. One process-wide 40-calls/minute limiter is shared by every client.
- **Malformed responses:** non-JSON, non-object, missing/empty/invalid period lists, a missing city block, duplicate or missing period times are `invalid_data` and never saved; unreadable, non-finite or out-of-range metrics are saved blank, never as zero.
- **Saves and reuse:** each fresh forecast is saved once with its retrieval time and one fetch ID per response; a search at exactly the 3-hour TTL is served from the cache with no request or row, one minute later it fetches and appends new groups; a new service reuses the saved fresh groups after a restart.
- **Messages:** every API error code and batch-stop code has a fixed Searcher message without placeholders or secrets.

One actual gap was found and fixed:

1. A `variables.env` saved as UTF-16 (Windows PowerShell 5 `echo ... > variables.env`, or Notepad's "Unicode" option) raised a raw `UnicodeDecodeError` or, without a byte-order mark, silently hid the key, and the app only said the key was "missing or rejected". `config.get_api_key()` now reports `variables.env is not UTF-8 text` with how to resave it (a key supplied by the shell still wins), and the Searcher shows that fixed setup guidance under the key message (`searcher.py`, three lines in Asier's P4.1 file; the text comes only from `config`, never the key). README troubleshooting gained a row.

The 7 tests covering this gap fail against the `bfa3f36` sources and pass now; the other 36 confirm behavior that already worked. Full suite: **376 passed** (333 before); Flake8 zero findings. No live request was made: the P3.2 live check and P2.5 genuine multi-city verification remain the live evidence.

Limitations: the rate limiter is per process, so two separately started apps sharing one key are not paced together. Weather records are not encrypted or access-controlled beyond the file system (they contain no personal data or key). The existing outstanding P3.2 records (PROMPTS.md and the Phase 3 log) were corrected to show PR #6 approved and merged.

**Status:** completed locally; awaiting commit, PR into dev and Alejandra's review. Not approved or merged.

### P5.3 analytical acceptance - 12 November 2026

Christian / Claude Code, on `christian/feature` fast-forwarded to dev `cda1cc2` (a descendant of `1e43be3`, adding the P4.4 acceptance notes and the accumulated 82-destination forecasts). Since P3.3 the engine (`analytics.py`) changed only by the P2.5 line-length reformatting; its behavior is unchanged. Acceptance reused the existing tests where they already prove a requirement and added `tests/test_analytics_acceptance.py` (22 tests) for the boundaries they did not cover.

Already proven by existing tests (rerun, passing): the worked example and the three analyses (`test_analytics.py`), inclusive thresholds and the zero floor, the excluded reference time and included window end, the autumn clock change and off-grid 09:00/18:00 local boundaries, a missing fifth-day slot, staleness at exactly three hours versus one second more, other-city/mixed-fetch/mixed-retrieval/current-kind groups, duplicate timestamps, reason precedence, ANY/AND filters on the real catalog, the trip tie-break order, the driving cap, the service/store integration and the P2.5 genuine replay (`test_analytics_integration.py`); seasonal Dashboard criteria, weather-only competition ranks (1, 1, 3), city_id order within ties and filters that keep ranks (`test_dashboard.py`); seasonal Searcher defaults and the cached fifth-day refresh (`test_searcher.py`, `test_app_integration.py`).

Added and passing without code changes:

- **Windows:** for reference times every 7 h 13 min 17 s across March 2026-March 2027 (both clock changes, month and year ends, on and off the grid), every 1-5-day window holds exactly three daytime slots per day, all strictly after the reference time, at or before the end, on whole three-hour UTC times. The reason is checked by hand: Madrid daytime holds the 09/12/15 UTC slots in both CET and CEST. The spring clock change (28 March 2027) and a reference time already on 1 January in Madrid are spelled out.
- **Fifth day:** the end slot of a five-day window is included and required. A cached forecast that is still fresh (exactly three hours old) but no longer reaches the fifth-day end becomes `missing_periods`, never a 14-slot result. The Searcher then refreshes it once. Genuine evidence: replayed at `12:37:35 UTC`, the three 11:29 P2.5 groups end at 17 November 09:00, while the five-day window needs 12:00.
- **Missing and malformed data:** a missing temperature, probability or wind in any required slot gives `missing_metrics` with null scores, not zero. Missing values outside the window or at night do not matter. NaN, infinity, booleans and text cannot enter a record. Two partial fetch groups that would together cover the window are `invalid_data`, never stitched.
- **Unrounded ranking:** Segovia (26/27 checks, 75 min: 95.046) ranks above Seville (27/27, capped penalty: 95.0), although both display as 95.0 and a rounded score would favour Seville on weather match. The Dashboard ranks the same rows by weather alone, with Seville first.
- **Genuine catalog replay:** for 1-5 days at the historical reference time, the latest group per city saved by then (82 destinations; Barcelona has none and is `fetch_failed`) is compared with an independent tally of the raw CSV text. The tally uses no WeatherRecord, zoneinfo or analytics code. It is compared on reason, coverage, weather match, all-three percentage, mean temperature, highest slot probability, highest slot wind, final score and trip order. Dashboard competition ranks, the order within ties and a Coast display filter that keeps the global ranks are compared too. The Dashboard criteria are its own seasonal defaults (autumn 16-24 °C, ≤30%, ≤25 km/h) from `product_defaults.json`.

Mutation check (temporary edits, then restored): ranking on rounded scores, an exclusive window end and stitching fetch groups each make the new tests fail. A fixed UTC+1 offset instead of Europe/Madrid does not change any selected three-hour slot. That case is already caught by the off-grid boundary test in `test_analytics.py`.

No defect was found in analytics, so no source file changed. Wording was reviewed too: both views call the probability statistic the highest slot probability, and the Dashboard states it is not a whole-window rain probability. The Searcher's "below your limit" text is already qualified by "(boundaries included)". No Dashboard integration defect was found for Selin.

Validation on Windows: 403 passed, 2 skipped, 2 failed (Windows; the two failures are Dashboard AppTest 60-second timeouts explained below, not analytical results) (two POSIX-permission checks skip on Windows); `uv run --locked flake8 src tests scripts app.py` zero findings. The genuine CSV bytes are checked unchanged; no live request was made.

**Unresolved, outside analytics - storage lookup cost (reproducible):** `tests/test_dashboard.py::test_old_forecasts_warn_and_refresh_fetches_again` and `::test_genuine_saved_forecasts_rank_without_requests` fail on this PC, also when run alone. Each hits Streamlit AppTest's 60-second limit (96.7 s and 60.0 s). The cause is `WeatherStore.latest_forecast(city_id)` (`storage.py`): it re-reads and re-validates the whole weather CSV for every city. A full Dashboard load makes 83 such lookups:

```text
uv run --locked python -c "import time; from weather_app.storage import WeatherStore, load_destinations as L; s=WeatherStore(); t=time.perf_counter(); [s.latest_forecast(d.city_id) for d in L()]; print(time.perf_counter()-t)"
```

The 83 lookups take 1.57 s on the 164-row CSV of `1e43be3` and 28.7 s on the 3,324-row CSV after `18c0f04`, and the cost keeps growing as data accumulates. A single `load()` takes 0.41 s. This is a performance defect in the shared save/reuse path, not in the scores; the analytics results are correct. It belongs to the storage/service owners (Alejandra/Gabriel), and it affects Selin's Dashboard load and P5.4. For example, one read per batch, or a per-city index, would remove the repeated work. It is reported to them rather than changed here, because it lies outside `analytics.py`. The 383-test Windows baseline at `1e43be3` used the smaller CSV.

Limitations and observations:

- Genuine data covers one collection on 12 November 2026, and only up to five days ahead.
- One risk is not reproduced against the real provider. Saved responses start at the first three-hour slot after retrieval. If a batch that started just before a slot time (00, 03 ... 21 UTC) fetches a city just after it, that city's forecast may lack the first required slot and show as unavailable (`missing_periods`). It is not a cached result, so no refresh retries it; the next search does. This touches `searcher.search_destinations`, which both views use. It is recorded for Asier (P5.5) and Selin (P5.4) rather than changed. Rerunning the search clears it.

**Status:** completed locally; awaiting commit, push and Selin's review. Not approved or merged. P5.4 and P5.5 are not claimed.

*Later status:* committed as `1813421`, approved by Selin and merged into dev in [PR #17](https://github.com/AsierMarmol/weather-insights/pull/17) (`bfd9fd7`).

### P5.4 Dashboard/chart acceptance - 12 November 2026

Selin / Claude Code (Anthropic Claude Opus 5.5), on `selin/feature` fast-forwarded to dev `bfd9fd7` (P5.3 merged in PR #17; PR #16's status notes and accumulated 82-destination forecasts merged before it). P4.4 already implemented the Dashboard, so this step checked it against the acceptance criteria and corrected actual gaps only; nothing was redesigned.

**P5.3 review (post-merge).** PR #17 was already approved by Selin and merged when this check ran, so it was verified on the merged version. The new `tests/test_analytics_acceptance.py` was read against the approved rules and rerun: 407 passed, 0 skipped on macOS at `bfd9fd7`; Flake8 clean. Mutation check (temporary, restored): an exclusive window end fails the fifth-day test. Rounding Dashboard scores before ranking is not detected, but this cannot change a Dashboard rank: every available row in one load has the same number of checks, so distinct weather scores differ by at least 100/45 points. No analytical defect was found. The two Windows AppTest timeouts reported in P5.3 were not reproduced on macOS (10.1 s and 6.4 s). Christian's PR description and records still said "awaiting Selin's review"; the status lines above now record the merge.

**Checked and passing without change** (existing tests rerun, new ones added where marked):

- Before any load and without a Searcher run, the map shows all 83 catalog destinations at their catalog coordinates as grey "Weather not loaded" markers, and no request is made.
- The day selector defaults to 3 (1-5). The seasonal criteria (autumn 16-24 °C, probability ≤ 30%, wind ≤ 25 km/h; summer 22-30 °C) come from `product_defaults.json`.
- Ranks are weather-only competition ranks: no driving penalty, shared ranks for ties, `city_id` order within ties. Ranks stay global under filters, and every marker stays on the map.
- Dashboard and Searcher keep separate state across navigation. Changed days show a notice and never relabel the old overview.
- Refresh, cache reuse and failure states:
  - A refresh reuses the cache and saves nothing new.
  - Hover, filters and navigation make no requests and no saves.
  - Partial failures, failed saves (never ranked), a missing key and forecasts more than three hours old each produce a safe, explained state.
- **New:** a replay of a temporary copy of all genuine records, run at the time of the last saved response (12 Nov 2026 12:37:35 UTC):
  - All 82 saved forecasts are reused. Barcelona, which has no genuine forecast, is the only request, and it gets a fake 404, so nothing synthetic is ranked.
  - The page reports "82 of 83 destinations can be ranked".
  - Every hover's temperature, rank ("of 82") and score, and the ranking chart's order and values, match an independent tally of the raw CSV. The tally uses no engine code.
- **New:** every chart agrees with its table:
  - ranking, weather comparison for all three measures, and the share of slots meeting all three criteria, with k/n counts;
  - all daytime slots are 9 for 3 days.
- **New:** the two empty filter states:
  - "None of the selected destinations has a complete forecast" (no empty charts, reason table shown);
  - "No destinations match these filters", with all 83 markers still present.

**Defects found and fixed (`dashboard.py`):**

1. **Map centred too far north.** The visual check showed Plotly's `fitbounds="locations"` centring the map at about 42.9° N instead of the destinations' middle (39.8° N). The markers filled only a small part of the frame, with much of France and North Africa shown. The map is now centred on the middle of the catalog coordinates at a fixed mainland-Spain zoom (`MAP_SCALE`), checked at desktop and phone widths.
2. **Page scrolling zoomed the map.** Scrolling the page with the mouse over the map changed its zoom (22 → 14.5 in the browser), losing Spain. Mouse-wheel zoom is now off for the map; the +/- buttons still zoom.
3. **Comparison limit label hidden.** In the weather-comparison chart, the "Seasonal range" and "Limit" labels sat behind the first bar. The limit is now named in the chart title, for example "(seasonal range 16-24 °C shaded)" or "(limit 25 km/h dashed)".
4. **Table wording.** The comparison table said "Highest precipitation probability" and "Highest wind speed", while the chart axes say "Highest slot …". The table now says "slot" too, so it is not read as a whole-window value.

**Tests changed:**

- `test_genuine_saved_forecasts_rank_without_requests` now replays only the 164 rows saved by 11:34 UTC, as its P2.5 evidence intends; previously it replayed the whole later file.
- The two loads over thousands of saved rows get a 240-second AppTest limit (`LARGE_STORE_TIMEOUT`), so they check behaviour rather than the open storage cost. This does not make the real app faster.

**Validation (macOS, Apple Silicon):**

- **Automated:** `uv run --locked python -m pytest`: **410 passed, 0 skipped, 0 failed** (407 at `bfd9fd7`; 3 new tests). `uv run --locked flake8 src tests scripts app.py`: zero findings. The genuine `weather_records.csv` checksum is unchanged, and no live API request was made.
- **Visual:** the real `app.py` in a throwaway harness outside the repository, with live HTTP blocked. Two setups were used:
  - **Historical replay (not a fresh forecast):** a temporary copy of the genuine CSV at its historical time. Checked:
    - the map before and after loading, and that page scrolling over it keeps the zoom;
    - hover values, for example "Níjar · Coast, Nature · 16.4 °C · rank 12 of 82 · 88.9%", and Barcelona grey with only its reason;
    - all three charts and tables, ties and the comparison titles;
    - the Coast filter, which dims other markers while keeping global ranks;
    - navigation to the Searcher and back, which keeps the overview and filters;
    - the map at phone width.
  - **No API key:** the missing-key error with its setup text.

**Remaining limitations:**

- **Load time:** `WeatherStore.latest_forecast` re-reads the whole CSV for each destination. A full Dashboard load spends about 2.4 s on these lookups on macOS with 3,324 rows, and 28.7 s on Christian's Windows PC. The cost grows as data accumulates. This is a storage/service fix for Alejandra/Gabriel and is not changed here.
- **Load crossing a slot time:** a fresh full load crossing 09:00, 12:00 or 15:00 UTC can mark some cities `missing_periods`. This is the Searcher-path risk recorded in P5.3; a refresh clears it.
- **Map rendering:** country outlines need Plotly's online base map. At phone width, the chart title and Plotly's toolbar overlap.
- **Genuine data:** genuine forecasts cover 82 destinations from one collection on 12 November 2026; Barcelona has none.

**Status:** completed on `selin/feature`; awaiting Asier's review. Not approved or merged. P5.5 and final delivery are not claimed.
