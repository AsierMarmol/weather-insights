# Phase 6 - Documentation and Delivery

Updated: 13 November 2026. **P6.1 pushed; review and storage-recovery follow-up pending:** P5.5 was approved by Gabriel and merged in PR #19 (dev `2999dae`). Mac tests and desktop/mobile visual results remain unconfirmed; these remain open acceptance checks. Packaging checks and the successful P5.5 isolated-install rehearsal do not substitute for P6.2 clean-clone acceptance of a reviewed commit. Include the [remaining cross-platform and visual checks](PHASE5_QUALITY_REVIEW.md#remaining-cross-platform-and-visual-checks) in the review evidence.

## Purpose and dependencies

Package the verified local Streamlit application and genuine dataset, validate a clean clone, then submit the reviewed version.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P6.1 | Delivery package and README | Asier | Gabriel | Phase 5 | Current setup/run guide, code/catalog/defaults/provider overrides, genuine saved weather data, source credits and actual AI/contribution records. | Prepared and pushed; Gabriel review and source/account confirmations pending |
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
| 12 November 2026 | P6.1 | README includes Windows/macOS setup, three analytical views and rubric links; delivery checklist and source credits prepared; official weather attribution added to both views. Verification results below. | Awaiting Gabriel review; P6.2/P6.3 not performed |

## Next action

Complete and review the P5.5 storage-recovery follow-up before P6.2. Gabriel reviews P6.1 and the follow-up while recording the remaining Mac and desktop/mobile checks on the merged P5.5 version. Final acceptance still requires those results. After P6.1, Selin verifies a clean clone in P6.2 (Christian reviews), then Asier completes P6.3 (Gabriel reviews). Retain the repository-based install instructions: standalone wheel installation does not include the app entry point or external reference/weather data. Confirm source redistribution terms, each member's understanding, instructor access and submission channel before delivery.

## P4.4 delivery dependency

P6.1 must document the independent Spain Dashboard and the difference between its weather rank and Searcher's trip score. P6.2 must test both views from a clean clone, including the all-83 map before a Searcher run, without copying another user's credentials. P6.3 remains blocked until P4.4 and the affected P5.4/P5.5 checks are accepted; no delivery work is marked complete by this planning update.


## Delivery contents and final checklist

Deliver the repository URL, not a separately maintained copy of the application. Use this checklist on the exact commit selected for final delivery; do not mark a requirement complete from an older run.

| Include in the reviewed repository | Purpose |
| --- | --- |
| `app.py`, `src/weather_app/`, `assets/openweather-logo.jpg` | Two-view application, installable library and provider credit |
| `pyproject.toml`, `uv.lock`, `.python-version` | Reproducible editable installation; tested Python selection |
| `data/reference/destinations.csv`, `product_defaults.json`, `weather_location_overrides.json` | All 83 destinations, seasonal preferences and provider-specific location mapping |
| `data/weather/weather_records.csv` and retained verification JSONL files | Genuine accumulated current/forecast data with retrieval and valid timestamps |
| Both data READMEs, root README and `WEATHER_API_CONTRACT.md` | Provenance, limitations, setup/run instructions and provider contract |
| `tests/`, `scripts/verify_weather_access.py` | Offline verification and optional explicitly live diagnostic |
| `PROMPTS.md`, phase plans, `PROJECT_PHASES.md`, `TEAMROLES.MD` | Actual AI work, reviews, ownership and remaining tasks |
| `.gitignore`, blank `variables.env.example` | Safe local configuration template |

Do not include real credential files, copied virtual environments, caches, temporary reports or private team-sharing material. Keep the genuine data; its timestamps are not a promise of fresh weather at grading time. Test synthetic inputs remain in tests and temporary stores.

### P6.1 review gates - Asier, reviewed by Gabriel

