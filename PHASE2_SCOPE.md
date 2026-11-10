# Phase 2 - Ideation and Project Flexibility

Updated: 10 November 2026.

Use the same rhythm as Phase 1: complete one small step, check its finish condition, record the decision, and review it before moving on. This phase defines what the team will build and how much flexibility it has. Implementation belongs to the following phase.

## Current checkpoint

Draft plan prepared at Asier's request. No product idea, enrichment source, formula, responsibility assignment, or architecture option is approved by this draft. Start Step 1 after the Phase 1 review workflow and Asier's Step 17 confirmations are complete.

## Purpose and finish condition

Agree on a useful weather application that all five students understand, meets every instructor requirement, and fits the team's available time. Finish with a written minimum scope, optional enhancements, data/history plan, class responsibilities, analytical views, UI outline, acceptance checks, and five-person work plan.

Keep this file and subsequent phase plans at the repository root beside README.md and PHASE1_SETUP.md. The instructor's assignment README and supporting summary remain external reference documents supplied to the team; this plan summarizes their requirements without replacing them.

## Ordered checklist

| Step | Small action | Finish condition | Status |
| --- | --- | --- | --- |
| 1 | Confirm the Phase 1 handoff. | The setup PR is reviewed and merged into dev, reviewed dev is promoted to main, protection enforcement has been checked, and Asier has collected each teammate's starter-app and collaboration-rule confirmation. | Waiting for Phase 1 closure |
| 2 | Review the non-negotiable course requirements. | All five members agree that the rubric map below is the minimum delivery checklist; team preferences and optional tools are clearly separate. | Pending |
| 3 | Choose the target user and main question. | Write one sentence describing who uses the app, what weather decision it helps with, and why comparing locations or observations over time helps. Agree on two or three concrete user scenarios. | Pending |
| 4 | Check the available API data before choosing features. | Verify required OpenWeatherMap endpoints, account access, fields, units, timestamps, request limits, and error behavior against current official documentation. Record which ideas work with the team's actual access. Use personal local credentials; do not record keys. | Pending |
| 5 | Separate the minimum product from optional improvements. | List the required user actions and outputs, an explicit optional-feature list, and deferred ideas. Every required rubric item is covered by the minimum product without depending on optional enrichment. | Pending |
| 6 | Decide the observation and history contract. | Choose CSV or SQLite; agree on location identifiers, retrieval timestamps/time zones, fields/units, successful-fetch append behavior, and missing/duplicate observation handling. Schedule logging early in implementation so genuine history can accumulate and be committed for grading. | Pending |
| 7 | Agree on meaningful OOP responsibilities. | Describe the generic JSON API base class, OpenWeatherMap subclass, snapshot/model objects, and storage responsibilities. Identify deliberate public/protected/private state, a useful special method beyond __init__, and a genuinely computed property. Explain why inheritance is useful. | Pending |
| 8 | Specify the analytics and dashboard together. | Define at least three distinct analytical views spanning at least two of trend/comparison/derived metrics. For each, record its question, real-data inputs, formula or aggregation, units, empty-history behavior, and interpretation. Sketch at least two app views and two labeled charts with meaningful location interaction. | Pending |
| 9 | Decide whether to enrich the data. | Record an explicit yes/no/later decision using the enrichment rules below. Any selected extra source has verified access, provenance, usage conditions, joining logic, and a clear user benefit. The required core remains usable independently. | Pending |
| 10 | Assign five meaningful contributions and peer reviewers. | Agree on manageable responsibilities and interfaces for all five students, with a reviewer for each change. Include shared explanation/review time so every member can explain the whole application. | Pending |
| 11 | Define acceptance checks before implementation. | Write concrete success/failure checks for city validation, authentication, bad locations, timeouts/server failures, partial batch success, timestamped persistence, analytical correctness, app interactions, installation, secret protection, and AI attribution. | Pending |
| 12 | Review and record the agreed scope. | Resolve open decisions below and update this document through a reviewed PR. Keep selected behavior, deferred ideas, ownership, and reasons understandable to someone outside the team. | Pending |
| 13 | Close Phase 2 and order implementation work. | The five-person team can explain the scope and architecture, the minimum product maps to every rubric row, and the next implementation checklist prioritizes a real fetch-to-storage path early enough to collect history. | Pending |

