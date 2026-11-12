# Phase 3 - Core Application and Automatic Data Saving

Updated: 12 November 2026. **In progress:** P3.1 implemented locally; P3.2/P3.3 pending.

## Purpose and dependencies

Build models/storage, the reusable API/save service and the analytical engine. Reviewed P2.1-P2.4 are the start gate. Asier verifies P2.5 using P3.1/P3.2 after they are connected; require that check for Phase 3 acceptance, not before constructing the components.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P3.1 | Models, catalog loading and persistence | Alejandra | Christian | P2.4 | Validated models with useful special method/computed property; safe CSV append/reload, preserved genuine records and meaningful tests. | In progress: implemented and tested locally; awaiting PR and Christian's review; P2.4 review by Christian still outstanding |
| P3.2 | Production API and request/save service | Gabriel | Alejandra | P2.4; integration after P3.1 | Generic/provider inheritance and deliberate encapsulation; safe credentials, normalization, partial failures, pacing/cache, single automatic save path and tests. | Pending |
| P3.3 | Analytics and ranking engine | Christian | Selin | P2.4; real-data integration after P3.1 + P3.2 | Complete coverage/time/filter/scoring/tie rules, three analyses and independently checked tests on synthetic and genuine inputs. | Pending |

## Implementation and acceptance

Use the shared objects, methods, CSV header and worked example in P2.4. Alejandra owns models.py/storage.py; Gabriel client.py/config.py/service.py; Christian analytics.py. Keep analytics pure and credential-free. Extend the existing lazy get_api_key helper rather than duplicating configuration. Retain valid dated records; new successes save automatically, cache reads do not. A failed save is not analytical success. No scheduler or second verification client/store.

Read [Phase 2](PHASE2_SCOPE.md) for product rules, shared schema and the worked example; [API contract](WEATHER_API_CONTRACT.md) for provider behavior; [roles](TEAMROLES.MD) for ownership. Each owner includes tests/docs/fixes. Follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance) when decisions change. The instructor README governs final acceptance; plans are not proof of completed functionality.

## Task prompt

```text
Work on <task ID> in PHASE3_CORE_DATA.md as <actual requester>.
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
| 12 November 2026 | P3.1 | Alejandra/Claude Code implemented `models.py` (validated frozen `Destination`, `SearchPreferences`, `WeatherRecord`; `drive_hours`, `horizon`, `lead_time`, `key` properties; `__str__`/`__repr__`, chronological `__lt__`; exact CSV round-trip) and `storage.py` (`load_destinations`, `WeatherStore.append/load/latest_forecast`, `CatalogError`, `StorageError`). Saves copy the existing file byte-for-byte to a temporary file, append, fsync and atomically replace; retries are idempotent on (fetch_id, city_id, kind, valid_at_utc); conflicting values raise `ValueError`; damaged files raise `StorageError` and are never appended to; writes are serialized per file within the process. `tests/test_models.py` and `tests/test_storage.py` add 82 offline tests using temporary files only; the full suite passes (107). The real catalog loads 83 rows (14/26/43 sizes, Lugo values unchanged). No `weather_records.csv` was created and no live request was made. | In progress; awaiting PR and Christian's review |
| 12 November 2026 | P3.1 limits | Importing the retained JSONL evidence is not done: it needs the provider-to-record mapping from P3.2 and must keep original retrieval times. Two records with the same key but different values in one batch are rejected rather than stored, so a provider duplicate surfaces as an invalid-data save error. Single writing process per clone, as specified. | Open; revisit with Gabriel at P3.2 integration |

## Next action

Christian reviews P3.1 (and the outstanding P2.4/catalog review). Gabriel builds P3.2 on `WeatherStore` and maps `StorageError` to the `storage` code and conflict `ValueError` to `invalid_data`. Implement the remaining components after review; connect API to storage, have Asier run P2.5, then verify analytical results on the saved data.