- [x] Prepare Windows and macOS install/key/run guidance and explain the two views and three analyses.
- [x] Identify required repository content and link existing schema, rubric and provenance records.
- [x] Add visible OpenWeather text/link/logo and reference source credits without changing calculations.
- [ ] Confirm the account-specific OpenWeather storage/redistribution terms and any remaining source reuse conditions. Public attribution guidance was checked; this does not confirm the team's private account agreement.
- [ ] Gabriel reviews the P6.1 diff and reports the tested commit. Review has not been requested by this local preparation.
- [ ] Close P5.5's Mac tests and live desktop/mobile checks, including the new sidebar credit. The supplied PDF/screenshot support partial desktop rendering only, not Mac test results or mobile interaction.

### P6.2 clean-clone acceptance - Selin, reviewed by Christian

After the prepared P6.1 change is reviewed and merged, use a new directory and only README instructions. Record `git rev-parse HEAD`, operating system, Python/uv versions and actual results. Do not copy another clone's environment or credentials.

1. Clone reviewed dev and run `uv sync --locked`, package import, `uv pip check`, the full offline test suite and Flake8 as documented in README. Keep the app stopped during tests. On macOS the two Unix permission tests should run, not be dismissed as Windows skips.
2. Configure a personal key locally and start Streamlit. Check Dashboard before Searcher, the all-83 map, hover, highlighting and all three charts; verify 1/5-day selection, navigation and independent state. Check desktop and phone-width layout. Live loads create real saved records and count against the account quota.
3. Exercise Searcher preferences, All selections, top-five/full-table consistency and unavailable states. Verify successful fresh fetches save genuine records and suitable cache reuse does not append duplicates. Use existing tests for simulated error paths; do not deliberately overload the provider.
4. Record limitations and any fixes with their retest results in this phase. Christian reviews this evidence. Preserve new real records and inspect the diff before proposing them for commit.

### P6.3 final publication - Asier, reviewed by Gabriel

- [ ] All earlier review/check evidence applies to the selected delivery commit; each member can explain the complete app.
- [ ] Review final accumulated data and secret exclusions; include genuine history in the reviewed change.
- [ ] Confirm source reuse conditions, instructor access and the actual submission channel and due date with the instructor.
- [ ] Obtain authorization, open the reviewed dev-to-main PR, retain actual authorship/AI trailers and satisfy branch rules. Do not invent contributors or approvals.
- [ ] Confirm final main contains the verified delivery files. If code/data changes invalidate acceptance, repeat affected checks before submission.
- [ ] Submit the repository URL through the confirmed channel and record the actual receipt. No submission or final grade is claimed here.

## P6.1 local preparation - 12 November 2026

Asier requested the next phase step; OpenAI Codex prepared the documentation and provider attribution. Existing local status edits and newly accumulated weather records were preserved. No live API request was made, and the weather dataset was not edited by this work. Verification: isolated `uv sync --locked` succeeded; 18 existing app-integration/final-acceptance tests passed in 19.91 seconds; Flake8 reported no findings. All 75 local Markdown links/anchors resolve and `git diff --check` passes. The official logo was visually inspected and copied without modification. A frozen CSV snapshot passed WeatherStore model/schema validation, catalog membership, unique keys and preservation of all 6,604 previously committed rows: 6,644 records across 83 destinations (4 current and 6,640 forecast), including 40 newly accumulated forecast rows. These counts are a dated snapshot. This targeted Windows run is not a full-suite rerun, a Mac test result or P6.2 clean-clone approval; no live desktop/mobile visual result is claimed. After preparation, Asier authorized a commit and push to `asier/feature` on 12 November 2026. Gabriel review, merging and submission remain pending.


### Delivery dependency update - 13 November 2026

A user-reported storage failure reopened P5.5 follow-up work. The recovery change must be reviewed and included in the version Selin tests in P6.2; an earlier P6.1 commit alone does not include it. P6.2/P6.3 remain pending. See the latest Phase 5 entry for diagnosis, tests and remaining live verification.
