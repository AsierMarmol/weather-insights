# Phase 4 - Analytics and Streamlit Interface

Updated: 12 November 2026. **In progress:** P4.1 approved by Gabriel and merged (PR #10); P4.2 approved by Asier and merged (PR #11); P4.3 approved by Gabriel and merged (PR #12).

## Purpose and dependencies

Deliver Searcher and Dashboard on the same data and calculations, then connect the user journey. Preparation can use the reviewed result shape; acceptance needs actual Phase 3 components and P2.5 verification.

## Deliverables

| Step | Whole deliverable | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P4.1 | Complete Searcher | Asier | Gabriel | Phase 3 accepted incl. P2.5 | Editable seasonal preferences, rolling 1-5 days, All filters from catalog values, five leading results/full ranking, useful errors and tests. | Approved by Gabriel and merged into dev in PR #10 (12 November 2026) |
| P4.2 | Complete Dashboard | Selin | Asier | Phase 3 accepted incl. P2.5 | Interactive ranking, weather comparison and simultaneous-preference metrics; at least two labeled real-data charts, missing states and tests. | Approved by Asier and merged into dev in PR #11 (12 November 2026) |
| P4.3 | Integrate the app | Asier | Gabriel | P4.1 + P4.2 | Shared search state, navigation, data reuse, progress/freshness and partial errors verified end to end. | Approved by Gabriel and merged into dev in PR #12 (12 November 2026); 11 integration tests, 312 total tests pass |

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
| 12 November 2026 | P4.1 | Asier/Codex implemented searcher.py and connected app.py; 22 Searcher tests and 259 total tests pass; Flake8 zero findings. PR #9 approvals/merge confirmed first. Genuine data unchanged; no new live requests. | Approved by Gabriel; merged in PR #10 |
| 12 November 2026 | P4.2 | Selin/Claude Code implemented `src/weather_app/dashboard.py` (`render_dashboard`, `render_dashboard_page`) and `tests/test_dashboard.py`; replaced only the Dashboard placeholder in `app.py` with `render_dashboard_page()`. Details and evidence below. 301 tests pass; Flake8 zero findings; genuine CSV checksum unchanged; no live requests. | Awaiting Asier review |

## Next action

Phase 4 is complete: P4.3 was approved by Gabriel and merged in PR #12. Proceed with Phase 5 component acceptance and the complete rubric walkthrough. P4.1/P4.2 approvals do not imply P4.3 approval.


### P4.1 implementation and state contract

`searcher.initial_preferences(now_utc, defaults)` derives the initial season from Europe/Madrid; only first use or explicit reset applies it. Valid manual choices persist across reruns, navigation and season changes. Activities/sizes derive from the real catalog and visibly default to All. Empty selections mean All. P4.3 makes All exclusive in both views: a specific choice clears All; choosing All or clearing the selection restores it. Invalid temperature ranges disable Search.

`search_destinations` filters before asking the actual WeatherService for forecasts and delegates all scoring to analytics. It captures one common UTC search time and refreshes cached forecasts once when they no longer cover the requested window. The service remains the only fetch/save path. No network occurs on initial load, control edits, reset or navigation. Fresh searches save automatically and show progress; key/network/quota/provider/storage/location failures use safe distinct messages.

The view displays up to five available destinations, the full eligible ranking (including unavailable reasons), travel units, score explanation, window/preferences, coverage and data age. Changed controls leave the old results explicitly labeled until another search. Old results show a warning after three hours. The three-day historical genuine replay renders Seville 83.9, Toledo 50.8 and Segovia 46.9; this is a test replay at the original search time, not fresh weather.

Shared session keys: `search_preferences` (current controls), `search_run_at_utc`, `search_analysis_rows`, `search_result_preferences` (preferences used for those results), `search_errors` and `search_cached_count`. `weather_service` is lazily created once per session. P4.2/P4.3 must consume the result snapshot and its preferences together, rather than implying that unsent control changes have recomputed scores. Dashboard now consumes this contract; P4.3 implementation is verified below and awaits review.

Validation: 259 tests passed, including 22 new checks for season/Madrid-month boundaries, navigation/reset persistence, lazy requests, filters, top-five/full-ranking agreement, save/cache reuse, safe failures, empty matches, incomplete cached coverage, historical genuine replay and age warnings. Tests block live HTTP and assert the genuine CSV is unchanged. Flake8 reports zero findings. P4.1 publication for Gabriel review is authorized; review and merge remain pending. Selin owns the separate P4.2 implementation.

### P4.2 Dashboard implementation

`dashboard.render_dashboard(analysis_rows, catalog_rows)` presents the Searcher's last result snapshot; `render_dashboard_page()` reads `search_analysis_rows`, `search_result_preferences`, `search_preferences` and `search_errors` and loads the catalog. The Dashboard never fetches, saves, scores or re-sorts: rank is each row's position among available rows in the engine's order, so it matches the Searcher after filtering. It validates rows against `analytics.RESULT_FIELDS` and shows a safe message for malformed results.

Three analyses, each with a chart and a table: suitability ranking (final score, with weather match and driving penalty), cross-city weather comparison (selectable mean temperature °C, highest period precipitation probability %, highest period wind km/h, with the searched preference range/limit marked and the aggregation explained), and periods meeting all preferences (% with k/n counts). Context shows the search time and forecast window in Europe/Madrid, daytime hours, forecast retrieval times and age, the preferences used for the results, a notice when controls changed after the search, and the Searcher's three-hour freshness warning. Destination/activity/size filters use `dashboard_*` keys, visibly default to All (All is exclusive), use ANY within a group and AND between groups, persist across navigation and never change `search_*` state. Unavailable destinations are listed with the Searcher's safe messages (service error codes take precedence), not as zero scores. No-search, empty, no-match and only-unavailable states are explicit.

Validation: `tests/test_dashboard.py` (42 tests) covers helpers, contract validation, filter logic, chart data/axis units/preference markers, AppTest interactions, freshness and changed-settings notices, a read-only replay of the genuine P2.5 forecasts through the real analytics engine (charts plot Seville, Toledo, Segovia with the independently tallied scores) and an end-to-end `app.py` journey (fake HTTP, temporary store: search, open Dashboard, filter, navigate back) proving the view makes no requests and writes no records. Full suite 301 passed; Flake8 zero findings. Visually checked with the genuine replay in a throwaway local harness outside the repository.

Limitations: genuine data currently covers three cities from P2.5; wider real coverage comes from normal searches. Dashboard filters only narrow the shown result; changing days/preferences requires a new search in the Searcher. P4.3 verification is recorded below; its peer review and P5.4 final chart acceptance remain pending.


### P4.3 integration - 12 November 2026

Asier / OpenAI Codex verified the merged app at dev `d6d210e`. P4.2 PR #11 is approved by Asier and merged; earlier pending notes above describe the original submission state. No second page router, service, data store or analytics implementation was needed.

Two reproduced gaps were corrected: the Dashboard's weather-measure radio reset after navigation, and Searcher's default All could remain alongside a specific choice, causing the specific choice to be ignored. Dashboard now saves/restores its selected measure outside transient widget state. Both views use the same small `searcher.normalize_all_selection` helper for exclusive All behavior. Searcher’s existing empty-selection test now checks the visible All value.

`tests/test_app_integration.py` adds 11 complete journeys through app.py: metric/filter persistence; consistent All behavior; all five forecast windows; changing preferences while retaining the labeled old snapshot until Search; resetting an invalid Dashboard destination filter after a narrower search; partial failure and recovery; persistence failure/recovery without charting unsaved results; stale-result warnings in both views and explicit refresh; empty new searches clearing old charts; progress completion/cleanup; and genuine saved data through the actual service, storage, analytics, Searcher and Dashboard at a fixed historical replay time.

The two regression tests failed before their fixes. Final verification: **312 tests passed; Flake8 zero findings**. Synthetic HTTP and temporary stores isolate writes; integration fixtures block live HTTP and verify every repository data file remains unchanged. The genuine replay copies the existing CSV to a temporary store, renders Seville/Toledo/Segovia in the expected order and scores, and makes zero HTTP calls. Normal navigation/filtering does not request or write weather. The same service instance is reused, and successful requests retain the existing automatic-saving path. No new live requests or genuine-data edits were made.

**Status:** implemented, awaiting Gabriel review. Phase 5's integrated rubric acceptance and the clean-clone delivery check are still pending. No commit, push or merge performed for P4.3.
