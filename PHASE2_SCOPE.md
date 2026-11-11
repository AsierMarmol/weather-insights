# Phase 2 - Ideation and Project Flexibility

Updated: 11 November 2026.

## Current checkpoint

In progress: P2.1 scope-to-rubric deliverable is prepared and document-checked; Gabriel's peer review is pending. Catalog, contracts and technical evidence still need verification. These are planning instructions, not evidence that features, data verification, or peer reviews are complete.

## Purpose and finish condition

Translate the agreed Spain getaway idea into a bounded, testable implementation plan.

**Entry condition:** Phase 1 is complete according to the user. Retain its established setup.

**Finish condition:** All five can explain the scope, catalog rules, data/scoring contracts, required analyses and assigned tasks; unresolved implementation decisions are reviewed before dependent work.

The instructor assignment README in the parent folder is authoritative; its summary is a supporting reference, not an additional specification. The selected product and scoring contract live in [PHASE2_SCOPE.md](PHASE2_SCOPE.md). Roles and workload rules live in [TEAMROLES.MD](TEAMROLES.MD); navigation is in [PROJECT_PHASES.md](PROJECT_PHASES.md).

## Ordered checklist

Work in dependency order. Independent tasks can proceed together after their shared interfaces are agreed. Owners implement their tasks and checks; reviewers verify the actual changes. Pending means not yet demonstrated.

| ID | Small action | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P2.1 | Write the scope-to-rubric checklist and list unresolved proposals | Asier | Gabriel | Phase 1 | Group distinguishes rubric requirements, agreed choices and proposed defaults. | Deliverable prepared - awaiting Gabriel review |
| P2.2a | Verify the 3-5 seed cities against the agreed catalog contract | Alejandra | Christian | P2.4 + P2.5 | Seed records have sourced coordinates, activity tags and selected-mode reference times; unresolved fields are explicit. This limited seed enables early collection. | Pending |
| P2.2 | Create the numbered 20-30-city candidate catalog and seed shortlist | Alejandra | Christian | P2.1 | Candidate city IDs, inclusion evidence and 3-5 seed IDs recorded; IDs map to named research batches in TEAMROLES.MD. | Pending |
| P2.3 | Verify API fields, access and request constraints | Gabriel | Alejandra | P2.1 | Current/forecast field and unit mapping, safe credential smoke check and dated official sources; no key recorded. | Pending |
| P2.4a | Write activity-tag evidence rules and sample tagged city records | Selin | Asier | P2.2 | Definitions for the four categories, acceptable source evidence and sample records delivered to Gabriel and Alejandra. | Pending |
| P2.4 | Write sourced car/train reference-time rules | Gabriel | Alejandra | P2.2 + P2.4a | Written reference origin/destination, transfer, duration and missing-data conventions, using Selin's activity-source rules. | Pending |
| P2.5 | Agree models, catalog schema and persistence contract | Alejandra | Christian | P2.3 + P2.4 | Schemas, timestamps, storage choice, append/reload rules and schema-change/migration procedure documented. | Pending |
| P2.6 | Freeze scoring, time windows and known-answer examples | Christian | Selin | P2.3 + P2.5 | Exact approved behavior covers units, boundaries, missing data, ties and mode-specific penalty. | Pending |
| P2.7 | Sketch Finder controls and user journey | Asier | Gabriel | P2.4 + P2.6 | Inputs, defaults, result card fields and error messages agreed. | Pending |
| P2.8 | Specify Dashboard analyses and chart contracts | Selin | Asier | P2.5 + P2.6 | Three distinct analyses, two labeled charts, data freshness and history empty states specified. | Pending |
| P2.9 | Write module interfaces and the file ownership map | Asier | Gabriel | P2.5-P2.8 | Concrete signatures, input/output examples and file boundaries connect the completed model, scoring and UI specifications; each implementation row has one author and reviewer. | Pending |
| P2.10 | Check the scope pack against acceptance cases and publish the readiness checklist | Selin | Asier | P2.2-P2.9 + P2.2a | Scope pack has resolved required choices, reviewed seed evidence and actionable handoffs; discrepancies returned to the named author before implementation. | Pending |

