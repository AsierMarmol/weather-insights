# Weather Insights - Project Phase Index

Updated: 11 November 2026.

## Selected project

The group decision is a local Streamlit weather getaway finder departing from Madrid for a curated 20-30-city mainland-Spain catalog. Users choose Car or Train, an activity style, the next 24/48/72 hours, and temperature/precipitation/wind preferences. Weather earns a score out of 100; one point per one-way reference travel hour is deducted, capped at five. Cloud cover is informational, not a scoring component.

Activity categories: Culture and sightseeing; Food and gastronomy; Coast and seaside; Nature and outdoor visits. Catalog entries can have several tags. Reference times are sourced, not live traffic/timetables or booking guarantees. Actual catalog entries and implementation details still require the Phase 2 review.

## Plans and current status

| Phase | Detailed plan | Current status | Outcome |
| --- | --- | --- | --- |
| 1 - Team and Environment Setup | [PHASE1_SETUP.md](PHASE1_SETUP.md) | Completed by Asier; retained as setup reference | Retained environment, package, credentials and collaboration workflow |
| 2 - Ideation and Project Flexibility | [PHASE2_SCOPE.md](PHASE2_SCOPE.md) | In progress: business choices agreed; technical/catalog review pending | Approved scope, sourced catalog rules, contracts and acceptance checks |
| 3 - Core Application and Data Collection | [PHASE3_CORE_DATA.md](PHASE3_CORE_DATA.md) | Not started | Meaningful OOP, real API retrieval, persistence and early genuine history |
| 4 - Analytics and Streamlit Interface | [PHASE4_ANALYTICS_UI.md](PHASE4_ANALYTICS_UI.md) | Not started | Shared ranking, Finder, Dashboard and three analyses |
| 5 - Integration and Quality Review | [PHASE5_QUALITY_REVIEW.md](PHASE5_QUALITY_REVIEW.md) | Not started | Verified required behavior and rubric evidence |
| 6 - Documentation and Final Delivery | [PHASE6_DELIVERY.md](PHASE6_DELIVERY.md) | Not started | Clean-clone local execution, real logs, accurate records and submission |

Team ownership, code boundaries, workload balancing and reviewer rotation: [TEAMROLES.MD](TEAMROLES.MD).

## Execution rules

Each phase has task IDs, owners, reviewers, dependencies and observable finish conditions. Complete prerequisites before dependent work, split large tasks, and update statuses only from actual evidence. Keep the teacher's assignment authoritative and the summary as supporting examples. No deadline is invented; progress as efficiently as dependencies allow, while genuine history accumulates over real elapsed time.

The product/scoring source of truth is Phase 2; role ownership is TEAMROLES.MD; the detailed phase files hold execution progress. Keep this index brief to avoid competing specifications. Code, tests, documentation and peer review are shared across all five members; substantive contributions and authorship remain accurate.

## Teacher requirements, repository structure and task coverage

Read-only structure audit: 11 November 2026. The authoritative assignment and supporting summary were compared with the actual repository. The required src package, pyproject, app entry point, root README, root PROMPTS and safe environment example exist. No empty directories were found in the application source/test tree. This confirms structure, not completed application behavior.

Current source status: client.py contains starter comments and a configuration import; models.py, storage.py and analytics.py contain starter comments; app.py has two heading-only views; tests/test_analytics.py contains only an arithmetic placeholder. __init__.py is empty, which is a legitimate package marker. No real history directory/dataset exists yet. These are expected at the current planning stage and must not be counted as implemented rubric evidence.

### Existing file responsibilities

