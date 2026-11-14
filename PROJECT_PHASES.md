# Project phases

## Current checkpoint

**P6.1: application and documentation prepared on asier/feature for review into dev; Gabriel approval pending.**
P4.5 checkpoint 6 local validation is complete, and the requester confirmed
final preview review on 14 November 2026. The P4.5 development update is
awaiting peer approval and merge into dev.
[Phase 4](PHASE4_ANALYTICS_UI.md#p45-canva-inspired-executive-redesign)
summarizes the adopted changes and why; [Phase 5](PHASE5_QUALITY_REVIEW.md#checkpoint-6-validation--13-november-2026)
records test/visual evidence and limitations. [SCORING.md](SCORING.md) owns the
current two-score model. [PROMPTS.md](PROMPTS.md#phase-4-extension-and-delivery-development-record)
records the detailed Canva-to-Streamlit development sequence and its decisions.
Until the PR is merged, a dev pull does not contain this feature update.

| Phase | Outcome | Current state |
| --- | --- | --- |
| [1 — Setup](PHASE1_SETUP.md) | Environment, secure variables and GitHub workflow | Completed by Asier; historical record unchanged |
| [2 — Scope/data](PHASE2_SCOPE.md) | Catalog, product/API contracts and save-path proof | Foundation accepted; P4.5 specifications updated locally |
| [3 — Core](PHASE3_CORE_DATA.md) | Models/storage, reusable API/service, analytics | Original components accepted; redesign shares these components |
| [4 — Interface](PHASE4_ANALYTICS_UI.md) | Landing, Searcher and executive Dashboard | P4.1–P4.4 reviewed historically; P4.5 local validation/review |
| [5 — Quality](PHASE5_QUALITY_REVIEW.md) | Integrated tests, rubric and failure handling | P5.5 reviewed historically; current redesign evidence recorded separately |
| [6 — Delivery](PHASE6_DELIVERY.md) | Reviewed documentation, clean clone, submission | P6.1 documentation prepared; peer review pending; P6.2/P6.3 pending |

## Next actions and owners

1. Final preview review confirmed by Asier on 14 November. P6.1 documentation
   is prepared; complete Gabriel's review. The [latest audit](PHASE5_QUALITY_REVIEW.md#feature-integration-validation--14-november-2026)
   has 523 passed and two POSIX skips in 82.90 seconds in the main-project
   environment after integration; lint and dependency checks passed.
   Earlier installation/build checks are retained as dated evidence. Rendered VS Code
   preview evidence is dated 13 November, not repeated by the 14 November audit.
   Proposed specialist reviews: Christian (scores/data), Selin (UI), Gabriel
   (integration). Phone/Mac checks are outside this audit by user instruction; no results
   on those platforms are claimed.
2. After explicit authorization, publish coherent reviewed changes through the
   protected feature → dev workflow. Preserve actual authorship and AI records.
3. **P6.2: Selin, reviewed by Christian.** Fresh clone of the agreed reviewed
   commit; follow README only, run tests/lint, use a personal key and record
   desktop/phone behaviour. No copied environment or credentials.
4. **P6.3: Asier, reviewed by Gabriel.** Confirm data/source conditions,
   contribution/understanding, instructor access and submission channel; then
   authorized dev → main publication and actual submission receipt.

## Original baseline history

These are previously recorded reviews, not a fresh GitHub status query:
foundation PR #3; core through #8; P2.5 #9; Searcher #10; Dashboard #11;
integration #12; model/storage #13; API #14; independent Dashboard #15;
analytics #17; chart acceptance #18; P5.5 #19 (then dev `2999dae`). P6.1
documentation was prepared/pushed before the local redesign. Its current
adoption/review state must be checked when publication resumes.

## Dependencies and document ownership

Phase 2 foundations → Phase 3 models/store → API/service → analytics → Phase 4
UI → Phase 5 integration → Phase 6 delivery. P2.5 verifies Phase 3's save path;
it does not block constructing that path. One owner builds a complete component
with tests/docs/fixes; another reviews it. [TEAMROLES.MD](TEAMROLES.MD) records roles.

README owns installation/use; Phase 2 owns product/schema; SCORING owns exact
calculation rules; WEATHER_API_CONTRACT owns provider/save rules; data READMEs
own provenance; phases own progress/evidence. Link rather than duplicate rules.

## Plan maintenance

When decisions change, update the owning specification and affected phases,
tests, documentation and acceptance gates together. Keep task IDs stable and
dated evidence truthful. Mark Prepared, In progress, Awaiting review, Done or
Needs recheck based on actual work, not intention. Keep Phase 1 history intact.

Record substantial AI work with actual requester/tool in [PROMPTS.md](PROMPTS.md).
Assigned roles are not authorship evidence. Every member must make meaningful
contributions and explain the application. Reviews and publication need their
own evidence/authorization; automated tests are not instructor acceptance.
