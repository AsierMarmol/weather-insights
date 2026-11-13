# Phase 5 - Quality Review

Updated: 13 November 2026. **In progress:** P5.1 model/storage acceptance approved by Christian and merged in [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); P5.2 API/security/save acceptance merged in PR #14 with Selin's approval (Alejandra was the planned reviewer); P5.3 analytical acceptance approved by Selin and merged in [PR #17](https://github.com/AsierMarmol/weather-insights/pull/17) (dev `bfd9fd7`); P5.4 Dashboard/chart acceptance approved by Asier and merged in PR #18 (dev `1784b8c`); P5.5 approved by Gabriel and merged in [PR #19](https://github.com/AsierMarmol/weather-insights/pull/19) (dev `2999dae`); Mac test results and desktop/mobile visual confirmation remain unconfirmed. Phase 5 verification is not yet fully closed. A user-reported storage failure is under follow-up review; see the 13 November entry below.

## Purpose and dependencies

Verify the integrated app against the teacher rubric. Component tests already belong to implementation; rerun affected checks and fix actual gaps rather than repeating development as new tasks.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Model/storage acceptance | Alejandra | Christian | P4.1-P4.3 merged | Validate catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity. | Completed locally: three gaps fixed, 21 new tests, 333 total pass, Flake8 clean; commit ac30f13, [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); approved by Christian and merged |
| P5.2 | API/security/save acceptance | Gabriel | Alejandra | P4.1-P4.3 merged | Exercise input/key/location/network/server/quota/malformed responses, partial batches, cache saves and safe failure messages. | Completed locally: one gap fixed (key file in another encoding), 43 new tests, 376 total pass, Flake8 clean; merged in PR #14 with Selin's approval (Alejandra was the planned reviewer) |
| P5.3 | Analytical acceptance | Christian | Selin | P4.1-P4.3 merged | Verify all day windows, clock changes, threshold boundaries, missing/stale metrics, driving cap, ties and three distinct analyses. | Completed locally: no analytical defect found, 22 new acceptance tests; 403 passed, 2 skipped, 2 failed (Dashboard timeouts from a storage lookup cost, reported to its owners); approved by Selin and merged in PR #17 (dev `bfd9fd7`) |
| P5.4 | Dashboard/chart acceptance | Selin | Asier | P4.4 merged | Validate the independent Dashboard: all 83 map markers, hover values, plotted inputs and units, weather-only ranks/ties, interactive filters, windows, freshness and empty/unavailable states against common results. | Completed on `selin/feature` from dev `bfd9fd7`: three Dashboard defects fixed (map centre, wheel zoom, hidden limit label) plus table wording; 3 new tests; 410 passed, 0 skipped (macOS), Flake8 clean; approved by Asier and merged in PR #18 |
| P5.5 | Searcher/integration and rubric walkthrough | Asier | Gabriel | P5.1-P5.4 | Validate seasonal/manual preference persistence, All options, top-five/full-table consistency, complete user journey, every rubric row and actual team contributions. | Approved by Gabriel and merged in PR #19. Windows evidence: 427 passed, 2 skipped; Flake8 clean. Mac/visual results unconfirmed; 13 November storage recovery follow-up requires review |

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

Dated entries describe their original submission state. The deliverable table and subsequent review entries provide the current status. The P5.3/P5.4 limitations below are historical findings; P5.5 records their current disposition.