## P2.1 deliverable - scope and rubric review

Prepared: 11 November 2026. Task owner/requester: Asier (AsierMarmol). Actual AI collaborator: OpenAI Codex. Assigned peer reviewer: Gabriel (gabrielstec). Status: deliverable prepared and document checks passed; Gabriel's review is pending. No new team approval, API success, source verification, code implementation or publication is claimed.

Compared with the complete instructor assignment README and supporting summary in the parent directory. The assignment sets the requirements; the summary's examples are illustrative. The existing package and source files were inspected: the UI remains heading-only and the core modules remain starter placeholders. Existing setup is preserved.

### Scope confirmed from the user's decisions

- Madrid is the departure context; choose a curated 20-30-city mainland-Spain catalog, including suitable smaller tourist destinations. The actual list is still to be proposed and reviewed.
- Select Car or Train. Use sourced one-way reference journey times; no flight network, live traffic, train availability, prices or booking integration.
- Filter by Culture and sightseeing, Food and gastronomy, Coast and seaside, or Nature and outdoor visits. A destination can have several tags; activities do not change scoring weights.
- Evaluate the next 24, 48 or 72 hours and destination-local daytime from 09:00 inclusive to 18:00 exclusive, with actual dates shown.
- Earn equal positive credit for preferred actual temperature, acceptable precipitation probability and acceptable wind in each complete evaluated period. Convert passed checks to a weather-match percentage.
- Deduct one point per selected-mode travel hour, capped at five, and floor the final score at zero. Missing duration cannot earn a zero penalty. Cloud cover is informational only.
- Deliver a local Streamlit Finder and Dashboard with useful comparisons, derived-score explanations and a genuine observed-weather timeline. Keep existing repository/package/environment names unless a later explicit decision changes them.
- Phase 1 was completed by Asier. Future tasks have concrete named authors and reviewers; records describe actual human and AI contributions.

### Scope-to-rubric checklist

Checked here means included in the plan and mapped to a concrete verification step, not implemented or awarded points.

| Requirement | Planned project evidence | Build tasks | Verification tasks | P2.1 finding |
| --- | --- | --- | --- | --- |
| Reusable inheritance | Generic JSON APIClient with meaningful OpenWeatherClient subclass | P3.2-P3.3 | P5.8 | Covered in design |
| Intentional encapsulation | Justified public/protected/private state in models/client, not decorative private fields | P3.1-P3.3 | P5.8 | Covered; exact attributes selected in P2.5/P2.9 |
| Special method beyond init and computed property | Useful model representation and actual derived value such as unit conversion | P3.1 | P5.8 | Covered; concrete model contract pending |
| Safe dotenv credentials | Local variables.env; no real key in source, repo, UI, logs or errors | Retained setup; P3.2, P4.4 | P5.3, P6.3 | Setup retained; runtime handling to implement |
| Distinct errors and input validation | Invalid input/key/location and network/server failures explained without raw tracebacks or bare except | P3.2-P3.3, P4.4 | P5.3, P5.7 | Covered in design |
| Multiple locations degrade gracefully | Valid destinations remain usable when one request fails | P3.3, P3.11 | P5.3, P5.7 | Covered in design |
| Every successful fresh fetch logged | Append current observations and forecast batches with retrieval and provider/valid timestamps; cache redisplay is separate | P3.4-P3.6 | P5.5, P6.4 | Covered; storage and collection schedule pending |
| Genuine history accumulated and committed | Collect observed conditions early, retain real records, submit nonempty data and keep fixtures separate | P3.5-P3.6 | P5.5, P6.4, P6.8-P6.9 | Covered; no actual history collected yet |
| Three distinct analyses across two or more categories | Cross-city comparison, derived preference/travel score breakdown and observed-condition trend | P4.1-P4.3, P4.7-P4.8 | P5.4-P5.6 | Covers all three categories in design |
| Real analytical inputs | Use fetched/logged weather and sourced travel references; distinguish forecasts from observations | P3.5-P3.7, P4.5-P4.8 | P5.2, P5.5-P5.6 | Covered; sources/data still need evidence |
| Two views and meaningful location interaction | Finder with mode/activity/weather controls and destination details; Dashboard with selected-city history | P4.4-P4.8 | P5.6-P5.7 | Covered; not implemented |
| Two correct labeled charts and usability | Cross-city chart plus observed-history chart, with units, dates and empty/error states | P4.7-P4.10 | P5.6-P5.7 | Covered; cards/map alone do not satisfy this |
| Installable package and clean-clone README | Retain src/pyproject, implement actual modules and document reproducible setup | Existing setup; P2.9, P6.2-P6.6 | P6.8 | Structure exists; final feature verification pending |
| Specific AI record and co-author attribution | Task-linked records of actual requests, outputs, checks and decisions, plus correct AI trailers | Each substantive implementation task | P6.7a-P6.7e, P6.7 | Convention exists; maintain during work |
| Real contributions and whole-code understanding | Named coding deliverables, actual authorship and individual demonstrations | Owned phase tasks | P5.10a-P5.10e, P5.10, P6.7 | Assignments exist; future evidence required |
| Accessible repository and proper submission | Reviewed final commit, committed real data, clean install and actual repository URL submission | P6.1, P6.9-P6.10 | P6.8, P6.10 | Planned; no submission claimed |