| Path / artifact | Required purpose and present state | Implementation owner / tasks | Completion check |
| --- | --- | --- | --- |
| src/weather_app/ | Existing installable package directory; preserve modular boundaries | Asier writes file/interface map in P2.9; named module authors below | P5.1, P5.8, P6.8 |
| src/weather_app/__init__.py | Valid empty package marker; do not add artificial code just to fill it | Asier defines package interface; P2.9 | Package import in P6.8 |
| src/weather_app/client.py | Starter only; implement reusable JSON base and OpenWeather subclass | Gabriel; P3.2, P3.3, P3.10 | P5.3 and P5.8 |
| src/weather_app/config.py | Existing dotenv loading; currently raises at import if key missing. Preserve secure loading and make the application boundary handle missing configuration safely | Gabriel with Asier; P3.2, P4.4-P4.5 | P5.3, P6.3, P6.8; no secrets in UI/errors |
| src/weather_app/models.py | Starter comments; validated objects, deliberate encapsulation, useful special method and computed property | Alejandra; P3.1 | P5.8 and model tests |
| src/weather_app/storage.py | Starter comments; append/reload successful real current and forecast fetches, timestamps and write safety | Alejandra; P3.4-P3.6 | P5.5, P6.4 |
| src/weather_app/analytics.py | Starter comments; time coverage, positive weather checks, selected-mode travel deduction, ordering and explanation values | Christian; P3.8, P4.1-P4.3 | P5.4; known-answer and real-data checks |
| app.py and any agreed UI helpers | Currently heading-only starter; two connected interactive views, Finder plus Dashboard | Asier: P4.4-P4.6; Selin: P4.7-P4.9 | P5.6-P5.7; two labeled charts and three analyses |
| tests/ | Existing directory, but arithmetic test is not functional coverage. Replace it and add focused tests alongside implementation | Each component owner; P3/P4 task checks | P5.9; meaningful suite runs from clean clone in P6.8 |
| pyproject.toml, uv.lock, .python-version | Existing packaging and reproducible environment; retain, update only for justified needs | Relevant owner; Asier integrates; P3.8 if timezone dependency needed | P6.8 installed imports, tests and startup |
| .gitignore, variables.env.example | Existing exclusions and safe example; private variables.env must stay untracked. Real data must remain trackable | Gabriel; P3.2, P5.3 | P6.3, P6.7-P6.8 |
| README.md at repository root | Existing application instructions; update to actual implementation and relative data paths | P6.2-P6.6 section owners | P6.8 clean clone using this README only |
| PROMPTS.md at repository root | Existing eight-field collaboration convention; accurate implementation entries and named AI co-author trailers remain required | Each actual contributor during coding; P6.7 | Compare real work and Git history; no fabricated entries |
| Phase plans and TEAMROLES.MD | Team planning aids; keep owners, dependencies, status and evidence current | Task owners/reviewers; all phases | Plan maintenance procedure and phase gates |

Module names follow the supplied starter; the assignment requires an installable modular application, not arbitrary additional empty directories. UI helpers, extra tests, assets and data folders are created only when they have a real purpose and content.

### New artifacts to create during implementation

Paths below are proposals to settle in P2.5/P2.9, not folders that exist now.

| Proposed artifact | Owner / creation step | Required content before delivery |
| --- | --- | --- |
| data/reference/destinations.csv or agreed equivalent | Named batches P3.7a-e; Alejandra implements validation/merge in P3.7 | Approved 20-30-city catalog, coordinates, activities, sourced per-mode durations and verification metadata |
| data/history/ current and forecast files, or agreed SQLite database | Alejandra; P3.4-P3.6 | Actual accumulated records with retrieval/provider/forecast-valid times; not empty files, header-only CSVs or empty tables |
| Isolated test fixtures, if needed | Each component owner during P3/P4 | Known-answer examples clearly separated from real submitted logs; create a fixtures folder only when fixtures exist |
| UI modules or assets, if used | Asier/Selin; P4.4-P4.10 | Actual imported UI helpers or used licensed assets with credits; no unused scaffolding |

Git does not preserve empty directories. Do not use .gitkeep or fake records to make an unfinished data directory look complete. A small genuine collection can be started early, then grows through actual use. Data amount/coverage and limitations must be reported honestly.

### Requirement-to-step cross-check

| Teacher requirement | Implementation / preparation tasks | Independent check and delivery evidence |
| --- | --- | --- |
| Generic JSON API inheritance | P3.2-P3.3 | P5.8 |
| Deliberate public/protected/private conventions | P3.1-P3.3 | P5.8 |
| Special method beyond init and computed property | P3.1 | P5.8 |
| dotenv key, never hardcoded/committed/displayed | Retained setup; P3.2, P4.4 | P5.3, P6.3, P6.7 |
| Distinct input/key/location/network/server errors; no bare except | P3.2-P3.3, P4.4-P4.5 | P5.3, P5.7 |
| Multi-location partial success and validation before API call | P3.1-P3.3, P3.11 | P5.3, P5.7 |
| Every successful fetch logged with timestamps; real accumulated dataset committed | P3.4-P3.6 | P5.5, P6.4, P6.8-P6.9 |
| Three distinct analyses spanning at least two categories | P4.1-P4.3, P4.7-P4.8 | P5.4-P5.6 |
| Analytics use genuine fetched/logged data | P3.5-P3.6, P4.5-P4.8 | P5.5-P5.6 |
| Two app views, meaningful location interaction, two labeled charts and usability | P4.4-P4.10 | P5.6-P5.7, P6.8 |
| Installable src package, pyproject and working application README | Existing setup; P2.9, P6.2-P6.6 | P6.8 |
| Ongoing specific AI log and appropriate co-author trailers | Each implementation task; P6.7 | Actual records/history audit before publication |
| Real contributions from every member and whole-project understanding | TEAMROLES and every owned task | P5.10, P6.7 |
| Accessible repository URL and correct submission channel | P6.1, P6.9-P6.10 | Recorded final commit/access and actual submission receipt |

