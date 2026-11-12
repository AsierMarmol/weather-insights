# Phase 5 - Quality Review

Updated: 12 November 2026. **In progress:** P5.1 model/storage acceptance completed locally, awaiting Christian's review; P5.2-P5.5 pending.

## Purpose and dependencies

Verify the integrated app against the teacher rubric. Component tests already belong to implementation; rerun affected checks and fix actual gaps rather than repeating development as new tasks.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Model/storage acceptance | Alejandra | Christian | Phase 4 | Validate catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity. | Completed locally: three gaps fixed, 21 new tests, 333 total pass, Flake8 clean; awaiting Christian's review |
| P5.2 | API/security/save acceptance | Gabriel | Alejandra | Phase 4 | Exercise input/key/location/network/server/quota/malformed responses, partial batches, cache saves and safe failure messages. | Pending |
| P5.3 | Analytical acceptance | Christian | Selin | Phase 4 | Verify all day windows, clock changes, threshold boundaries, missing/stale metrics, driving cap, ties and three distinct analyses. | Pending |
| P5.4 | Dashboard/chart acceptance | Selin | Asier | Phase 4 | Validate plotted inputs, units, interactive filters and empty/unavailable states against common results. | Pending |
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

## Next action

Christian reviews P5.1. Gabriel (P5.2), Christian (P5.3) and Selin (P5.4) run their acceptance checks, then Asier runs the connected walkthrough (P5.5), recording failures and fixes with actual evidence. P4.3 provides 11 integration journeys and a 312-test passing baseline; reuse that evidence and investigate actual remaining rubric gaps rather than rebuilding components. Phase 5 is not yet completed.

### P5.1 model/storage acceptance - 12 November 2026

Alejandra / Claude Code, on `Alejandra/feature` from dev `27e088e`. Acceptance reused the P3.1 component tests and added `tests/test_model_storage_acceptance.py` (17 tests) for the criteria they did not cover, plus 4 regression cases in `tests/test_models.py` and `tests/test_storage.py`.

Checked and passing without changes: the real 83-row catalog (also with Windows line endings and a byte-order mark); all 164 genuine weather rows reload with unique keys, catalog city IDs and provider coordinates within about 11 km of the catalog point; every fetch group has one city, kind and retrieval time; the latest genuine forecast for Toledo, Segovia and Seville is one 40-period fetch on a three-hour grid; every genuine row round-trips through the model. On a temporary copy of the genuine file, appending synthetic rows keeps every existing byte as a prefix, reloads through a new store instance, and a retry writes nothing. Failed fsync, failed replace and a failed mid-copy leave the previous file and no temporary files. OOP: frozen validated value objects with equality/hashing, computed properties, `__str__`/`__repr__`/`__lt__`, a private name-mangled lock shared per file and a read-only `path` property.

Three actual gaps were found and fixed in `models.py`/`storage.py`:

1. A catalog that is not valid UTF-8 raised a raw `UnicodeDecodeError` instead of `CatalogError`. It now reports `<file> is not valid UTF-8`.
2. Every save replaced `weather_records.csv` with a temporary file created owner-only (`0o600`), so a teammate's data file silently lost group/other read access (Git does not track this). Saves now keep the previous file's permissions, and a first file follows the user's umask. The temporary file is created exclusively, so a name clash can never remove another file.
3. A CSV row with missing cells was reported as "schema_version and provider_city_id must be integers". It is now reported as a column mismatch with its line number.

The new regression tests failed against the dev `27e088e` sources (permissions, non-UTF-8 catalog and short rows) and pass now. Full suite: **333 passed** (312 before); Flake8 zero findings. Tests read the genuine catalog and weather file only, and an autouse check confirms their bytes and permissions are unchanged; all writes use pytest temporary copies. The CSV schema, record key and public interfaces are unchanged.

Limitations: one writing process per clone remains the supported model (the lock is per process). A weather CSV saved with a byte-order mark (for example by a spreadsheet program) is reported as having an unexpected header and is not modified; it must be restored from Git. Permission checks are skipped on Windows. Importing the retained historical JSONL evidence remains deferred.

**Status:** completed locally, awaiting Christian's review. No commit, push or PR yet.