P2.1 conclusion: the selected idea has no identified conflict with the assignment. Required behavior has an implementation and verification path. The course does not require a flight service, hosting, a chatbot or a particular tourism catalog size. Reference travel data and activity metadata are useful enrichment; they do not replace the required weather functionality.

### Unresolved decisions and evidence, in dependency order

| Item still to resolve | Concrete output | Author | Reviewer | Task / downstream constraint |
| --- | --- | --- | --- | --- |
| Actual candidate cities and initial seed | Stable numbered shortlist with tourism inclusion evidence and 3-5 seed candidates | Alejandra | Christian | P2.2; no final city list claimed yet |
| Actual account/API feasibility | Required endpoints/fields, units, limits and safe access-check result | Gabriel | Alejandra | P2.3; needed before final schema/scoring contract |
| Activity tagging evidence | Category definitions, qualifying sources and tagged examples | Selin | Asier | P2.4a; feeds reference-data rules |
| Comparable reference travel times | Origin/destination convention, reference-service assumptions, transfers, missing/unavailable labels and dated sources | Gabriel | Alejandra | P2.4; do not mix unlabelled door-to-door and station-only times |
| Data/model/storage contracts | Concrete fields/types/units/timestamps, CSV or SQLite choice, append/duplicate/write-safety/migration rules | Alejandra | Christian | P2.5; verified seed in P2.2a depends on this |
| Exact timing and ranking defaults | Common-window boundary examples, complete-period rules, tie-breaks and hand-calculated cases | Christian | Selin | P2.6; core formula is already agreed |
| Control defaults and activity-selection behavior | Editable weather defaults, any-tag versus all-tag matching, empty selection behavior and Finder sketch | Asier | Gabriel | P2.7; current defaults in the specification are proposals |
| Dashboard display/aggregation choices | Chart inputs/units, aggregations, displayed count, alternative sorting and history states | Selin | Asier | P2.8; top-10/top-20 proposal still needs review |
| Exact files and callable interfaces | Function signatures, model examples, UI split and named module ownership | Asier | Gabriel | P2.9; avoid conflicting implementations |

Refresh/cache thresholds and request budget are documented in Gabriel's P2.3 report and implemented/tested in P3.10. Collection frequency and operation belong to Alejandra's P3.6, within that budget. Public product title can be resolved with the UI documentation; it must not block the early data path. Optional map/photos are not prerequisites for mandatory charts or history.

