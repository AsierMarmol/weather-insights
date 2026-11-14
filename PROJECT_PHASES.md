# Project phases

## Current checkpoint

**P4.5/P6.1 approved and merged; typing fixes and warning markers validated locally before P6.2.**
The [type-checking follow-up](PHASE5_QUALITY_REVIEW.md#type-checking-follow-up--14-november-2026) passes locally;
Alejandra reviews these changes before merge and the final P6.2 tests.
Gabriel approved [PR #21](https://github.com/AsierMarmol/weather-insights/pull/21) on 14 November 2026; it merged into dev
as `3444728`. Its files match audited feature commit `8b1210e` exactly.
[Phase 4](PHASE4_ANALYTICS_UI.md#p45-canva-inspired-executive-redesign)
summarizes the changes; [Phase 5](PHASE5_QUALITY_REVIEW.md#delivery-readiness-recheck--14-november-2026)
records the latest checks and limitations. [SCORING.md](SCORING.md) owns the
two-score model. [PROMPTS.md](PROMPTS.md#phase-4-extension-and-delivery-development-record)
preserves the development sequence. The PR #21 redesign is available on dev;
the typing and warning-marker follow-ups require Alejandra's review before merge.

| Phase | Outcome | Current state |
| --- | --- | --- |
| [1 — Setup](PHASE1_SETUP.md) | Environment, secure variables and GitHub workflow | Completed by Asier; historical record unchanged |
| [2 — Scope/data](PHASE2_SCOPE.md) | Catalog, product/API contracts and save-path proof | Foundation accepted; P4.5 specifications merged in PR #21 |
| [3 — Core](PHASE3_CORE_DATA.md) | Models/storage, reusable API/service, analytics | Original components accepted; redesign shares these components |
| [4 — Interface](PHASE4_ANALYTICS_UI.md) | Landing, Searcher and executive Dashboard | P4.1–P4.4 reviewed historically; P4.5 approved and merged in PR #21 |
| [5 — Quality](PHASE5_QUALITY_REVIEW.md) | Integrated tests, rubric and failure handling | P5.5 reviewed historically; current redesign evidence recorded separately |
| [6 — Delivery](PHASE6_DELIVERY.md) | Reviewed documentation, clean clone, submission | P6.1 approved and merged; P6.2 next; P6.3 pending |

## Next actions and owners

1. **P6.2: Gabriel and Alejandra, reviewed by Christian.** After the final
   documentation changes and any fixes are reviewed and merged, each clones
   the same reviewed dev commit into a fresh
   directory, follow README only, use a personal key, and record the exact
   commit, environment, tests/type checks/lint and agreed visual checks. Do not copy an
   existing environment or credentials. The [post-commit audit](PHASE5_QUALITY_REVIEW.md#post-commit-validation--14-november-2026)
   passed 523 tests with two Windows POSIX skips; it is supporting evidence,
   not independent P6.2 acceptance. No new phone/Mac result is claimed.
2. **P6.3: Asier, reviewed by Gabriel.** After P6.2, confirm data/source
   conditions, team understanding, instructor access and submission channel;
   then perform authorized dev → main publication and record submission.

Gabriel's PR #21 approval closes the integration review. It does not itself
document a new Mac or browser run. Dated earlier checks retain their scope.

## Original baseline history

These are previously recorded reviews, not a fresh GitHub status query:
foundation PR #3; core through #8; P2.5 #9; Searcher #10; Dashboard #11;
integration #12; model/storage #13; API #14; independent Dashboard #15;
analytics #17; chart acceptance #18; P5.5 #19 (then dev `2999dae`). P6.1
documentation was prepared/pushed before the redesign. The current P4.5/P6.1
update was subsequently approved and merged in PR #21, as recorded above.

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
