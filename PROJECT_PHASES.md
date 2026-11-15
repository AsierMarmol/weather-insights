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

1. **Christian:** acknowledge the combined [P6.2 evidence](PHASE6_DELIVERY.md#p62-final-code-live-save-and-acceptance-status--14-november-2026).
2. **Gabriel and Christian:** review the replacement `asier/feature` to `dev` pull request for the live-save evidence/data (`e46abec`) and consolidated delivery documentation. [PR #26](https://github.com/AsierMarmol/weather-insights/pull/26) was closed without merging; its commit and branch were preserved. Use the [open pull requests](https://github.com/AsierMarmol/weather-insights/pulls) for the current review.
3. **Asier, reviewed by Gabriel:** finish [P6.3](PHASE6_DELIVERY.md#p63-final-publication---asier-reviewed-by-gabriel) after acceptance and the reviewed merge into dev; confirm instructor access/channel and team understanding, publish reviewed main and record the submission.

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

| Information | Authoritative document |
| --- | --- |
| Installation, use and verification commands | [README.md](README.md) |
| Product scope, filters, shared objects and CSV schema | [Phase 2](PHASE2_SCOPE.md) |
| Exact formulas, ranking and displayed metric definitions | [SCORING.md](SCORING.md) |
| Provider identity, requests, pacing, cache and save/recovery | [API contract](WEATHER_API_CONTRACT.md) |
| Catalogue/data provenance and licences | [Reference notes](data/reference/README.md), [weather notes](data/weather/README.md) |
| Visual assets and attribution | [Asset credits](assets/README.md) |
| Component ownership and attribution | [TEAMROLES.MD](TEAMROLES.MD) |
| Implementation decisions and changes | Relevant phase's dated progress log |
| Automated validation and its limits | [Phase 5](PHASE5_QUALITY_REVIEW.md) |
| Acceptance, review and publication status | [Phase 6](PHASE6_DELIVERY.md) |
| Actual AI requests, results and decisions | [PROMPTS.md](PROMPTS.md) |

Link to the owning document instead of copying its complete rules. Short
summaries may explain a phase's dependencies. Keep dated evidence unchanged;
historical pending states and superseded formulas are not current instructions.
The instructor's assignment remains authoritative; plans alone are not proof
of completed functionality.

## Plan maintenance

When decisions change, update the owning specification and affected phases,
tests, documentation and acceptance gates together. Keep task IDs stable and
dated evidence truthful. Use Pending/Prepared, In progress, Awaiting review,
Blocked (with reason), Needs recheck or Done according to actual work. If a
change invalidates a completed check, name its owner and retain the old evidence.
Keep Phase 1 history intact; no separate change register is required.

Record substantial AI work with actual requester/tool in [PROMPTS.md](PROMPTS.md).
Assigned roles are not authorship evidence. Every member must make meaningful
contributions and explain the application. Reviews and publication need their
own evidence/authorization; automated tests are not instructor acceptance.

## Shared task workflow

Use the named task in its phase and the actual requester/tool. Read the task,
shared specification and prerequisite files first. Complete the whole deliverable
within its owned files using existing components. Keep secrets private and
synthetic inputs separate from genuine data. Run relevant checks and record
actual results, limitations and the next dependency in that phase. Update
affected plans when rules change and record substantial AI assistance accurately.
Do not invent teammate work or approval. Commit, push, review requests, merge
and submission require the relevant authorization; the task template alone
does not authorize publication.
