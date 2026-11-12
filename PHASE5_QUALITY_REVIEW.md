# Phase 5 - Quality Review

Updated: 12 November 2026. **In progress:** P5.1 model/storage acceptance approved by Christian and merged in [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); P5.2 API/security/save acceptance merged in PR #14 with Selin's approval (Alejandra was the planned reviewer); P5.3-P5.5 pending. P5.4 now follows P4.4.

## Purpose and dependencies

Verify the integrated app against the teacher rubric. Component tests already belong to implementation; rerun affected checks and fix actual gaps rather than repeating development as new tasks.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Model/storage acceptance | Alejandra | Christian | P4.1-P4.3 merged | Validate catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity. | Completed locally: three gaps fixed, 21 new tests, 333 total pass, Flake8 clean; commit ac30f13, [PR #13](https://github.com/AsierMarmol/weather-insights/pull/13); approved by Christian and merged |
| P5.2 | API/security/save acceptance | Gabriel | Alejandra | P4.1-P4.3 merged | Exercise input/key/location/network/server/quota/malformed responses, partial batches, cache saves and safe failure messages. | Completed locally: one gap fixed (key file in another encoding), 43 new tests, 376 total pass, Flake8 clean; merged in PR #14 with Selin's approval (Alejandra was the planned reviewer) |
| P5.3 | Analytical acceptance | Christian | Selin | P4.1-P4.3 merged | Verify all day windows, clock changes, threshold boundaries, missing/stale metrics, driving cap, ties and three distinct analyses. | Pending |
| P5.4 | Dashboard/chart acceptance | Selin | Asier | P4.4 merged | Validate the independent Dashboard: all 83 map markers, hover values, plotted inputs and units, weather-only ranks/ties, interactive filters, windows, freshness and empty/unavailable states against common results. | Pending; P4.4 approved and merged in PR #15 |
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

## Next action

P5.1 and P5.2 are merged. P4.4 is approved and merged in PR #15; Christian (P5.3) and Selin (P5.4) run their acceptance checks, then Asier runs the connected walkthrough (P5.5), recording failures and fixes with actual evidence. P4.3 provides 11 integration journeys and a 312-test passing baseline; reuse that evidence and investigate actual remaining rubric gaps rather than rebuilding components. Phase 5 is not yet completed.

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