The teacher's summary provides illustrative classes, formulas and folder names. Its examples are not mandatory product formulas or extra features. The starter app's TODO suggests history charts; the authoritative assignment permits charts from real data. Our comparison chart plus genuine-history chart meet the planned requirement, subject to correct implementation.

### Final folder and placeholder policy

P5.1 inventories the deliverable tree; P5.9 removes unused scaffolding and resolves required-feature TODOs/stubs; P6.8 checks the actual clean clone. Empty __init__.py files may remain as intentional package markers. Optional placeholders may remain only if clearly outside the delivered feature set and not misleading. Required source modules, tests and datasets must perform their actual purpose.

.venv, .git, .pytest_cache, __pycache__ and generated egg-info are local tooling/environment artifacts, not course feature folders to populate. The README inside .pytest_cache is generated pytest documentation and must not replace the repository-root README. These directories should not be edited to satisfy the assignment; continue ignoring generated artifacts and private credentials.

## Plan maintenance

1. Before starting a row, the owner records the exact input/prerequisite, expected output and files, reviewer, acceptance checks and effort estimate. Split large rows into stable child task IDs when needed. The tables are an ordered work plan, not a promise that every future implementation detail is already known.
2. When a decision, API constraint, source, schema, interface, formula or assignment changes, record the old/new choice and reason. Review all six phases for impact; update affected rows and their downstream dependencies before proceeding.
3. Update the authoritative product contract in Phase 2 and owner/reviewer assignments in TEAMROLES.MD as needed. Update diagrams/examples, expected calculations, data migration procedure, README and delivery checks if affected. Preserve collected data and past evidence rather than overwriting history.
4. Mark invalidated completed checks Needs recheck, assign an owner and specify the required rerun. The peer reviewer checks that documentation, tests and implementation agree. Phase 1 stays closed unless a concrete setup change requires a targeted recheck.
5. Record evidence and update the current checkpoint/next action after each completed task. A plan change is not proof of implementation or review. No automatic commits, pushes, merges or fabricated attribution follow from this procedure.

| Change date | Reason and old/new decision | Affected task IDs / files | Owner / reviewer | Recheck and evidence |
| --- | --- | --- | --- | --- |
| 11 November 2026 | Planning audit: preserve Asier's completed setup; make verified seed, safe early collection, configuration/startup and cross-phase maintenance explicit | Phase 1; P2.2, P2.5, P2.10; P3.5, P3.6, P3.8, P3.10; P4.4; P6.8; all plans and TEAMROLES | Codex documentation edit requested by Asier; human review pending | Plan structure/dependencies checked; application checks remain pending |

Structure alignment audit also mapped each inherited module and future data artifact to named tasks and final checks. No application functionality was claimed or implemented by this audit.

## Planning validation checkpoint

The six rubric areas are mapped to owners, planned checks and delivery evidence. Phase 2 deliberately contains unresolved source/contract choices, each with an owner and a gate before dependent implementation. The catalog, journey-time evidence, actual account access, storage choice and collection schedule must be verified; this audit does not approve them or promise issue-free execution.

## Next step

Current checkpoint: Phase 1 complete; P2.1 scope/rubric checklist and unresolved-decision register prepared in PHASE2_SCOPE.md. Document checks passed; Gabriel's peer review is pending. Phases 3-6 have not started.

| Order | Task and tangible output | Owner | Reviewer / participation |
| --- | --- | --- | --- |
| Next | P2.1 deliverable prepared: check the scope/rubric mapping and unresolved proposals, then record actual review | Gabriel performs the review | Asier addresses any requested corrections |
| After P2.1 review, parallel | P2.2: produce a reviewable 20-30-city shortlist, assign 4-6 research entries per member and identify 3-5 seed candidates | Alejandra writes the numbered shortlist | Christian reviews; P3.7a-e name the subsequent batch authors |
| After P2.1 review, parallel | P2.3: verify API access, fields/units and request constraints with a safe small check | Gabriel | Alejandra reviews |
| After shortlist | P2.4: settle sourced car/train reference conventions and activity evidence | Selin writes activity rules in P2.4a; Gabriel writes travel rules in P2.4 | Asier reviews activity rules; Alejandra reviews travel rules |

Christian then leads scoring/window acceptance examples after the data contract is agreed; Asier and Selin define Finder and Dashboard behavior against those contracts. Do not mark team agreement or API/source verification complete merely because these plans exist.

## Concrete ownership update - 11 November 2026

Each actionable phase row now has one named author, one different reviewer and a specific artifact/finish condition. Catalog verification, component fixes, individual walkthroughs and contribution checks have named child tasks. Read dependencies rather than assuming document row order: a parent is complete only when its listed children and checks are complete. Phase 1 remains Asier's completed setup. This replaces vague coordinator/group assignments; it does not claim implementation or approval.