### Gabriel's review checklist

- [ ] Compare the agreed-scope summary with the user's choices; identify any invented or missing behavior.
- [ ] Check every requirement row against the instructor assignment and confirm the build/verification references.
- [ ] Confirm that proposed defaults are not presented as approved decisions.
- [ ] Confirm real history, individual contributions and accurate AI attribution remain explicit.
- [ ] Record actual approval or requested corrections. No review is assumed from this checklist.

### Handoff after review

Asier's P2.1 document deliverable is ready for Gabriel. P2.1 remains awaiting review until Gabriel's actual response is recorded. After review, P2.2 (Alejandra's candidate catalog) and P2.3 (Gabriel's API report) can proceed in parallel. The seed-verification child P2.2a comes later, after P2.4/P2.5; its position near P2.2 in the table is not an instruction to skip those dependencies.

## Agreed product contract

The group decision is a weather-led getaway finder departing from Madrid, for a curated selection of approximately 20-30 tourist cities in mainland Spain. Europe-wide and flight-based scope has been replaced. The public product title is still to confirm; retain the repository/package names for now.

| Item | Agreed behavior |
| --- | --- |
| Audience and question | A traveler in Madrid asks which Spanish destination best fits their weather preferences over the next few days. |
| Geography | Mainland Spain only; candidate cities are reviewed for tourism interest. The list is curated, not an exhaustive or objectively best list. |
| Transport | Select Car or Train, never an automatic Either choice. Use sourced one-way reference journey times from Madrid for the selected mode. |
| Activity filters | Culture and sightseeing; Food and gastronomy; Coast and seaside; Nature and outdoor visits. A city may carry multiple tags. Tags filter destinations and do not add score points. |
| Forecast horizon | Next 24, 48 or 72 hours, with actual covered dates displayed; not an arbitrary future-weekend calendar. |
| Daytime | Destination-local 09:00 inclusive to 18:00 exclusive within one common evaluation window. |
| Weather preferences | Preferred actual temperature range in C, maximum precipitation probability in percent, and maximum wind speed in km/h. |
| Weather scoring | Three equally weighted pass/fail checks per complete evaluated daytime period; inclusive preference boundaries and partial credit. |
| Travel scoring | One point deducted per one-way reference travel hour, capped at five points. |
| Cloud cover | Informational/comparison data only; no sunshine bonus or fourth scoring criterion has been agreed. |
| Execution | Local Streamlit application, retaining the existing installable weather_app package and uv setup. |
| Experience | Finder recommendations plus a comparison/history Dashboard. Visual style can be polished without obscuring units, limitations or required functionality. |

Main scenarios: select transport/activity/weather preferences and receive an explained ranking; compare destinations and the components behind their scores; inspect a selected city's genuinely collected recent conditions. Coast/nature tags describe tourism opportunities near a city: city-center forecasts do not establish beach, mountain, or activity safety conditions.

## Exact agreed scoring

For n complete evaluated daytime forecast periods, each period earns one check for temperature within the inclusive preferred range, one for precipitation probability at or below its limit, and one for wind at or below its limit.

```text
weather_match_pct = 100 * passed_checks / (3 * n)
travel_penalty_points = min(reference_journey_minutes / 60, 5)
recommendation_score = max(0, weather_match_pct - travel_penalty_points)
```

All three components contribute equally. Example: 24 passed checks out of 30 gives 80% weather match; a two-hour reference trip deducts 2 points, giving 78/100. This percentage measures matched preferences, not the probability of a pleasant trip. Travel beyond five hours receives the same five-point maximum deduction. Times must be valid and positive; missing time for the selected mode makes that option unavailable rather than awarding zero penalty.

