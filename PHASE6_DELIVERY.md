# Phase 6 - Documentation and Delivery

Updated: 12 November 2026. **Not started:** P5.5 is implemented/tested locally but awaits Gabriel review. Packaging checks and the successful P5.5 isolated-install rehearsal do not substitute for P6.2 clean-clone acceptance of a reviewed commit. Include the [remaining cross-platform and visual checks](PHASE5_QUALITY_REVIEW.md#remaining-cross-platform-and-visual-checks) in the review evidence.

## Purpose and dependencies

Package the verified local Streamlit application and genuine dataset, validate a clean clone, then submit the reviewed version.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P6.1 | Delivery package and README | Asier | Gabriel | Phase 5 | Current setup/run guide, code/catalog/defaults/provider overrides, genuine saved weather data, source credits and actual AI/contribution records. | Pending |
| P6.2 | Clean-clone verification | Selin | Christian | P6.1 | Named version installs, imports, tests and runs using README only; no copied environment or credentials; real results recorded. | Pending |
| P6.3 | Reviewed publication and submission | Asier | Gabriel | P6.2 | Authorized protected-branch PR workflow, instructor access, confirmed submission channel/deadline and actual receipt. | Pending |

## Implementation and acceptance

Include the accumulated real application CSV; never fabricate history or ship an empty substitute. Keep current observations and forecasts distinguishable. Retain data-source attribution and check applicable redistribution terms. All requirements must be available from the repository and README. Keep real credentials and generated environments excluded. Recheck affected behavior if the submitted version differs from the tested one. Hosting is optional; local Streamlit remains the target.

Read [Phase 2](PHASE2_SCOPE.md) for product rules, shared schema and the worked example; [API contract](WEATHER_API_CONTRACT.md) for provider behavior; [roles](TEAMROLES.MD) for ownership. Each owner includes tests/docs/fixes. Follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance) when decisions change. The instructor README governs final acceptance; plans are not proof of completed functionality.

## Task prompt

```text
Work on <task ID> in PHASE6_DELIVERY.md as <actual requester>.
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
| Not started | Phase 6 | No completed implementation/acceptance results | Pending |

## Next action

After Gabriel accepts P5.5, Asier completes P6.1 (Gabriel reviews), Selin verifies a clean clone in P6.2 (Christian reviews), then Asier completes P6.3 (Gabriel reviews). Retain the repository-based install instructions: standalone wheel installation does not include the app entry point or external reference/weather data. Confirm source redistribution terms, each member's understanding, instructor access and submission channel before delivery.

## P4.4 delivery dependency

P6.1 must document the independent Spain Dashboard and the difference between its weather rank and Searcher's trip score. P6.2 must test both views from a clean clone, including the all-83 map before a Searcher run, without copying another user's credentials. P6.3 remains blocked until P4.4 and the affected P5.4/P5.5 checks are accepted; no delivery work is marked complete by this planning update.
