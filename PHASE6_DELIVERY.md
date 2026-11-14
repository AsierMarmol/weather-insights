# Phase 6 - Documentation and Delivery

Updated 14 November 2026. The original P6.1 preparation/publication history is
retained below. P4.5/P6.1 was approved by Gabriel and merged in PR #21.
The independent reviewed-version clean-clone gate remains P6.2.

| Step | Deliverable | Owner | Reviewer | Dependency and current status |
| --- | --- | --- | --- | --- |
| P6.1 | Current README, delivery contents, real data/source/AI evidence | Asier | Gabriel | Approved by Gabriel; merged in PR #21 (dev `3444728`) |
| P6.2 | Independent clean-clone verification by both testers | Gabriel and Alejandra | Christian | Gabriel's report recorded below (dev `d1c3bdf`, macOS); Alejandra's report and Christian's review pending; before P6.3 |
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

### P6.2 report - Gabriel, 14 November 2026

**Tester:** Gabriel Polan Barros Stec (Gabrielstec). **AI collaborator:**
Claude Code (Anthropic Claude Opus 5.5), which ran the commands and drove the
in-app browser at Gabriel's request. This is one of the two required reports;
it does not close P6.2 or record Christian's review.

**Commits and environment.** Fresh `git clone --branch dev` from GitHub into
new directories; no environment, key or local configuration was copied. Live
checks ran on `34447285c0fda927f2bb4ee77da8651ec12879a2` (PR #21). Dev then
advanced to `d1c3bdfb5cd30a68fb66af4051b7b764d512f8f9` (PR #22, seven Markdown
files only; `git diff` confirmed `src`, `tests`, `app.py`, `scripts`, `data`,
`assets`, `.streamlit`, `pyproject.toml`, `uv.lock`, `.python-version`,
`.gitignore` and `variables.env.example` identical), so the automated and
no-key checks were repeated on a second fresh clone of `d1c3bdf`. macOS 26.6.2
(arm64), Python 3.14.0, uv 0.12.9. The personal key was entered locally in the
ignored `variables.env`; it was never displayed.

**Automated checks (app stopped), identical on both commits.**

| Command | Result |
| --- | --- |
| `uv sync --locked` | Succeeded |
| `uv pip check` | All installed packages are compatible |
| `uv run --locked python -c "import weather_app; ..."` | Package import OK |
| `uv run --locked python -m pytest -q -ra` | 524 passed, 1 skipped (`test_storage_recovery.py:122`, Windows file sharing); 32-35 s |
| `uv run --locked flake8 src tests scripts app.py` | No findings |

Both POSIX permission tests (`test_saving_keeps_the_files_permissions`,
`test_first_saved_file_follows_the_umask`) ran and passed. The genuine weather
CSV was byte-identical after testing.

**Manual and live checks (`3444728`, 1024x768 in-app browser).**

- Landing loads; navigation works; the season card shows Autumn 16–24 °C,
  matching `product_defaults.json`. Searcher defaults also match (3 days,
  16–24 °C, Low rain, Moderate wind, Activities and Size All).
- Dashboard opened before Searcher and loaded automatically ("83 of 83 ... 83
  saved forecast(s) reused"). Windows 1, 2, 3, 4 and 5 each reused the saved
  forecasts; every window kept all 83 destinations on the map and scatter.
- In every window the map and scatter scores agree for all 83 destinations at
  full precision, and the KPI average, leader, top five, driving bands and
  visible catalogue rows agree with them. Four 4-day scores recomputed by hand
  from the CSV with the SCORING.md formula matched exactly (Elche 86.2997,
  Alicante 85.9091, Toledo 71.8666, Santiago de Compostela 42.4494).
- Heatmap: 83 rows; each day is its own 24-hour window; Daily avg is the mean
  of the day scores and rows are sorted by it; 64 of 83 averages differ from
  the whole-window score, as documented. In the 1-day window every Day 1 value
  equals the overview score.
- Searcher: Coast replaced All (37 matches); Coast plus Small city or town gave
  21; both match the catalogue. Controls showed "Settings changed" and did not
  fetch. Reset restored every default. Low/Medium/High rain and the four wind
  categories are offered; a High rain search ranked dry coastal forecasts lower.
- Cards equal the first five full-ranking rows in Trip score and driving time
  (cards `4:01 h`, table `04:01`, padded for sorting); the full ranking had 83
  rows (75 read, all descending, none blank) and 21 rows for the filtered search.
- The views kept independent settings and snapshots across navigation.
- High-wind notice, Strong wind preferred: "1 of your top recommendations ..."
  was correct; only A Coruña in the top five reached 39+ km/h (48.0), while a
  second windy destination outside the top five was not counted. No notice
  appeared with defaults (top-five maxima 6.7-22.4 km/h).
- After the saved forecasts passed three hours, one 21-destination Searcher
  search fetched fresh data ("0 reused") and saved 840 genuine forecast rows
  (21 fetch groups x 40 periods, retrieved 2026-11-14 21:05:35-37 UTC, valid
  times after retrieval, no blank required metrics, unique keys, earlier bytes
  unchanged). Repeating the search ("21 reused") and switching to 5 days
  reused the full saved forecasts and appended nothing.
- No key, `d1c3bdf`: Landing works; Dashboard shows the key message and the
  `variables.env.example` setup step, 0/83 coverage and all 83 destinations as
  "Weather not loaded" with no invented scores; nothing was written.

**Not tested.** Live quota, network, storage and missing-weather states (none
occurred; the offline suite covers them); map tiles, hover, zoom/reset and
fonts were not judged visually (chart data was read directly); no live
Dashboard fetch; Windows, phone and other viewports.

**Defects.** None in the application. Cosmetic: the window option reads "Next 1
days" and the wind notice "1 of your top recommendations include"; the
smallest fix is singular wording for a count of 1. Documentation: the dated
P6.1 preparation section above still says Gabriel's review "remains open"
(superseded by the P6.1 review and merge note); README quotes the Windows
result (523 passed, 2 skipped), equivalent to 524 passed, 1 skipped on macOS.

**New genuine records.** 840 forecast rows exist only in the uncommitted CSV of
the `3444728` test clone (22,767 to 23,607 rows). They are preserved there and
are not part of this change; proposing them for commit needs a diff review.

**Result.** The reviewed `d1c3bdf` repository installs, tests and runs from a
fresh clone on macOS with no application failure found. Ready for final
delivery from this tester's perspective once Alejandra's report and
Christian's review complete P6.2.

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