Require all expected temperature/precipitation/wind samples for that city's evaluated periods. Missing values must not shrink the denominator and improve its score. No evaluated daytime periods means unavailable, not division by zero. Freeze the evaluation window once per search; use one sufficiently fresh forecast batch per city and separate predicted valid times from retrieval times. Preserve raw precision for ranking and round only for display.

## Proposed defaults to verify in this phase

These are implementation proposals, not additional user-approved product features.

| Decision | Proposed default / required resolution | Owner / reviewer |
| --- | --- | --- |
| Destination list | Review 20-30 candidates before adopting a final list; exclude Madrid as a getaway destination. No city names or journey times are verified by this plan. | Alejandra writes shortlist (P2.2); named batch authors deliver P3.7a-P3.7e |
| Travel reference convention | Define origin/destination points, normal one-way car duration without live traffic, and representative rail station-to-station duration. Clearly disclose that these are different reference measures, not guaranteed door-to-door times. Define how transfers and varying services are handled. | Gabriel / Alejandra |
| Unknown vs unavailable train | Distinguish missing verification from a verified lack of the agreed rail option; do not claim no rail service merely because a source is missing. | Alejandra / Christian |
| Activity selection | Multi-select with any selected tag matching; an empty selection means all activities. No automatic weather presets. | Asier / Gabriel |
| Default controls | Choose sensible editable temperature/rain/wind defaults after checking actual fields and UX; do not label them scientifically optimal. | Asier / Selin |
| Ranking ties | Unrounded final score descending, then mean evaluated-period precipitation probability ascending, then stable city ID. | Christian / Selin |
| Poor matches | Show best available matches with explicit trade-offs; do not silently relax thresholds. No hidden minimum score. | Asier / Christian |
| Display size | Up to 10 Finder cards and 20 Dashboard destinations, sorting/filtering the full eligible catalog before slicing. | Selin / Asier |
| Window convention | Freeze a start on the next forecast grid timestamp relative to search time; use [start, start + horizon), apply local daytime filtering, and reject stale/incomplete batches. Confirm exact boundary examples. | Christian / Gabriel |
| Storage | CSV initially proposed; choose CSV or SQLite after reviewing forecast volume and write safety. | Alejandra / Christian |
| Refresh and cache | Verify account limits/fields; set explicit freshness thresholds, bounded retries and a shared request budget. Reuse suitable data across preferences, mode, tabs and ordering. | Gabriel / Alejandra |
| Presentation extras | Map/photos are optional polish after required charts work. Any image has appropriate rights and credits. No live routing, train schedules, booking or prices. | Selin / Asier |

## Catalog and data contracts to fill

Catalog: stable city ID; name and region; mainland eligibility; city coordinates; named time zone; activity tags and tourism sources; per-mode reference minutes, origin/destination convention, source and verification date; verification status; optional image/credit. Keep exclusions and missing metadata auditable. Source candidates include official tourism and transport/operator information; verify each claim, do not infer train time from distance.

Current observations: city ID, fetch ID/retrieval UTC time, provider observation UTC time, normalized fields/units and source. Forecast records additionally identify batch and future valid UTC time. Cache records are operational reuse data, not a replacement for persistent logs. Store necessary fields without secret-bearing request URLs.

Append every successful fresh fetch, including duplicate provider timestamps as fetch events; deduplicate appropriately in analytical views so repeats are not counted as independent observations. Never relabel saved predictions as observed weather. Cached redisplay is not a fresh fetch. Keep deterministic fixtures separate from the submitted genuine history. Establish collection ownership/frequency in Phase 3 and include accumulated data in Git.

## Architecture and analytics contract

| Boundary | Planned responsibility | Owner |
| --- | --- | --- |
| Generic APIClient -> OpenWeatherClient | Reusable JSON request behavior; provider endpoints/fields; distinct safe failures and partial batches | Gabriel |
| Destination, preferences, current/forecast models | Valid units/timestamps; deliberate encapsulation; useful representation and a computed property such as unit conversion | Alejandra |
| Storage/catalog | Validate reference data; append and reload real logs; protect overlapping writes | Alejandra |
| Pure analytical functions | Coverage, three component scores, travel penalty, ranking and explanation values | Christian |
| Finder/orchestration | Input controls and validation, shared result state, recommendation cards | Asier |
| Dashboard/chart helpers | Cross-city comparison, score breakdown, observed history, labeled charts | Selin |

