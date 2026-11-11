# Team Roles and Concrete Handoffs

Updated: 11 November 2026.

## Assignment rule

Each task has one named person who produces a concrete artifact and one different person who reviews it. No task is assigned to "everyone", a "coordinator", or an unspecified group. Members build on reviewed models, interfaces, data and code delivered by the preceding tasks. Activities that involve five people are split into five named subtasks.

Phase 1 setup was completed by Asier. The assignments below apply to future work and do not change setup authorship. Assignments are not claims that code, source verification or review is already complete.

## Coding roles

| Member / branch | Code they implement | Checks they write and run | Deliverable used next by | Reviewer |
| --- | --- | --- | --- | --- |
| Asier / asier/feature | Application orchestration, Finder controls/cards, navigation and shared result state | Input/UI interaction and complete user-journey checks | Selin consumes shared results; Gabriel reviews integration | Gabriel |
| Gabriel / gabrielstec/feature | Generic JSON API base, OpenWeather subclass, configuration boundary, safe errors, retries/pacing/cache | API failures, partial batches, secret protection and refresh behavior | Asier calls the client; Alejandra persists returned models | Alejandra |
| Alejandra / Alejandra/feature | Domain models, catalog validator, append/reload storage and collection command | Schema/unit/timestamp, data integrity, duplicate and write-safety checks | Gabriel maps responses to models; Christian and Selin consume stored records | Christian |
| Christian / christian/feature | Coverage/time helpers, weather scoring, selected-mode travel penalty, ranking and explanation values | Known-answer, unit, boundary, incomplete-data and ordering checks | Asier and Selin display the same analytical results | Selin |
| Selin / selin/feature | History-to-chart adapter, Dashboard filters/charts, score breakdown and presentation | Chart-data correctness, history behavior, ranking parity and clean-clone checks | Asier integrates Dashboard navigation; final users compare results | Asier |

Each author updates the documentation for their component and the actual implementation AI record. Record real contributions and preserve truthful human/AI attribution. Receiving completed code does not establish authorship; any reassignment must specify genuine new implementation or improvement work.

## Named reference-data batches

Alejandra creates a stable numbered 20-30-city candidate list in P2.2. The following deterministic allocation assigns every candidate without a vague shared research task. If the list changes, keep IDs stable and explicitly assign any new ID. Each record includes coordinates, named time zone, tourism/activity evidence, sourced one-way car/train reference durations, endpoints/conventions, verification date, and explicit unknown/unavailable fields. Missing train information must not be invented.

| Task | Author | Candidate IDs from the approved numbered list | Artifact | Reviewer |
| --- | --- | --- | --- | --- |
| P3.7a | Asier | 1, 6, 11, 16, 21, 26 when present | Verified batch 1, 4-6 records | Gabriel |
| P3.7b | Gabriel | 2, 7, 12, 17, 22, 27 when present | Verified batch 2, 4-6 records | Alejandra |
| P3.7c | Alejandra | 3, 8, 13, 18, 23, 28 when present | Verified batch 3, 4-6 records | Christian |
| P3.7d | Christian | 4, 9, 14, 19, 24, 29 when present | Verified batch 4, 4-6 records | Selin |
| P3.7e | Selin | 5, 10, 15, 20, 25, 30 when present | Verified batch 5, 4-6 records | Asier |

Alejandra implements the validator and combines those reviewed artifacts in P3.7. Each author fixes their own rejected records. P2.2a verifies a small seed first; subsequent batch tasks reuse those verified records rather than repeating the research. Alejandra implements and runs the initial collection procedure in P3.6; this is data/software work, not delegation.

## What each person produces in each phase

| Member | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 |
| --- | --- | --- | --- | --- | --- |
| Asier | Scope/rubric checklist, Finder sketch, exact interface/file map | API-to-storage runner, shared orchestration, reference batch 1 | Finder/navigation and connected user journey | End-to-end results, Finder fixes, individual walkthrough | Run guide, release PR and submission receipt |
| Gabriel | Verified API field/access report and car/train source conventions | Client/config/reliability code and tests, reference batch 2 | Review Finder/client integration; implement any named API follow-up | API/security/OOP evidence, API fixes, individual walkthrough and combined walkthrough report | API troubleshooting and own contribution record |
| Alejandra | Numbered candidate catalog, verified seed, model/storage specification | Models, persistence, validator, collection, reference batch 3 and combined catalog | Deliver corrected data/history interfaces when checks reveal issues | Catalog/history audits, storage fixes and individual walkthrough | Real-data export, dictionary/sources and own contribution record |
| Christian | Scoring/window contract and hand-computed acceptance cases | Pure unit/time helpers and reference batch 4 | Scoring, ranking and explanation implementation | Calculation checks, scoring fixes and individual walkthrough | Scoring guide, own record and combined contribution audit |
| Selin | Activity-tag source rules, Dashboard specification and scope-readiness checklist | History adapter, reference batch 5 and core handoff verification | Dashboard/charts and parity checks | Usability evidence, chart fixes, combined regression and individual walkthrough | Dashboard guide, clean-clone report and own contribution record |

## Dependency handoffs

1. Asier writes the scope/rubric checklist; Gabriel reviews it. Alejandra then produces the candidate list while Gabriel verifies weather access/fields.
2. Selin writes activity-source rules; Gabriel adds travel-time conventions. Alejandra uses those inputs for schemas and seed records.
3. Christian uses the schema and API fields to write scoring/time examples. Asier and Selin use those examples to specify Finder and Dashboard.
4. Alejandra implements models; Gabriel maps API data into them and Alejandra implements storage. Asier connects the actual fetch-to-storage flow.
5. Christian supplies tested scoring outputs. Asier consumes them in Finder; Selin consumes the same outputs and Alejandra's history records in Dashboard.
6. Named P5.9a-e tasks produce component fixes; Selin runs the combined regression checks. Named P5.10a-e tasks produce actual walkthrough evidence; Gabriel checks the combined results.
7. Named P6.7a-e tasks supply truthful contribution records; Christian checks them against actual history. Selin performs the clean clone; Asier prepares the reviewed release and submits it.

Independent tasks can proceed in parallel once their prerequisites exist. Building on each other does not require one person to wait for unrelated work. Split large tasks into a concrete child deliverable with one author and reviewer; do not solve overload by assigning it to "everyone". Rebalance using observed effort, not equal commit counts. If a reviewer co-authored the change, name a different independent reviewer.

## Changes and task evidence

The author updates affected phase steps, contracts, tests and documentation. The named reviewer checks cross-phase consistency under the maintenance procedure in PROJECT_PHASES.md. Preserve task IDs, actual evidence and earlier history; mark invalidated checks Needs recheck. No automatic commit/push/merge follows from this plan.

| Task ID | Concrete artifact and affected files | Actual author | Reviewer | Checks / PR | Status |
| --- | --- | --- | --- | --- | --- |
| Fill at task start | Fill before implementation | One named member | One different member | Actual evidence only | Pending |