## Minimum requirements and planning evidence

The assignment README is authoritative. The summary illustrates patterns; example formulas, class names, and tools are not additional course requirements.

| Course requirement | Decision/evidence needed in Phase 2 | Implementation later |
| --- | --- | --- |
| Meaningful inheritance | Explain generic JSON-request behavior and the provider-specific subclass; define their responsibilities and callers. | Reusable request handling and actual OpenWeatherMap integration. |
| Encapsulation, special method, computed property | Identify justified public/_protected/__private state, an operation beyond __init__, and a calculated value useful to the product. | Implement and exercise these choices without decorative classes or properties. |
| API robustness and input validation | Specify clear outcomes for invalid input, bad key, bad location, network/server failure, and partial multi-location success. | Validate before requesting; handle distinct failures without exposing credentials or crashing the whole batch. |
| Real timestamped history | Select a storage format, schema, timestamps, and append rules; start collection early. | Store genuine successful fetches over time and commit the accumulated data log for grading. |
| Three analytical views across at least two categories | Define questions and computations on real fetched/logged observations. | Correct calculations with meaningful trends, comparisons, or derived metrics. |
| At least two app views and two labeled charts | Sketch navigation, location interaction, chart inputs, units, and insufficient-history messages. | A usable interactive Streamlit app, rather than static headings. |
| Installable package, README, secret protection, AI records | Retain the existing src layout, pyproject, locked setup, local credentials, ongoing PROMPTS entries, and accurate attribution. | Keep clean-clone installation and documentation working as features are added. |
| Five-person collaboration and understanding | Assign real contributions, reviewers, and shared walkthroughs. | Meaningful human-authored commits and the ability to explain any part of the code. |

## Flexibility and data enrichment

The team can choose the audience, story, locations, visual design, storage option, analytical questions, and useful derived metrics while meeting the minimum requirements. Changing the theme must not remove the OpenWeatherMap foundation, meaningful OOP, genuine history, required analytics, interaction, or collaboration evidence.

Additional real data or calculated fields may be considered when they improve the agreed user scenarios. Before selecting a source, verify its current official documentation, access requirements, usage conditions/attribution, data coverage, units, timestamps, and how locations match. Record the source and transformation so observations remain traceable.

Keep original observations and derived values distinguishable. Document a custom index's formula, units, assumptions, and limits; do not present an invented score as an official meteorological or health measure. Extra historical datasets do not replace the assignment's requirement to log the app's own successful fetches over time.

Use real observations for the app and submitted history. Clearly identified fixtures are appropriate for deterministic tests; they must remain separate from the genuine observation log. Never manufacture weather history to make a trend appear complete.

## Decision record

Replace pending items with actual team decisions and reasons as each step is completed.

| Decision | Agreed choice | Reason / evidence |
| --- | --- | --- |
| Target user and main question | Pending | Step 3 |
| Minimum user scenarios | Pending | Steps 3 and 5 |
| Available API access and required fields | Pending verification | Step 4; link current official sources when checked |
| Required features and deferred ideas | Pending | Step 5 |
| Storage format and observation contract | Pending | Step 6 |
| Class responsibilities and interfaces | Pending | Step 7 |
| Three analytics and two chart definitions | Pending | Step 8 |
| Extra data: yes, no, or later | Pending | Step 9 |
| Five contributors and peer reviewers | Pending | Step 10 |
| Acceptance checks and implementation order | Pending | Steps 11 and 13 |

## Next action only

Finish the Phase 1 review workflow and Asier's teammate confirmations. Then begin Phase 2 Step 1 and review the requirements together before choosing the target user and product idea. This draft does not start feature development or declare either phase complete.
