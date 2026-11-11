# Phase 3 - Core Application and Automatic Data Saving

Updated: 11 November 2026. **Not started.**

## Purpose and dependencies

Build models/storage, the reusable API/save service and the analytical engine. Reviewed P2.1-P2.4 are the start gate. Asier verifies P2.5 using P3.1/P3.2 after they are connected; require that check for Phase 3 acceptance, not before constructing the components.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P3.1 | Models, catalog loading and persistence | Alejandra | Christian | P2.4 | Validated models with useful special method/computed property; safe CSV append/reload, preserved genuine records and meaningful tests. | Pending |
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
| Not started | Phase 3 | No completed implementation/acceptance results | Pending |

## Next action

Implement the three components after review; connect API to storage, have Asier run P2.5, then verify analytical results on the saved data.
