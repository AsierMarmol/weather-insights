# Project phases

## Current checkpoint

**Current dev: `83cc7f9`; implementation reviewed, final live-save check passed.**
PR #23 was approved by Alejandra and merged. PR #24 retains her earlier
clean-clone report; Gabriel's final-code report in PR #25 was approved by
Christian. The group accepts that later coverage without requiring another
complete Alejandra rerun. Christian's acknowledgement of her earlier report
remains pending. [Phase 6](PHASE6_DELIVERY.md#p62-final-code-live-save-and-acceptance-status--14-november-2026) owns current acceptance details;
[Phase 5](PHASE5_QUALITY_REVIEW.md) owns automated evidence and limitations.
[SCORING.md](SCORING.md) remains the two-score specification.

| Phase | Outcome | Current state |
| --- | --- | --- |
| [1 — Setup](PHASE1_SETUP.md) | Environment, secure variables and GitHub workflow | Completed by Asier; historical record unchanged |
| [2 — Scope/data](PHASE2_SCOPE.md) | Catalog, product/API contracts and save-path proof | Foundation accepted; P4.5 specifications merged in PR #21 |
| [3 — Core](PHASE3_CORE_DATA.md) | Models/storage, reusable API/service, analytics | Original components accepted; redesign shares these components |
| [4 — Interface](PHASE4_ANALYTICS_UI.md) | Landing, Searcher and executive Dashboard | P4.1–P4.4 reviewed historically; P4.5 approved and merged in PR #21 |
| [5 — Quality](PHASE5_QUALITY_REVIEW.md) | Integrated tests, rubric and failure handling | P5.5 reviewed historically; current redesign evidence recorded separately |
| [6 — Delivery](PHASE6_DELIVERY.md) | Reviewed documentation, clean clone, submission | P6.1 merged; P6.2 technical evidence recorded, acknowledgement pending; P6.3 pending |

## Next actions and owners

1. **Christian:** acknowledge Alejandra's earlier report and the combined
   [P6.2 evidence](PHASE6_DELIVERY.md#p62-final-code-live-save-and-acceptance-status--14-november-2026); his PR #25 approval already covers Gabriel's report.
2. **Asier:** review/commit the local live-check records and status updates,
   obtain review/merge, then complete P6.3 with Gabriel reviewing. Confirm
   instructor access/channel and team understanding; publish reviewed dev
   to main and record the real submission. Main is still the starter version.

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
