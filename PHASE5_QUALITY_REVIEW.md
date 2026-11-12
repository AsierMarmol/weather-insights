# Phase 5 - Quality Review

Updated: 11 November 2026. **Not started.**

## Purpose and dependencies

Verify the integrated app against the teacher rubric. Component tests already belong to implementation; rerun affected checks and fix actual gaps rather than repeating development as new tasks.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Model/storage acceptance | Alejandra | Christian | Phase 4 | Validate catalog loading, OOP behavior, persistence/reload, write failures and genuine data continuity. | Pending |
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
| Not started | Phase 5 | No completed implementation/acceptance results | Pending |

## Next action

After Gabriel accepts P4.3, run each owner’s acceptance checks and then the connected walkthrough, recording failures and fixes with actual evidence. P4.3 provides 11 integration journeys and a 312-test passing baseline; reuse that evidence and investigate actual remaining rubric gaps rather than rebuilding components. Phase 5 is not yet completed.
