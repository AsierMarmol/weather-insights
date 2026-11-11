# Phase 5 - Integration and Quality Review

Updated: 11 November 2026.

## Current checkpoint

Not started; testing also accompanies every earlier coding task. These are planning instructions, not evidence that features, data verification, or peer reviews are complete.

## Purpose and finish condition

Verify the integrated product and all ten rubric points with evidence, then resolve defects and demonstrate shared understanding.

**Entry condition:** Required core, scoring and UI features are integrated; a named review commit and known limitations are recorded.

**Finish condition:** Required scenarios pass; each rubric row has actual evidence; blocking defects are fixed; every teammate can explain the entire flow.

The instructor assignment README in the parent folder is authoritative; its summary is a supporting reference, not an additional specification. The selected product and scoring contract live in [PHASE2_SCOPE.md](PHASE2_SCOPE.md). Roles and workload rules live in [TEAMROLES.MD](TEAMROLES.MD); navigation is in [PROJECT_PHASES.md](PROJECT_PHASES.md).

## Ordered checklist

Work in dependency order. Independent tasks can proceed together after their shared interfaces are agreed. Owners implement their tasks and checks; reviewers verify the actual changes. Pending means not yet demonstrated.

| ID | Small action | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P5.1 | Freeze the review scope and evidence matrix | Asier | Gabriel | Phase 4 | Named commit, requirements, repository file inventory and known limitations recorded; map every required module/artifact to implemented behavior; no prediction of grades. | Pending |
| P5.2 | Audit catalog and journey evidence | Alejandra | Christian | P5.1 | Run a catalog evidence audit and produce a source-gap list. Assign each correction to its original batch author; verify the corrected catalog. | Pending |
| P5.3 | Exercise API, refresh and secret-safe failures | Gabriel | Alejandra | P5.1 | Validation, bad credentials/locations, server/network/quota failures and partial results behave correctly. | Pending |
| P5.4 | Independently verify scoring boundaries | Christian | Selin | P5.1 | Hand-computed examples, unit conversions, transport mode, caps, ties, time boundaries and incomplete periods checked. | Pending |
| P5.5 | Audit persistence and genuine history | Alejandra | Christian | P5.1 | Timestamped fetch records accumulate, survive reload and remain separate from fixtures/forecasts; real dataset ready for Git. | Pending |
| P5.6 | Verify charts and user interpretation | Selin | Asier | P5.1 | Two labeled charts, three distinct analyses, fair scales, empty states and consistent rankings checked. | Pending |
| P5.7 | Run complete car and train journeys | Asier | Gabriel | P5.2-P5.6 | Users can filter activities, change horizon/preferences, compare results and inspect history; failures remain understandable. | Pending |
| P5.8 | Write and run the OOP/package boundary verification | Gabriel | Alejandra | P5.3 + P5.5 | Inheritance, public/protected/private intent, special method and computed property demonstrated; pure analytics key-independent. | Pending |
| P5.9a | Fix Finder/navigation defects and rerun component checks | Asier | Gabriel | P5.2-P5.8 | Reviewed fixes and check results for Finder/navigation; if no defect exists, record the actual no-defect verification rather than inventing a change. | Pending |
| P5.9b | Fix API/configuration/cache defects and rerun component checks | Gabriel | Alejandra | P5.2-P5.8 | Reviewed fixes and check results for API/configuration/cache; if no defect exists, record the actual no-defect verification rather than inventing a change. | Pending |
| P5.9c | Fix models/storage/catalog validation defects and rerun component checks | Alejandra | Christian | P5.2-P5.8 | Reviewed fixes and check results for models/storage/catalog validation; if no defect exists, record the actual no-defect verification rather than inventing a change. | Pending |
| P5.9d | Fix scoring/time-window logic defects and rerun component checks | Christian | Selin | P5.2-P5.8 | Reviewed fixes and check results for scoring/time-window logic; if no defect exists, record the actual no-defect verification rather than inventing a change. | Pending |
| P5.9e | Fix Dashboard/chart data defects and rerun component checks | Selin | Asier | P5.2-P5.8 | Reviewed fixes and check results for Dashboard/chart data; if no defect exists, record the actual no-defect verification rather than inventing a change. | Pending |
| P5.9 | Run regression checks on the five completed component fixes | Selin | Asier | P5.9a + P5.9b + P5.9c + P5.9d + P5.9e | Combined regression results recorded; required stubs and arithmetic placeholder test resolved; unused empty deliverable folders identified and removed in reviewed changes. | Pending |
| P5.10a | Demonstrate full user journey and storage-to-score handoff | Asier | Gabriel | P5.9 | Explain the complete application, demonstrate the assigned route through it, and answer the named reviewer's questions; record real evidence and gaps. | Pending |
| P5.10b | Demonstrate API failures plus how scores reach the two views | Gabriel | Alejandra | P5.9 | Explain the complete application, demonstrate the assigned route through it, and answer the named reviewer's questions; record real evidence and gaps. | Pending |
| P5.10c | Demonstrate persistence plus forecast-to-score behavior | Alejandra | Christian | P5.9 | Explain the complete application, demonstrate the assigned route through it, and answer the named reviewer's questions; record real evidence and gaps. | Pending |
| P5.10d | Demonstrate calculations plus retrieval/persistence behavior | Christian | Selin | P5.9 | Explain the complete application, demonstrate the assigned route through it, and answer the named reviewer's questions; record real evidence and gaps. | Pending |
| P5.10e | Demonstrate charts plus API errors and the scoring formula | Selin | Asier | P5.9 | Explain the complete application, demonstrate the assigned route through it, and answer the named reviewer's questions; record real evidence and gaps. | Pending |
| P5.10 | Compile the five walkthrough results and check unresolved knowledge gaps | Gabriel | Alejandra | P5.10a + P5.10b + P5.10c + P5.10d + P5.10e | Five actual demonstrations and peer questions recorded; unresolved answers assigned to the participant before phase closure. | Pending |

