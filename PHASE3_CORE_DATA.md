# Phase 3 - Core Application and Data Collection

Updated: 11 November 2026.

## Current checkpoint

Not started; implementation follows the Phase 2 contract review. These are planning instructions, not evidence that features, data verification, or peer reviews are complete.

## Purpose and finish condition

Build a reliable API-to-storage path first, start real history, and then complete the core services for the reviewed catalog.

**Entry condition:** P2 contracts and acceptance examples are agreed; a small verified catalog subset is available.

**Finish condition:** Current and forecast fetches work across the approved catalog with partial failures, persistent genuine logs, safe reuse and validated interfaces.

The instructor assignment README in the parent folder is authoritative; its summary is a supporting reference, not an additional specification. The selected product and scoring contract live in [PHASE2_SCOPE.md](PHASE2_SCOPE.md). Roles and workload rules live in [TEAMROLES.MD](TEAMROLES.MD); navigation is in [PROJECT_PHASES.md](PROJECT_PHASES.md).

## Ordered checklist

Work in dependency order. Independent tasks can proceed together after their shared interfaces are agreed. Owners implement their tasks and checks; reviewers verify the actual changes. Pending means not yet demonstrated.

| ID | Small action | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P3.1 | Implement validated domain and catalog models | Alejandra | Christian | P2.5 | Typed/validated fields, meaningful repr/property and justified encapsulation; focused model tests. | Pending |
| P3.2 | Implement generic JSON API request behavior | Gabriel | Alejandra | P2.3 + P2.9 | Reusable base, timeout/status/JSON handling, injectable configuration, safe errors and tests. | Pending |
| P3.3 | Implement OpenWeather current/forecast mapping | Gabriel | Alejandra | P3.1 + P3.2 | Provider subclass returns normalized current/forecast objects, distinct errors and partial batch results. | Pending |
| P3.4 | Implement append/reload persistence | Alejandra | Christian | P3.1 + P2.5 | Successful fresh-fetch records retain retrieval/provider/valid times; fixtures isolated; write protection tested. | Pending |
| P3.5 | Implement the first real API-to-storage orchestration | Asier | Gabriel | P3.3 + P3.4 | Real current and forecast records save/reload for the verified seed without exposing secrets; use the agreed request budget and conservative manual pacing before automated controls exist. | Pending |
| P3.6 | Implement and run repeatable genuine collection | Alejandra | Christian | P3.5 | Executable collection procedure, schedule, request budget and append/reload checks recorded; Alejandra runs the initial agreed collection and records real results. | Pending |
| P3.7a | Produce verified catalog batch 1 | Asier | Gabriel | P2.4 + P2.5 + P3.1 | Complete all reference fields and source dates for candidate IDs assigned to batch 1; run the shared validator and hand the reviewed batch to Alejandra. | Pending |
| P3.7b | Produce verified catalog batch 2 | Gabriel | Alejandra | P2.4 + P2.5 + P3.1 | Complete all reference fields and source dates for candidate IDs assigned to batch 2; run the shared validator and hand the reviewed batch to Alejandra. | Pending |
| P3.7c | Produce verified catalog batch 3 | Alejandra | Christian | P2.4 + P2.5 + P3.1 | Complete all reference fields and source dates for candidate IDs assigned to batch 3; run the shared validator and hand the reviewed batch to Alejandra. | Pending |
| P3.7d | Produce verified catalog batch 4 | Christian | Selin | P2.4 + P2.5 + P3.1 | Complete all reference fields and source dates for candidate IDs assigned to batch 4; run the shared validator and hand the reviewed batch to Alejandra. | Pending |
| P3.7e | Produce verified catalog batch 5 | Selin | Asier | P2.4 + P2.5 + P3.1 | Complete all reference fields and source dates for candidate IDs assigned to batch 5; run the shared validator and hand the reviewed batch to Alejandra. | Pending |
| P3.7 | Validate and combine the five verified catalog batches | Alejandra | Christian | P3.1 + P3.7a + P3.7b + P3.7c + P3.7d + P3.7e | Catalog validator runs on all five delivered batches; merged dataset, coverage report and rejected records are explicit. | Pending |
| P3.8 | Implement pure units/time/coverage helpers | Christian | Selin | P3.1 + P2.6 | Common window, named time zones and expected daytime samples pass boundary/missing-data checks; timezone data availability on clean Windows is checked and dependencies updated only if needed. | Pending |
| P3.9 | Implement history-to-chart data adapter | Selin | Asier | P3.4 | Reloaded current observations are sorted and deduplicated for analysis; predictions never appear as observations. | Pending |
| P3.10 | Add pacing, bounded retries and reusable cache | Gabriel | Alejandra | P3.3 + P3.5 | Budget/freshness policies implemented; credential failures do not trigger endless retries; cache hits do not append fake fetches; cache reuse does not bypass credential validation or retain secret-bearing URLs. | Pending |
| P3.11 | Connect shared collection orchestration | Asier | Gabriel | P3.7-P3.10 | Selected-city collection reports progress, age and failures; immutable analysis inputs available to both views. | Pending |
| P3.12 | Run core integration checks and write the Phase 4 handoff report | Selin | Asier | P3.6 + P3.11 | Implemented core modules and meaningful API/model/storage tests reviewed; real collection evidence and catalog gaps explicit; remaining analytics/UI placeholders assigned to Phase 4. | Pending |

## Collection and persistence checklist

Record the approved file/database paths, schema version, normalized units, UTC timestamp meanings, fetch/batch IDs, duplicate rules, write safety and recovery behavior. Prefer portable relative paths under the repository. Do not blanket-ignore the submitted genuine dataset.

Each collector uses their own local credential setup and agreed procedure; never distribute a secret file. Partition collection by city/time or use a designated collector to avoid overlapping writes. Reconcile schema and provenance before merging contributed data. Alejandra implements integrity validation and writes the combined dataset; each named batch author corrects rejected records in their own batch.

Keep every successful fresh fetch as a fetch event. Analytical deduplication happens downstream and must not erase the audit of actual requests. A failed persistence operation needs a clear error rather than a false success. Saved forecasts remain predictions even after their valid times pass.

## Core acceptance cases

| Area | Required check |
| --- | --- |
| Input | Invalid coordinates, empty/invalid values and malformed catalog records rejected before requests |
| API | Bad credentials, bad location, timeout, server/rate-limit and malformed payload produce distinct safe results |
| Batch | One location failure leaves other valid results usable; account-wide auth failure is reported clearly |
| Data | Current/forecast separation, append/reload, missing values, duplicate events, overlapping writes and corruption handling |
| Reuse | Cache redisplay is not a fetch; stale data and refresh boundaries are explicit |
| History | Real collected observations demonstrably accumulate; fixture records never enter that log |

Live account access and limits must be verified during implementation; the plan does not assert a successful API call. Do not change dependencies until justified by the chosen contract.


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

Start P3.1 and P3.2 after the contract gate. Prioritize P3.5-P3.6 over complete catalog polish so observation history can accumulate.
