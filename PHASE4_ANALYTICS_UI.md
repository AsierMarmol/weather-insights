# Phase 4 - Analytics and Streamlit Interface

Updated: 11 November 2026.

## Current checkpoint

Not started; specification is in Phase 2. These are planning instructions, not evidence that features, data verification, or peer reviews are complete.

## Purpose and finish condition

Implement explainable weather recommendations and three analyses within Finder and Dashboard views.

**Entry condition:** Agreed analytics contracts and usable API/storage interfaces exist; real history collection is running.

**Finish condition:** Both views use one consistent result set; preference scoring and travel penalty are correct; three analytical views and at least two labeled charts work with real data.

The instructor assignment README in the parent folder is authoritative; its summary is a supporting reference, not an additional specification. The selected product and scoring contract live in [PHASE2_SCOPE.md](PHASE2_SCOPE.md). Roles and workload rules live in [TEAMROLES.MD](TEAMROLES.MD); navigation is in [PROJECT_PHASES.md](PROJECT_PHASES.md).

## Ordered checklist

Work in dependency order. Independent tasks can proceed together after their shared interfaces are agreed. Owners implement their tasks and checks; reviewers verify the actual changes. Pending means not yet demonstrated.

| ID | Small action | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P4.1 | Implement three weather component matches | Christian | Selin | P3.8 | Inclusive thresholds, equal partial credit, completeness and zero-period handling pass known-answer tests. | Pending |
| P4.2 | Implement selected-mode penalty and full ranking | Christian | Selin | P4.1 + P3.7 | One point/hour capped at five, missing mode unavailable, unrounded ordering and agreed ties correct. | Pending |
| P4.3 | Generate explanations and breakdown values | Christian | Selin | P4.2 | Explanations reflect actual passed counts, data periods and travel deductions; no invented narrative numbers. | Pending |
| P4.4 | Build Finder controls and validation | Asier | Gabriel | P2.7 + P3.1 | Car/Train, activity filters, 24/48/72 hours and editable weather preferences validate before analysis; missing-key startup gives safe setup guidance instead of an import traceback. | Pending |
| P4.5 | Connect shared results, refresh and navigation | Asier | Gabriel | P3.11 + P4.2 + P4.4 | Suitable fetched data reused across controls/views; changes recalculate locally; freshness and failures visible. | Pending |
| P4.6 | Build recommendation cards and details | Asier | Gabriel | P4.3 + P4.5 | Each result explains weather match, final score, selected-mode reference duration and source limitations. | Pending |
| P4.7 | Build comparison and score-breakdown dashboard | Selin | Asier | P4.3 + P4.5 | Distinct cross-city and derived-score analyses; separate units/scales and shared ranking inputs. | Pending |
| P4.8 | Build observed-history selection and chart | Selin | Asier | P3.9 + P4.5 | Selected city has timestamped observed trend, honest empty/single-point state and no forecast-history substitution. | Pending |
| P4.9 | Implement and run Finder/Dashboard consistency checks | Selin | Asier | P4.6-P4.8 | Finder equals Dashboard under same ordering; sort entire eligible pool before display limit; excluded/unavailable counts clear. | Pending |
| P4.10 | Implement final Finder/navigation usability fixes and run complete journeys | Asier | Gabriel | P4.9 | Reviewed Finder/navigation fixes and an end-to-end result report; dashboard defects go to Selin, API to Gabriel, models/storage to Alejandra, scoring to Christian as named follow-up tasks. | Pending |

## Analytical evidence

| Analysis | Category | Inputs | Required display and check |
| --- | --- | --- | --- |
| City weather comparison | Cross-location | Evaluated real forecast periods | Labeled comparison chart; disclose aggregation and do not mix C, km/h and percent on one unexplained scale |
| Weather/travel score breakdown | Derived metric | Three component matches and sourced selected-mode minutes | Components, weather-match percent, deduction points and final score; counts and formula reproducible |
| Recent observed conditions | Trend | Genuine current-condition logs | Chronological line chart for a selected city with units; repeated provider timestamps not independent observations |

Activity tags only filter; they do not change weather weights. Cloud cover may be displayed or sorted but does not earn personal-score points. Precipitation probability is not necessarily rain alone, and average period probability is not whole-trip rain probability. Reference travel durations are not traffic or train-availability promises.

## Interface acceptance

Show the search's actual dates, local daytime convention, data age, selected transport and unavailable reasons. A station-to-station train reference and a road reference must be labeled according to the agreed convention. Keep preferences and ranking shared across views; do not duplicate analytics in UI code.

Do not silently relax thresholds for poor matches. No destinations, one destination, missing transport time, failed weather requests and short history each need useful states. Every chart must show real input values and meaningful labels. Optional images need appropriate rights/credits; no invented tourism facts.


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

Begin pure scoring checks and Finder structure against the approved contracts; keep real observation collection running.