## Ten-point evidence matrix

| Criterion | Points | Required evidence | Lead / reviewer | Actual result |
| --- | --- | --- | --- | --- |
| OOP | 2 | Meaningful reusable inheritance; deliberate encapsulation; special method beyond init; computed property | Gabriel + Alejandra / Christian | Pending |
| API | 2 | Environment-loaded secret; distinct errors; partial batches; pre-request validation | Gabriel / Alejandra | Pending |
| Data and analytics | 2 | Real timestamped accumulated logs; three distinct analyses across two or more categories; real data calculations | Alejandra + Christian / Selin | Pending |
| Streamlit | 2 | Two views; meaningful selection; two correct labeled charts; usability | Asier + Selin / Gabriel | Pending |
| Repository and AI | 1 | Installable src package, README, no secrets; specific ongoing AI records and proper trailers | All / cross-review | Pending |
| Team | 1 | Genuine commits from five members and ability to explain all code | All / cross-review | Pending |

## Required adversarial cases

No eligible cities; selected mode unverified; empty/invalid preferences; min temperature above max; exact inclusive weather thresholds; fractional travel hours; five-hour cap; no complete daytime periods; one missing required field; stale/duplicated forecast batches; timezone/clock-change boundary; equal scores; changing sort before slicing; current log with zero/one/repeated timestamps; malformed responses; failure during persistence; local reruns without excess API calls; no secret in errors/logs/UI.

## Defect and walkthrough records

| Defect / question | Reproduction and impact | Owner | Fix / explanation | Independent recheck |
| --- | --- | --- | --- | --- |
| To record when observed | To fill | Component owner | Pending | Pending |

Fixture tests establish calculation correctness; real checks establish integration and provenance. Passing the inherited arithmetic placeholder is not functional evidence. Neither a planned reviewer nor this matrix proves an actual approval.


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

Record the review commit and begin P5.1; assign each found defect to its component owner rather than routing all fixes to Asier.