| Date | Task | Actual result and evidence | Status |
| --- | --- | --- | --- |
| 12 November 2026 | Phase 5 start | Prerequisites checked on GitHub: P4.1 (PR #10, Gabriel), P4.2 (PR #11, Asier) and P4.3 (PR #12, approved by Gabriel and merged into dev `27e088e`). Baseline at `27e088e`: 312 passed, Flake8 zero findings. | Phase 4 accepted |
| 12 November 2026 | P5.1 | Alejandra/Claude Code accepted models/storage against catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity; three actual gaps found and fixed (details below). 333 passed; Flake8 zero findings; genuine CSV and catalog byte-identical and permissions unchanged; no live requests. | Awaiting Christian's review |
| 12 November 2026 | P5.2 | Gabriel/Claude Code accepted the API/security/save path through the connected app: credentials, input, location, network, server, quota and malformed responses, partial batches, cache saves and safe messages (details below). One actual gap found and fixed. 376 passed; Flake8 zero findings; genuine data byte-identical; no live requests. | Awaiting Alejandra's review |
| 12 November 2026 | P5.3 | Christian/Claude Code accepted the analytics against windows, daytime, clock changes, thresholds, scoring, ties, both rankings, the three analyses and missing/invalid/stale data, on dev `cda1cc2` (details below). No analytical defect found; 22 regression/acceptance tests added. 403 passed, 2 skipped, 2 failed (Windows; the two failures are Dashboard AppTest 60-second timeouts explained below, not analytical results); Flake8 zero findings; genuine data byte-identical; no live requests. | Awaiting Selin's review |
| 12 November 2026 | P5.3 review | Selin approved PR #17 and it was merged into dev `bfd9fd7`. Post-merge check with Claude Code on `bfd9fd7` (macOS): full suite 407 passed, 0 skipped; Flake8 zero findings; the new acceptance tests rerun, read and mutation-checked. No analytical defect found (details in the P5.4 section). | Merged |
| 12 November 2026 | P5.4 | Selin/Claude Code accepted the independent Dashboard on dev `bfd9fd7` against all P5.4 criteria with automated and visual checks (details below). Three visual defects and one wording gap fixed in `dashboard.py`; 3 tests added and 4 strengthened. 410 passed, 0 skipped; Flake8 zero findings; genuine data byte-identical; no live requests. | Approved by Asier; merged in PR #18 |

## Next action

P5.1-P5.5 are merged. Gabriel approved P5.5 in PR #19, but Mac test results and desktop/mobile visual checks are not yet confirmed. Gabriel should update his own feature branch from dev and record the tested commit, commands/results and browser/viewport checks. Asier can prepare P6.1 documentation while this evidence remains open; Selin performs P6.2 with Christian reviewing; Asier completes P6.3 with Gabriel reviewing. Phase 5 acceptance and Phase 6 delivery are not claimed complete.

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

**Status update:** approved by Asier and merged in PR #18 (dev `1784b8c`), verified on 12 November 2026. P5.5 and final delivery are not claimed.

### P5.5 readiness check - 12 November 2026

GitHub confirms P5.3 PR #17 approved by Selin and merged, and P5.4 PR #18 approved by Asier and merged. Local asier/feature was fast-forwarded to dev `1784b8c` without altering the existing .gitignore edit. Focused verification: 22 analytical acceptance tests passed; Flake8 zero findings. The full suite and visual walkthrough were not rerun in this readiness check. P5.5 is ready for Asier to start with Gabriel as reviewer; the known storage performance issue, slot-boundary risk, mobile layout limitation and actual rubric/contribution evidence remain to be evaluated.


### P5.5 integrated acceptance - 12 November 2026

AsierMarmol / OpenAI Codex, on `asier/feature` at current fetched dev `1784b8c`. No commit, push or merge performed. The pre-existing `.gitignore` change is preserved and is not part of this implementation. Actual GitHub approvals were checked: P5.1 Christian, P5.2 Selin (rather than the planned Alejandra), P5.3 Selin and P5.4 Asier.

**Changes and evidence**

- `storage.py` retains validated immutable records per store and reuses them only if freshly read file bytes match. A successful atomic save updates the snapshot; a failed save cannot enter the cache. Every call still reads the file, so same-size edits, another store's append, corruption, deletion and read-permission failures remain visible. Seven new tests in `tests/test_final_acceptance.py` cover these guarantees and the slot-boundary journey. Representative 83-city saved-forecast lookup time on this PC fell from **3.056 s to 0.069 s**. This is a local before/after measurement, not a promise for every computer or dataset. File reads and list scans still grow with history; the supported model remains one writing process per clone.
- A deterministic service test reproduces a load crossing 09:00 UTC. A city missing the first required slot stays unavailable; both views explain the boundary and advise a new search/refresh. A new window can reuse saved data without further HTTP calls. No interpolation, invented weather, shortened window, score change or automatic retry loop was added. This reproduces provider-like responses offline; it is not a new live provider experiment.
- `dashboard.py` moves the map heading to a Streamlit subheading outside Plotly's toolbar and adds accessible chart text. AppTest verifies rendering and both warning messages. **Fresh desktop/mobile visual confirmation is outstanding:** the computer-use browser host was unavailable. No new browser screenshot or visual pass is claimed. Plotly's geographical base map still needs browser connectivity to its CDN.
- Reviewed all tracked directories and Markdown documents. Updated stale current-status/navigation text in the README, phase plans, roles and API contract, retaining historical test and review records. Every local Markdown file link and heading anchor resolves. No required empty/stub implementation remains; the empty `src/weather_app/__init__.py` is a valid package marker. Environment, cache and build metadata directories are generated/ignored, not deliverables.

**Validation**

- Full suite: `.venv\Scripts\python.exe -m pytest -q --tb=short` - **415 passed, 2 skipped in 43.80 s** on Windows/Python 3.14. The skips are POSIX permission checks; they are not missing functional tests. The new regression tests exposed four failures against the pre-fix implementation and all seven pass after the changes.
- `.venv\Scripts\python.exe -m flake8 src tests scripts app.py` - zero findings.
- `uv lock --check`, `uv pip check`, and `uv build` to a temporary directory - passed. Both source distribution and wheel build. The supported installation remains `uv sync --locked` from a clone; the wheel alone does not contain app.py or external data. A fresh machine/clean-clone acceptance remains P6.2, and other declared Python versions were not retested here.
- Genuine tracked data has no Git content changes (Windows checkout line endings explain byte differences from blobs). The normalized CSV still contains **3,324 records across 82 destinations**, with Barcelona absent. No live API requests or new genuine weather writes were made; replay tests use historical timestamps and temporary/read-only data.
- `variables.env` and `.venv` are ignored; the committed example is blank. The currently configured key was absent from all tracked working files and **215 unique historical blobs**. This checks that key, not every possible unknown secret. The pre-existing `.gitignore` edit was not changed.

**Rubric walkthrough**

| Teacher criterion | Implementation and checked evidence | Remaining acceptance |
| --- | --- | --- |
| OOP (2) | `JSONAPIClient` supplies reusable transport/error/retry behavior; `OpenWeatherClient` specializes provider mapping. Public API, protected helpers and private credential/lock state are intentional. Validated immutable models expose meaningful special methods and computed properties. Client/model/storage tests pass. | Gabriel reviews design; every member must explain it. |
| API robustness (2) | dotenv credentials; pre-request validation; specific authentication/location/network/provider/storage errors; partial batches; successful saves before ranking. P5.2 and integration tests pass. | No fresh live provider or account-quota validation in P5.5; retain earlier genuine evidence. |
| Data and analytics (2) | Genuine timestamped current/forecast records persist, cache reads create no history. Ranking, cross-location metrics and simultaneous-suitability analysis span comparison and derived metrics. Independent genuine-data tallies and 1-5-day tests pass. | Continue genuine accumulation through normal use; do not describe forecast timestamps as observed multi-day weather history. |
| Streamlit (2) | Searcher and independent Dashboard; editable/seasonal settings, All filters, top-five/full-table consistency, separate state, all-83 map, three labeled analytical charts, unavailable states and safe recovery verified by AppTest. | Gabriel confirms the new map heading at desktop/mobile widths; usability is not guaranteed by automated tests alone. |
| Repository and AI record (1) | Installable src layout, locked dependencies, successful builds, linked README and phase records; configured-key audit clean. PROMPTS updated for the actual requester/tool. Existing substantial implementation commits have AI trailers; two trailer-free commits only update review/PR documentation. | Add the Codex trailer when this change is authorized for commit; P6.2 clean clone remains pending. |
| Team evidence (1) | Non-merge history contains contributions under AsierMarmol, alemedinabarreto, Gabriel Polan Barros Stec, christiansawaya-code and Selin Atalar. Reviewed PR evidence is retained. | Git history cannot prove understanding; each member must explain the complete application. |

**Status:** implementation and automated validation complete locally; awaiting Gabriel review and the noted browser check. No grade, final acceptance, fresh-clone success or submission is asserted. Phase 6 must also confirm source redistribution terms, instructor access and the actual submission channel/receipt.


### P5.5 follow-up review - 12 November 2026

Asier requested another complete alignment review and simple improvements before committing. Rechecked the authoritative assignment README and reference summary against the product rules, implementation, tests, sources, all phase documents and AI records. The product stays mainland-Spain/car-only, with separate Searcher preferences and an independent seasonal weather Dashboard. No dependency, framework, database or additional cache was introduced.

- Fixed narrow configuration-validation gaps in `config.py`: noninteger default days/months and malformed provider-override parameters now produce the existing safe validation errors. An unreadable credential file now gives safe guidance, while an existing nonblank environment key bypasses file reads. Twelve parameterized regression cases were added to `test_config.py`; ten failed before the fix. The affected configuration/API-security suite passes all 71 cases.
- Corrected obsolete function names/shared-state wording in Phase 2/4 and the contract's storage-stop behavior. Simplified README status and explained that changing a loaded API key requires restarting Streamlit, not just refreshing the browser. Kept historical evidence and Phase 6 gates.
- A fresh isolated environment exposed a historical replay test that incorrectly used later forecast issues at an earlier clock time. `test_app_integration.py` now selects only records retrieved by its 11:34 UTC reference time, preserving the same known answers and no-request assertion. Production behavior and genuine data were not changed by this test fix.
- Validation in a temporary snapshot of current files, without copying `.venv` or `variables.env`: `uv sync --locked` installed successfully; full suite **427 passed, 2 skipped in 45.44 s**; Flake8 clean. A final small credential-branch simplification was checked with the 71 configuration/security cases and lint. This is an isolated-install rehearsal of uncommitted files, not P6.2 acceptance of a reviewed Git commit.
- Asier confirmed he was using the app during review. His real CSV grew to **6,604 records across all 83 destinations**, latest retrieval **17:35:30 UTC on 12 November 2026**. The 3,280 new forecast rows form 82 fetch groups; all original 3,324 rows are preserved in order. A frozen copy passed model/schema, catalog-membership, unique-key and coherent-group checks. Barcelona now has saved records. Earlier 82-destination statements describe historical snapshots. The agent made no live requests or synthetic writes to genuine data.

The source counts and route/activity limitations remain explicit. Keep accumulating genuine fetches through normal use; forecasts for several future days are not several days of observed history. The instructor's rubric also requires real team understanding and a clean-clone run; those cannot be established by test counts or role assignments.

### Remaining cross-platform and visual checks

**Two skipped tests (Selin on macOS, or a Linux checkout):**

- `test_saving_keeps_the_files_permissions`: saving preserves an existing Unix mode of `0640`.
- `test_first_saved_file_follows_the_umask`: a first save under umask `0022` creates mode `0644`.

Windows does not implement these Unix permission semantics. Its real read/write failure paths are covered separately with simulated errors. WSL is not installed on this PC; no OS installation is needed for the project. Selin's prior macOS P5.4 suite passed these checks, but the revised P5.5 version still needs a targeted cross-platform run. After the reviewed changes are available locally, from the repository on macOS/Linux:

```sh
uv sync --locked
uv run --locked python -m pytest -q tests/test_model_storage_acceptance.py::test_saving_keeps_the_files_permissions tests/test_model_storage_acceptance.py::test_first_saved_file_follows_the_umask
```

Expected: **2 passed**, not skipped. Record the tested commit and OS. On WSL, use a checkout in the Linux home filesystem so the test measures Linux permissions.

**Browser appearance (Asier or Gabriel):** browser automation was retried and the browser access host remains unavailable. Automated UI behavior is covered; rendered layout still needs human confirmation. Start one app using `uv run --locked streamlit run app.py`, then:

1. Open Dashboard before a Searcher run. Confirm all 83 markers, a readable heading and separate map toolbar, with no exception.
2. Inspect both a normal desktop window and a narrow phone-sized viewport (about 390 pixels). Confirm the heading wraps above the map without covering the toolbar; charts, legends, filters and controls remain usable.
3. Load the overview for 3 days. Hover an available marker: city, activities, average daytime temperature with units, weather rank and score must be readable. Wheel-scrolling the page should not change the map zoom.
4. Apply Coast and a size filter. All markers remain; nonmatching ones dim and global ranks stay unchanged. Inspect ranking, comparison and all-three-criteria tabs and their tables.
5. Switch to Searcher, adjust preferences, search and return. Searcher choices and Dashboard's independent window/results must persist. Check 1-day and 5-day choices, explicit loading, and incomplete coverage messages if returned; do not invent a result to force a pass.
6. Record browser, viewport sizes, tested commit, pass/fail and any screenshots without credentials. Normal live loads append genuine data; visual checks should not run concurrently with data-integrity tests in the same clone.

**Acceptance remains pending** until Gabriel reviews P5.5 and the visual result is recorded. Phase 6 still owns the named clean-clone verification, final source/license check, reviewed main publication, instructor access and submission receipt. No commit, push, review request or merge was performed in this follow-up.


### P5.5 review and merge update - 12 November 2026

Gabriel approved commit `9c0bacc` and PR #19 was merged into dev as `2999dae`. His review says "Approved!"; it does not report Mac tests or desktop/mobile visual results. Asier confirmed those results have not yet been confirmed. Earlier dated pending-review statements above describe their original state and are superseded by this update.

Local `asier/feature` was fast-forwarded to the merged dev version. Gabriel should test from his own feature branch updated from dev, record the exact tested commit and report both the Mac suite (including the two Unix permission checks) and desktop/mobile walkthrough. Do not mark these checks passed from approval alone. P6.1 documentation preparation can proceed; final validation and delivery remain pending.


### Additional visual evidence - 12 November 2026

Asier supplied a desktop Searcher screenshot and a four-page browser print of Dashboard. The screenshot shows the form, All defaults and 83 matching destinations. The print reports 83/83 ranked destinations and shows the map, activity filter, weather ranking and table. Printed chart/table clipping and pagination do not establish a live-browser defect. These artifacts do not report a tested commit, Mac test output, hover behavior or phone-width interaction, so those remaining checks stay open. The subsequent P6.1 sidebar attribution also needs visual confirmation.


### P5.5 storage-recovery follow-up - 13 November 2026

**Reported:** Dashboard listed destinations without ranks with a generic local storage error. The current genuine file read successfully (8,004 records, all 83 destinations); the user has write permission and one listening Streamlit server was found. The original failing operation/OS code was not retained in the old UI, so its precise cause is unconfirmed. A controlled temporary-file probe reproduced Windows error 5 when an open file handle prevented atomic replacement; this is a supported possible cause, not proof of the historical incident.

**Confirmed defects and changes:** Searcher discarded useful storage diagnostics and Dashboard repeated the generic message for unrequested cities. A refresh also fetched a city again before flushing its retained unsaved batch. Storage errors now supply fixed safe guidance for access/locks, disk space, invalid CSV and other I/O failures, with an OS code when available. Both views retain the first storage explanation, skipped count and current pending-record count across reruns. Refresh retries pending saves before cache/HTTP, allowing the saved fresh response to be reused. Atomic replacement and reads retry only Windows access/lock errors 5/32/33 up to three attempts (0.1/0.2-second waits); permanent failures still stop the batch. No unsafe in-place writes, fabricated values or silent CSV repair were added.

**Data and scope:** The live weather CSV was neither modified nor restored by this fix. Tests use temporary records and a frozen copy of genuine data; no real weather calls were made. This is follow-up work on P5.5/P5.1/P5.2 and the shared UI, implemented by Asier with OpenAI Codex. Original component ownership remains unchanged. P6.2 must use the reviewed version containing this change, not only the earlier P6.1 commit.

**Validation:** Final isolated Windows suite: 438 passed, 2 POSIX-only tests skipped in 94.63 seconds; Flake8 clean; all 75 local Markdown links resolve and diff whitespace checks pass. Seven initial targeted cases failed against the previous behavior. The implemented fix passed ten targeted cases, including an actual Windows handle-release test. The first full isolated run passed 436 tests, skipped two POSIX tests and found one old integration assertion expecting a redundant fetch; that assertion was corrected to require exactly one response per city. Searcher and Dashboard recovery are both covered; the final run passed. The live CSV SHA256 stayed `616fa3b3f932aff53b0ef47f972eccdf64c1aa9111ca26b1c5bb96fd5da73e48` throughout the fix.

**Review:** Gabriel reviews the follow-up. Mac permission tests and live desktop/mobile recovery confirmation remain unconfirmed. On 13 November, Asier authorized a final test rerun, commit and push, and a PR into dev requesting Gabriel review. Approval and merging remain pending.


**Publication validation:** Final pre-publication rerun on 13 November 2026: 438 passed, 2 POSIX-only tests skipped in 88.18 seconds; Flake8 clean; isolated locked install, dependency check and source/wheel builds passed. All 75 local Markdown links resolve. The frozen data contains 8,004 records across all 83 destinations; all 6,644 rows in the previous commit remain intact, with 1,360 additional genuine forecast records. No live API requests were made.
