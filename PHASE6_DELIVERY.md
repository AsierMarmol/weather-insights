# Phase 6 - Documentation and Delivery

Updated 14 November 2026. The original P6.1 preparation/publication history is
retained below. P4.5/P6.1 was approved by Gabriel and merged in PR #21.
The independent reviewed-version clean-clone gate remains P6.2.

| Step | Deliverable | Owner | Reviewer | Dependency and current status |
| --- | --- | --- | --- | --- |
| P6.1 | Current README, delivery contents, real data/source/AI evidence | Asier | Gabriel | Approved by Gabriel; merged in PR #21 (dev `3444728`) |
| P6.2 | Independent clean-clone verification by both testers | Gabriel and Alejandra | Christian | At the end of preparation, after final documentation/fixes merge; before P6.3 |
| P6.3 | Reviewed publication and submission | Asier | Gabriel | After P6.2, source/access/channel confirmations and authorization; pending |

## Next action

**Gabriel and Alejandra each perform P6.2, reviewed by Christian.** Gabriel approved [PR #21](https://github.com/AsierMarmol/weather-insights/pull/21)
and it merged into dev as `3444728`. Clone reviewed dev into a new directory,
record the exact commit and follow README only. [Post-commit validation](PHASE5_QUALITY_REVIEW.md#post-commit-validation--14-november-2026)
passed against identical files but does not close this independent gate.
Local Streamlit is the delivery target; hosting is optional. The full
repository is needed: a wheel alone lacks app.py and external data/assets.

## Delivery contents and final checklist

Deliver the repository URL, not a separately maintained copy of the application. Use this checklist on the exact commit selected for final delivery; do not mark a requirement complete from an older run.

| Include in the reviewed repository | Purpose |
| --- | --- |
| `app.py`, `src/weather_app/`, `.streamlit/config.toml`, `assets/` | Landing, Searcher, Dashboard, installable library, theme, local imagery and attribution |
| `pyproject.toml`, `uv.lock`, `.python-version` | Reproducible editable installation; tested Python selection |
| `data/reference/destinations.csv`, `product_defaults.json`, `weather_location_overrides.json` | All 83 destinations, seasonal preferences and provider-specific location mapping |
| `data/weather/weather_records.csv` and retained verification JSONL files | Genuine accumulated current/forecast data with retrieval and valid timestamps |
| Both data READMEs, root README, `SCORING.md` and `WEATHER_API_CONTRACT.md` | Provenance, limitations, setup/run instructions and provider contract |
| `tests/`, `scripts/verify_weather_access.py` | Offline verification and optional explicitly live diagnostic |
| `PROMPTS.md`, phase plans, `PROJECT_PHASES.md`, `TEAMROLES.MD` | Actual AI work, reviews, ownership and remaining tasks |
| `.gitignore`, blank `variables.env.example` | Safe local configuration template |

Do not include real credential files, copied virtual environments, caches, temporary reports or private team-sharing material. Keep the genuine data; its timestamps are not a promise of fresh weather at grading time. Test synthetic inputs remain in tests and temporary stores.

### P6.1 review gates - Asier, reviewed by Gabriel

- [x] Requester confirmed final local preview review on 14 November 2026; this is not teammate approval or a Mac/phone test.
- [x] Prepare Windows and macOS install/key/run guidance and explain the two analytical views, Landing page and three analyses.
- [x] Identify required repository content and link existing schema, rubric and provenance records.
- [x] Add visible OpenWeather text/link/logo and reference source credits without changing calculations.
- [x] Requester confirmed the Free Current Weather + 5-day/3-hour Forecast plan; public ODbL/attribution conditions checked and weather-data notice added.
- [x] Clarify AI-assisted destination selection separately from numeric/weather sources; remove the unsupported INE selection-data confirmation gate.
- [x] Gabriel approved PR #21 for commit `8b1210e`; merged into dev as `3444728`. His approval does not report a separate test run; automated evidence is recorded in Phase 5.
- [x] Record current Windows/VS Code validation in Phase 5. Phone/Mac checks are outside this audit at the user's request; no cross-platform result is inferred.

### P6.2 clean-clone acceptance - Gabriel and Alejandra, reviewed by Christian

P6.1 is reviewed and merged in PR #21. Run P6.2 at the end of preparation,
after the final documentation cleanup and any fixes are reviewed and merged,
before P6.3 publication/submission. Gabriel and Alejandra each test the same
reviewed dev commit independently, using separate fresh directories, their
own environments and personal API keys. Both reports are required; this
assignment does not mark either run complete. Use only README instructions. Record `git rev-parse HEAD`, operating system, Python/uv versions and actual results. Do not copy another clone's environment or credentials.

1. Clone reviewed dev and run `uv sync --locked`, package import, `uv pip check`, the full offline test suite and Flake8 as documented in README. Keep the app stopped during tests. On macOS the two Unix permission tests should run, not be dismissed as Windows skips.
2. Configure a personal key locally and start Streamlit. Check Landing and Dashboard before Searcher, automatic Dashboard loading, the all-83 map, hover, executive tables, Destination-score-versus-driving scatter and daily heatmap; verify 1/5-day selection, navigation and independent state. Check the agreed delivery viewport; this local audit excludes phone/Mac acceptance. Live loads create real saved records and count against the account quota.
3. Exercise Searcher preferences, All selections, top-five/full-table consistency and unavailable states. Verify successful fresh fetches save genuine records and suitable cache reuse does not append duplicates. Use existing tests for simulated error paths; do not deliberately overload the provider.
4. Each tester records their identity, exact commit, environment, commands/results, visual checks, limitations and any fixes/retests in this phase. Christian reviews both reports. If a fix changes the candidate, both reports must cover the final reviewed version before P6.2 is closed. Preserve new real records and inspect the diff before proposing them for commit.

### P6.3 final publication - Asier, reviewed by Gabriel

- [ ] All earlier review/check evidence applies to the selected delivery commit; each member can explain the complete app.
- [ ] Review final accumulated data and secret exclusions; include genuine history in the reviewed change.
- [ ] Confirm source reuse conditions, instructor access and the actual submission channel and due date with the instructor.
- [ ] Obtain authorization, open the reviewed dev-to-main PR, retain actual authorship/AI trailers and satisfy branch rules. Do not invent contributors or approvals.
- [ ] Confirm final main contains the verified delivery files. If code/data changes invalidate acceptance, repeat affected checks before submission.
- [ ] Submit the repository URL through the confirmed channel and record the actual receipt. No submission or final grade is claimed here.


## P6.1 preparation — 14 November 2026

Prepared for the P4.5 delivery update; uncommitted. The requester confirmed
the final preview review and asked to finish documentation before committing.
README, phase navigation and adoption status now distinguish that review from
Gabriel's pending review and the future reviewed-commit P6.2 check. Two stale
508-test summaries were corrected to the then-current 505 passed / 2 skipped result.
The subsequent provider-identity follow-up reached 523 passed / 2 skipped;
[Phase 5](PHASE5_QUALITY_REVIEW.md#provider-identity-and-diagnostic-follow-up--14-november-2026)
owns the latest evidence. The [development log](PROMPTS.md#phase-4-extension-and-delivery-development-record)
now records the Canva adaptation and its implementation sequence for review.

The immediately preceding frozen-copy run passed 505 tests in 75.93 seconds;
the two skips are POSIX-only checks on Windows. Lint, locked installation,
dependency checks, source/wheel builds and credential-free Streamlit HTTP
startup passed. Additional independent checks covered 1,000 varied scoring
cases and 83,000 tie-rank comparisons. Three deliberately incorrect scoring
variants failed the unchanged tests. That P6.1 documentation step did not change code/tests; these
results describe its preparation checkpoint, before the provider follow-up. That full suite used the earlier 19,167-row
snapshot. The newer 22,487-row snapshot passed five additional genuine-data
Dashboard consistency tests (all 1–5-day windows) and full record-integrity
validation. Neither check is a new live API/browser run.

Delivery inventory includes source, tests, setup/lock files, theme/assets,
references, diagnostic, documentation and genuine data. Preserve all 19,167
records in the earlier audited snapshot and the 3,320 subsequent genuine
forecast rows: 22,487 records total (83 cities, 647 fetch groups). Later genuine
appends must be validated before publication. Credentials/generated artifacts
remain excluded. No code license or data permission is invented by this step.

### Source confirmations

- [OpenWeather attribution guidance](https://openweathermap.org/faq#license)
  was rechecked on 14 November: applicable plans require visible provider
  text, link and logo. These are already included. The requester confirmed
  the Free Current Weather + 5-day/3-hour Forecast plan. Its [published plan
  terms](https://openweathermap.org/full-price) identify ODbL; the retained
  weather dataset now carries that notice in its [README](data/weather/README.md#weather-dataset-license--14-november-2026).
  No paid upgrade is needed for the endpoints used by this project.
- [GeoNames terms](https://www.geonames.org/export/) identify CC BY and require
  credit; [OSM copyright](https://www.openstreetmap.org/copyright) identifies
  ODbL and attribution/share-alike conditions. Existing reference credits
  remain. Their source conditions are not replaced by a blanket project license.
- The requester clarified that AI helped select destinations matching the
  agreed activity/travel criteria. An INE tourism-data import was not established;
  the unreadable INE notice is not an acceptance gate. The [catalogue notes](data/reference/README.md#sources-and-limits)
  distinguish this curated selection from coordinate, route and weather sources.

P6.1 documentation is prepared; Gabriel's review remains open for acceptance.
P6.2 begins on the agreed reviewed commit; P6.3 remains final publication and
submission. No staging, commit, push, review request or merge was performed.

## Historical preparation evidence

## P6.1 local preparation - 12 November 2026

Asier requested the next phase step; OpenAI Codex prepared the documentation and provider attribution. Existing local status edits and newly accumulated weather records were preserved. No live API request was made, and the weather dataset was not edited by this work. Verification: isolated `uv sync --locked` succeeded; 18 existing app-integration/final-acceptance tests passed in 19.91 seconds; Flake8 reported no findings. All 75 local Markdown links/anchors resolve and `git diff --check` passes. The official logo was visually inspected and copied without modification. A frozen CSV snapshot passed WeatherStore model/schema validation, catalog membership, unique keys and preservation of all 6,604 previously committed rows: 6,644 records across 83 destinations (4 current and 6,640 forecast), including 40 newly accumulated forecast rows. These counts are a dated snapshot. This targeted Windows run is not a full-suite rerun, a Mac test result or P6.2 clean-clone approval; no live desktop/mobile visual result is claimed. After preparation, Asier authorized a commit and push to `asier/feature` on 12 November 2026. Gabriel review, merging and submission remain pending.



## P4.5 additions to clean-clone acceptance

- Verify Landing / Trip Searcher / Dashboard, independent state and all five
  windows; fetching uses full forecasts, reuse creates no duplicate history.
- Check one Trip score in Searcher and one Destination score throughout the
  Dashboard, including driving. Daily cells use daily windows and label their mean.
- Check equal-city rain/wind averages, explicit catalogue maxima, all-83 map
  and missing-data states; no illustrative Canva values or forced coverage.
- Check responsive KPI cards, navigation, h:mm sorting, table scrolling,
  chart hover/zoom/reset, OSM attribution/tiles and fallback fonts. A VS Code
  preview pass is not a real-phone or Mac pass.
- Run bounded offline stress tests and fault injection rather than overloading
  OpenWeather or damaging the real CSV. One writer process per clone remains
  the supported deployment; pending unsaved data must be recovered before closing.
- Record actual commit, OS/Python/uv, commands/results and reviewer acceptance.
  Recheck code/data changes after the tested version. Never infer contribution,
  peer approval, source rights or a grade from test counts.

## Instructor reproduction requirement

The final reviewed repository must be self-contained for an instructor as well
as a teammate: locked install, source/theme/assets, reference files, real logged
data and README commands. The reader supplies their own active API key after
installing Git/uv; no personal environment or developer-home path is required.
Keep the optional diagnostic and all setup files. Generated egg-info and caches
are recreated locally. See [latest clean-copy evidence](PHASE5_QUALITY_REVIEW.md#provider-identity-and-diagnostic-follow-up--14-november-2026). This local
evidence does not publish the preview or close P6.2 for a future reviewed commit.


## P6.1 integration checkpoint — 14 November 2026

The complete P4.5 candidate is present in the main project on asier/feature.
The requester will review and commit; nothing is staged or published by this
integration. [Latest checks](PHASE5_QUALITY_REVIEW.md#feature-integration-validation--14-november-2026)
passed in the destination environment on the combined 22,767-row genuine data.
Historical source-confirmation and earlier test snapshots above remain intact.
Next: requester review/commit, authorized push and PR review into dev; then
P6.2 on the actual reviewed commit, followed by P6.3. Copying files into the
feature working tree does not complete any of those publication/review gates.


## P6.1 review and merge — 14 November 2026

Gabrielstec approved [PR #21](https://github.com/AsierMarmol/weather-insights/pull/21), which merged commit `8b1210e` into dev as
`3444728`. This supersedes the pending-publication status in the dated
preparation/integration checkpoints above. [Post-commit verification](PHASE5_QUALITY_REVIEW.md#post-commit-validation--14-november-2026)
passed on identical files. P6.2 remains open for Gabriel and Alejandra,
reviewed by Christian;
P6.3 remains open for Asier, reviewed by Gabriel. Approval alone is not a
Mac/browser test report or final submission.
