# Phase 4 - Analytics and Streamlit Interface

Updated: 12 November 2026. **Not started.**

## Purpose and dependencies

Deliver Searcher and Dashboard on the same data and calculations, then connect the user journey. Preparation can use the reviewed result shape; acceptance needs actual Phase 3 components and P2.5 verification.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P4.1 | Complete Searcher | Asier | Gabriel | Phase 3 accepted incl. P2.5 | Editable seasonal preferences, rolling 1-5 days, All filters from catalog values, five leading results/full ranking, useful errors and tests. | Pending |
| P4.2 | Complete Dashboard | Selin | Asier | Phase 3 accepted incl. P2.5 | Interactive ranking, weather comparison and simultaneous-preference metrics; at least two labeled real-data charts, missing states and tests. | Pending |
| P4.3 | Integrate the app | Asier | Gabriel | P4.1 + P4.2 | Shared search state, navigation, data reuse, progress/freshness and partial errors verified end to end. | Pending |

## Implementation and acceptance

Asier owns app.py/searcher.py and shared preferences/state. Selin owns dashboard.py/charts. Both consume the same analytical results without a second scoring or fetching path. Use product_defaults.json only on initial load/reset; preserve user edits. Build size/activity options from real catalog values and show All explicitly. Display units, valid dates and data age. Keep synthetic UI tests separate from real demonstrations. Use native Streamlit controls and headless AppTest for interaction checks.

Read [Phase 2](PHASE2_SCOPE.md) for product rules, shared schema and the worked example; [API contract](WEATHER_API_CONTRACT.md) for provider behavior; [roles](TEAMROLES.MD) for ownership. Each owner includes tests/docs/fixes. Follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance) when decisions change. The instructor README governs final acceptance; plans are not proof of completed functionality.

## Task prompt

```text
Work on <task ID> in PHASE4_ANALYTICS_UI.md as <actual requester>.
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
| Not started | Phase 4 | No completed implementation/acceptance results | Pending |

## Next action

P2.5 verification has passed locally; Gabriel's review and Christian's multi-city analytical acceptance remain pending. After that gate, Asier builds P4.1 and Selin builds P4.2 using the shared services; Asier then connects the two in P4.3 and verifies the user journey. No view implementation is claimed complete.