Agree exact signatures and ownership of any shared helper before coding. Inject configuration into the API client at the application boundary so pure models/analytics/tests do not require a real key. A protected member is a convention, not secret protection; use private name-mangling only where justified.

Three distinct analytical views are required: cross-city weather comparison; derived weather-match/travel-adjusted score with component breakdown; observed-condition trend for a selected city. These cover all three rubric categories within two UI views. Use at least a labeled comparison chart and a genuine-history line chart; a map and cards alone are insufficient evidence. A single observation is one point; no history produces an honest empty state.

## Scope boundaries and acceptance priorities

No flights, islands, live traffic, live train availability/ticket pricing, booking, accounts, payments, chatbot, runtime AI, arbitrary future-date forecasts, or fabricated history. Reference travel times are enrichment; weather remains the central data source and ranking influence. Activity selection is a filter, not a second recommendation algorithm.

Before implementation, approve known-answer cases for score arithmetic, thresholds, selected transport, missing duration/fields, period completeness, time-zone boundaries, ties and full-pool ordering. Acceptance also covers secret-safe errors, partial batches, current/forecast persistence, chart correctness, consistent views, clean installation and all five meaningful contributors. Teacher requirements remain mandatory; examples and optional tools from the summary are not extra requirements.


## Workload and handoff

Every owner supplies code or the specified artifact, relevant checks, limitations, and a focused review request. Catalog work is assigned explicitly in P3.7a-P3.7e; each row has one batch author and a different reviewer. Before starting a task, estimate it as small/medium/large; split large tasks and rebalance explicit subtasks if someone becomes a bottleneck. Track actual effort and evidence rather than equal commit counts. Asier implements orchestration and Finder integration; Gabriel implements API fixes, Alejandra model/storage fixes, Christian scoring fixes, and Selin Dashboard fixes. A handoff is a reviewed artifact or interface, not a coordination assignment.

## Updating this phase when something changes

The task owner records the change and reason before dependent work continues. Check all six phase plans for impact, then update every affected step, dependency, finish condition and acceptance check in the same change. Also update the Phase 2 specification, TEAMROLES.MD, PROJECT_PHASES.md and application README when affected. Do not rewrite unaffected history or invent completion evidence.

Keep task IDs stable. Split a broad task into linked subtasks before starting if it has more than one independently reviewable outcome. If a previously completed check is invalidated, retain its old evidence and mark the affected task Needs recheck with a named owner; do not leave it silently Done. Distinguish Pending, In progress, Blocked (with reason), Needs recheck and Done (with evidence).

The named peer reviewer checks both the technical change and consistency across affected phases. The author writes the affected-file/task list and the named reviewer verifies it; no separate coordinator role is required. Record the change and its affected task IDs in the change register in [PROJECT_PHASES.md](PROJECT_PHASES.md). Full maintenance procedure: that file's Plan maintenance section.

## Completion evidence

| Evidence | Actual result / link |
| --- | --- |
| Completed steps and reviewed PRs | Pending |
| Checks actually run, results, and limitations | Pending |
| Real data and source verification relevant to this phase | Pending |
| Open defects / next owner | Pending |
| Team walkthrough and phase closure | Pending |

All phase status changes must reflect actual work. Shared decisions use group wording; names identify real owners and reviewers. Future implementation follows the established AI-record and attribution convention. This organizational planning update does not edit PROMPTS.md, as requested.

## Next action only

Gabriel reviews the P2.1 deliverable above. After actual review, Alejandra writes P2.2 and Gabriel writes P2.3. No catalog, live API result or peer approval is claimed by preparing this document.
