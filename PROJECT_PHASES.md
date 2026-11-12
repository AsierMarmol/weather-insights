# Project phases

## Current checkpoint

Phase 1 is completed by Asier. Phase 2 foundations were reviewed in PR #3. Core models/storage, API/service and analytics are reviewed and merged through PR #8. P2.5 was approved by Gabriel and Christian and merged in PR #9. P4.1 Searcher was approved by Gabriel and merged in PR #10. P4.2 Dashboard was approved by Asier and merged in PR #11. P4.3 integration is implemented locally and awaits Gabriel review; Phases 5-6 remain pending.

| Phase | Outcome | Status |
| --- | --- | --- |
| [1 - Setup](PHASE1_SETUP.md) | Environment, package, credentials and GitHub collaboration | Completed; historical record retained |
| [2 - Scope and data](PHASE2_SCOPE.md) | Product rules, catalog, API rules and shared specification | Foundation and P2.5 approved/merged |
| [3 - Core data](PHASE3_CORE_DATA.md) | Models/storage, reusable API/service, analytics | Core accepted for Phase 4; final integration checks in Phase 5 |
| [4 - Interface](PHASE4_ANALYTICS_UI.md) | Searcher, Dashboard and connected user journey | P4.1/P4.2 approved and merged; P4.3 implemented, awaiting Gabriel review |
| [5 - Quality](PHASE5_QUALITY_REVIEW.md) | Integrated acceptance and rubric evidence | Not started |
| [6 - Delivery](PHASE6_DELIVERY.md) | Documentation, clean-clone verification and submission | Not started |

## Work order

Review P2.1-P2.4 -> implement P3.1/P3.2/P3.3 -> Asier verifies the shared save path in P2.5 -> integrate P4 -> verify P5 -> deliver P6. P3.2 uses P3.1; P3.3 can start with synthetic unit-test inputs but needs normalized real data for integration. Selin can prepare UI against the specified result shape. P2.5 does not block implementation of the components it checks.

Each broad deliverable has one implementation owner, including tests/docs/fixes, and a separate reviewer. [TEAMROLES.MD](TEAMROLES.MD) owns assignments. [Phase 2](PHASE2_SCOPE.md) owns product rules/schema/examples. [WEATHER_API_CONTRACT.md](WEATHER_API_CONTRACT.md) owns provider mapping. [README.md](README.md) owns installation/run instructions. Keep each rule in its owning document and link to it.

## Plan maintenance

Use the active phase's task table, prompt and progress log. Before marking Done, record actual files, checks and reviewer outcome. Prepared is not approved; assigned ownership is not authorship. Use Pending, In progress, Awaiting review, Done, or Needs recheck with a reason.

When a decision changes, update its owning specification and affected phase dependencies/acceptance checks together. Keep IDs stable and meaningful past results; mark invalidated checks Needs recheck. Put the change and affected task IDs in the active phase's progress log rather than a separate change register. Future components remain pending until implemented. Keep Phase 1's completed history intact.

Substantial AI assistance is recorded truthfully in [PROMPTS.md](PROMPTS.md); organizational file movements do not need new entries. Each member uses their actual identity/tool and understands their contribution and the whole app. Follow personal branch -> reviewed dev -> reviewed main. Commits, pushes and merges require authorization; review assignments do not send requests automatically.

## Next action

Gabriel reviews P4.3 integration. After acceptance, Alejandra, Gabriel, Christian and Selin perform their Phase 5 component checks, followed by Asier’s integrated rubric walkthrough. The rubric mapping is in Phase 2 and final acceptance is in Phase 5. Saved observations/forecasts must accumulate through normal use and be submitted; no continuous collection process or historical-trend chart is required.
