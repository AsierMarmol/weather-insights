# Phase 6 - Documentation and Final Delivery

Updated: 11 November 2026.

## Current checkpoint

Not started; no deadline was provided, so work follows dependencies rather than invented dates. These are planning instructions, not evidence that features, data verification, or peer reviews are complete.

## Purpose and finish condition

Deliver a reproducible local application with accurate documentation, genuine data, peer-reviewed work and a verified submission.

**Entry condition:** Phase 5 evidence is complete and blocking defects are resolved.

**Finish condition:** The final reviewed repository installs/runs from a clean clone, includes required real history and collaboration records, is accessible to the instructor and has actual submission evidence.

The instructor assignment README in the parent folder is authoritative; its summary is a supporting reference, not an additional specification. The selected product and scoring contract live in [PHASE2_SCOPE.md](PHASE2_SCOPE.md). Roles and workload rules live in [TEAMROLES.MD](TEAMROLES.MD); navigation is in [PROJECT_PHASES.md](PROJECT_PHASES.md).

## Ordered checklist

Work in dependency order. Independent tasks can proceed together after their shared interfaces are agreed. Owners implement their tasks and checks; reviewers verify the actual changes. Pending means not yet demonstrated.

| ID | Small action | Owner | Reviewer | Depends on | Finish condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P6.1 | Confirm submission channel and final requirements | Asier | Gabriel | Phase 5 | Instructor deadline/channel/access and required artifacts confirmed; do not invent a deadline. | Pending |
| P6.2 | Finalize usage and Finder instructions | Asier | Gabriel | P6.1 | README accurately covers local setup, controls, car/train references, current capabilities and limitations. | Pending |
| P6.3 | Finalize API configuration and troubleshooting | Gabriel | Alejandra | P6.1 | Own-key setup, refresh limits and distinct error guidance work without exposing credentials. | Pending |
| P6.4 | Produce the final documented reference catalog and genuine-history export | Alejandra | Christian | P6.1 | Reviewed batches and real accumulated records packaged with schema and source documentation; fixtures remain separate. | Pending |
| P6.5 | Finalize scoring explanation and examples | Christian | Selin | P6.1 | Three positive weather components and capped travel deduction accurately explained, including limitations. | Pending |
| P6.6 | Finalize dashboard guide and demonstration | Selin | Asier | P6.1 | Charts, history interpretation and demonstration scenarios documented with actual results. | Pending |
| P6.7a | Check and supply Asier's actual contribution and AI-attribution record | Asier | Gabriel | P6.2-P6.6 | Actual changes/commits, implementation AI entries and applicable trailers verified; inaccuracies corrected truthfully, without fabricated retrospective prompts. | Pending |
| P6.7b | Check and supply Gabriel's actual contribution and AI-attribution record | Gabriel | Alejandra | P6.2-P6.6 | Actual changes/commits, implementation AI entries and applicable trailers verified; inaccuracies corrected truthfully, without fabricated retrospective prompts. | Pending |
| P6.7c | Check and supply Alejandra's actual contribution and AI-attribution record | Alejandra | Christian | P6.2-P6.6 | Actual changes/commits, implementation AI entries and applicable trailers verified; inaccuracies corrected truthfully, without fabricated retrospective prompts. | Pending |
| P6.7d | Check and supply Christian's actual contribution and AI-attribution record | Christian | Selin | P6.2-P6.6 | Actual changes/commits, implementation AI entries and applicable trailers verified; inaccuracies corrected truthfully, without fabricated retrospective prompts. | Pending |
| P6.7e | Check and supply Selin's actual contribution and AI-attribution record | Selin | Asier | P6.2-P6.6 | Actual changes/commits, implementation AI entries and applicable trailers verified; inaccuracies corrected truthfully, without fabricated retrospective prompts. | Pending |
| P6.7 | Compare the five contribution records against actual changes and history | Christian | Selin | P6.7a + P6.7b + P6.7c + P6.7d + P6.7e | Each member checks their actual work, meaningful commits and relevant AI records/trailers; no retroactive invented prompts. | Pending |
| P6.8 | Perform a clean-clone installation and write the verification report | Selin | Asier | P6.2-P6.7 | Named commit installs and runs using README only; time-zone data and committed nonempty real-history paths work; tracked deliverable inventory has no unexplained empty folders/stubs; tests/scenarios and OS/tool versions recorded without copying private env or venv. | Pending |
| P6.9 | Prepare the final release PR and publish only after the required review | Asier | Gabriel | P6.8 | Personal -> dev -> main process observed; no bypass; delivered commit recorded and changed-version checks rerun if needed. | Pending |
| P6.10 | Submit the reviewed repository URL and record the actual receipt | Asier | Gabriel | P6.9 | Correct accessible repository URL submitted through confirmed channel; actual receipt/version/date recorded. | Pending |

## Final artifact checklist

| Artifact | Required content | Accountable owner |
| --- | --- | --- |
| Source and package | Installable src layout, pyproject, reproducible dependencies and implemented features | Every component owner; Asier integrates |
| README | Clean setup/run instructions, actual behavior and limitations | Asier with all section owners |
| Data | Real timestamped accumulated current/forecast logs plus documented catalog sources | Alejandra with all collectors |
| Analysis guide | Weather match, selected-mode reference duration, penalty and history interpretation | Christian + Selin |
| Collaboration | Genuine contributions, reviews, ongoing feature AI records and accurate co-author attribution | All |
| Submission | Accessible repository URL, final commit and actual channel confirmation | Asier / Gabriel review |

Local Streamlit execution is the agreed delivery target; public hosting is not a hidden requirement. External instructor reference files must not be necessary for someone to install the app. Keep variables.env private and provide only a safe example.

## Clean-clone and submission record

- Tested commit, machine/OS and versions: Pending.
- Actual installation/import/test/run commands and results: Pending.
- Real API check and fixture-check distinction: Pending.
- Delivered commit and any difference from tested version: Pending.
- Instructor access and submission channel: Pending.
- Submission date, submitter and receipt: Pending.
- Final team walkthrough and remaining required follow-up: Pending.


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

Asier completes P6.1. Asier then writes the usage guide, Gabriel API troubleshooting, Alejandra data documentation, Christian scoring explanations and Selin the Dashboard guide. Record submission only after it actually happens.
