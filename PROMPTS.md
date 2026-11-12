# AI collaboration log

Keep this file at the repository root and update it while work happens. Record each substantial AI-assisted feature, class, or setup task. A brief explanation or routine command does not need its own entry unless it changes a meaningful decision or result. Routine file moves and editorial housekeeping do not need separate entries; keep the record focused on substantive planning, setup, and development.

## Local commit checkpoint (2026-11-11)

The reviewed working tree is being recorded in three batches: documentation in
`00acc3a`, catalog and saved evidence in `5f73bc6`, and configuration, diagnostic
scripts, tests and starter-view alignment in the commit containing this checkpoint.
The final code changes are described in the existing P2.3/P2.4 entries below.
The pre-commit review passed 25 offline tests, both starter-view AppTests,
dependency/lock checks and the P2.4 catalog, defaults and saved-evidence audit.
Peer reviews remain pending. Earlier Commit / PR statements describe their
original recording time, not the current batch status. No merge is claimed.

## How the five-person team uses this log

1. Append an entry for the task before its changes are committed. Record the requesting teammate and AI tool; include a model name only when it is known.
2. Write a professional summary of the request and any material follow-up in the Asked field. Include the phase name, step, and purpose so a short instruction such as proceeding to the next step is understandable without the chat. Preserve the actual scope; do not invent requests. Redact secrets and label any verbatim excerpt if exact wording is needed.
3. Describe the output using the actual file, class, or function names. Separate generated suggestions from what was actually applied.
4. Record checks that really ran and their results. Mention relevant failures, skipped checks, and limitations. A passing placeholder test is not evidence of completed features.
5. Explain what was kept, changed, or rejected and why. Record human review as pending until it actually happens; do not invent reviewers, approvals, tests, or contributions.
6. Add a real PR link or commit reference once one exists. A commit SHA can be recorded in a later log update; do not invent a future SHA or claim work is published before a push.
7. Preserve other members' substantive contributions and actual verification results. Resolve log conflicts by keeping both contributions and their actual sequence. Editorial revisions may clarify summaries and consolidate administrative details without inventing or removing meaningful work. Every member remains responsible for understanding the code, including AI-written parts.

Never include real API keys in this log. The instructor starter code is inherited material; copying it does not make it AI-authored. Record the AI's actual changes to that starting point.

## Commit attribution convention

For Codex-assisted commits, use this exact final trailer line:

```text
Co-Authored-By: Codex <noreply@openai.com>
```

Use it on **every commit containing substantially AI-authored code**, as required by the assignment. Our team also uses it for substantially AI-authored setup and documentation changes. Purely human work does not need an AI trailer. If another AI tool substantially contributed, name that actual tool with its appropriate attribution; do not credit Codex for work it did not do.

Keep the human contributor's own Git identity as the author. The trailer belongs at the end of the commit message, separated from the subject or body by a blank line. Attribution in a PR description alone does not put it in the commit history.

Example message only; no commit is created by this example:

```text
chore: initialize Weather Insights starter

Add the starter package and local development setup.
Record the AI-assisted setup work in PROMPTS.md.

Co-Authored-By: Codex <noreply@openai.com>
```

When merging a PR, preserve the relevant human and AI trailers. If squash merging, check the final squash message before merging, because it becomes the message in the shared history. Add only people who actually co-authored the work, using the email address they choose for attribution.

AI attribution does not count as one of the five students' contributions. Each teammate must still make meaningful commits and understand the whole application.

Reference: [GitHub's commit co-author instructions](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors). The Codex name/email pair is also used in [OpenAI's Codex source tests](https://github.com/openai/codex/blob/main/codex-rs/cli/tests/login.rs). The capitalization above follows our assignment's example.

## Reusable entry template

Copy this template for a new substantial task. Replace the placeholders with actual information; it is not a completed work entry.

```markdown
## Feature or setup: <short name> (<YYYY-MM-DD>)

**Requested by:** <actual teammate name or GitHub handle>

**AI collaborator:** <actual tool; model if known>

**Asked:** <professional summary of the actual request, including phase/step and purpose; not a fabricated verbatim quote>

**Got:** <actual files/classes/functions suggested and applied>

**Checked:** <commands or manual checks actually performed, outcomes, and limits>

**Kept / changed / rejected:** <decisions and reasons>

**Human review:** <pending, or the actual reviewer and outcome>

**Commit / PR:** <pending until it exists, then the actual reference>

---
```

The Asked fields below are professional summaries of the original requests and their context, not verbatim quotations. The chronological records retain the actual outputs, checks, decisions, and review status. Every entry uses the same eight fields shown in the template.

Historical status: the seven original entries dated 2026-11-05 retain their review and publication status at the time they were recorded. Their setup changes were subsequently included in [initial commit 0223991](https://github.com/AsierMarmol/weather-insights/commit/0223991f05005d0420c7be2c760c2c6850fbfd88). The later records below connect the completed manual steps and verification evidence to that real commit; they do not retroactively claim peer approval. Later entries also retain their status at the time of recording; the publication entry records the corresponding commit and PR references.

---

## Setup: Phase 1 - Team and Environment Setup (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Define Phase 1 - **Team and Environment Setup** to support the preparation of Weather Insights before feature development. Organize the Python environment, secure credentials, installable package, GitHub repository, and five-person collaboration into small, ordered steps with a clear completion check before proceeding.

**Got:** Documented the user-established Phase 1, **Team and Environment Setup**, and created a 17-step checklist. The plan covers environment setup, API-key protection, project documentation, AI records, Git identity, an approved initial baseline, the `asier/feature` -> `dev` -> `main` workflow, repository review rules, and teammate onboarding.

**Checked:** Compared the phase scope and checklist with the assignment README and technical summary. Confirmed that setup supports the required package, credential, AI-record, and team foundations while leaving OOP implementation, API behavior, observation logging, analytics, and the completed dashboard to later phases. Distinguished course requirements from team choices and optional tooling.

**Kept / changed / rejected:** Kept the user's Phase 1 name and preparation-first sequence. Adopted small checkpoints so the team can finish and understand each setup step before moving on. Retained the requested branch flow and kept optional automation separate from mandatory course requirements.

**Human review:** Pending review of the complete initial change set; no commit approval is implied.

**Commit / PR:** Not created for this task; no commit or push was performed.

---

## Setup: Python environment and dependencies (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 2: prepare and verify the Python development environment. Create a local virtual environment with the agreed Python 3.14 series, install the starter package and dependencies, add pytest, and record the shared dependency configuration for the team.

**Got:** Created a project-local `.venv` using Python 3.14.7, added `.python-version` selecting 3.14, declared pytest in the development dependency group in `pyproject.toml`, generated `uv.lock`, and excluded generated package/test artifacts in `.gitignore`. A temporary verification script checked installed-package imports and both existing Streamlit views.

**Checked:** `uv sync --locked`, `uv pip check`, and `uv run --locked python -m pytest -q` passed. The one passing test is the instructor's placeholder arithmetic test, not a feature test. The installed package and all declared dependency imports succeeded under Python 3.14.7, and both starter views loaded without exceptions. Git ignore checks confirmed `.venv`, `variables.env`, and `.env` are excluded. No credentials, live API requests, or fabricated weather observations were used.

**Kept / changed / rejected:** Retained the instructor's application code and feature placeholders. Standardized the development environment on Python 3.14 and the shared lockfile. Applied environment and generated-file housekeeping changes without implementing weather features.

**Human review:** The user confirmed the VS Code interpreter selection and starter app startup. Review and approval of the complete initial commit remain pending.

**Commit / PR:** Not created for this task; no commit or push was performed.

---

## Setup: API-key and secret-file protection (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 4: **finish API-key and secret-file protection**. Review environment loading, protect local credential files and backups from Git, keep the publishable example blank, and verify the configuration without using or exposing a real API key.

**Got:** Expanded `.gitignore` exclusions for local environment files, common backups, and Streamlit secrets, while keeping blank examples eligible for tracking. `variables.env.example` now has an empty key and safe copy instructions. A local blank `variables.env` was created if absent; existing personal credentials would be preserved. The instructor's `config.py` was retained.

**Checked:** 22 Git ignore checks passed, including secret variants, safe examples, generated environment files, and future CSV/SQLite observation logs. Four isolated checks of the unchanged configuration code passed: missing file, blank key, file loading from another working directory, and process-environment precedence. These checks used dummy values in a temporary directory and produced no key output. No possible secret files are tracked. No real key or live API request was used.

**Kept / changed / rejected:** Kept the starter's `python-dotenv` loading and explicit missing-key error. Added only credential-file housekeeping and records. A real personal key remains to be added locally before API testing; that is not required to verify these protections. No application feature, commit, push, or GitHub permission change was made.

**Human review:** Pending review of the complete initial change set; no commit approval is implied.

**Commit / PR:** Not created for this task; no commit or push was performed.

---

## Setup: application setup and run documentation (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 5: prepare the application's setup and run documentation. Write a self-contained Windows README covering prerequisites, dependency installation, local credentials, VS Code interpreter selection, Streamlit startup, installation checks, troubleshooting, and the starter's current limitations. Verify the instructions in a fresh local source copy.

**Got:** Replaced the template README with self-contained Windows setup/run instructions, prerequisites, a credential-copy guard that preserves existing files, VS Code interpreter selection, installation checks, troubleshooting, the actual package structure, and the agreed team branch flow. The README clearly states that the two starter views contain headings only and weather features remain unimplemented. It contains no dependency on external phase plans or assignment files.

**Checked:** Nine checks passed in a fresh temporary source copy with a new `.venv`: locked installation, initial credential copying, preservation of an existing dummy credential file, Python version, dependency consistency, installed-package import, the documented pytest command, Streamlit runner syntax, and both views via AppTest. The test suite still contains only one arithmetic placeholder. No personal credential file or existing environment was copied. The initial help-output check encountered Windows text encoding limitations; it passed when the verification subprocess used UTF-8. The application source and lockfile stayed unchanged. A real GitHub clone is still pending the first authorized push; the README explains that an empty remote cannot yet supply the starter files.

**Kept / changed / rejected:** Kept the current application code, dependency versions, package name, and user-selected branch flow. Added documentation and accurate status information without introducing weather features. No commit, push, GitHub change, or new web server was performed.

**Human review:** Pending review of the complete initial change set; no commit approval is implied.

**Commit / PR:** Not created for this task; no commit or push was performed.

---

## Setup: AI collaboration and co-author convention (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 6: establish a consistent AI collaboration and co-author convention for the five-person team. Use the same structured fields for all entries, summarize requests professionally with phase and step context, retain meaningful outputs and verification results, and define accurate commit attribution for AI-assisted work.

**Got:** Added the team logging rules, a reusable eight-field entry template, professional contextual request summaries, the exact Codex co-author trailer, a commit-message example, and merge-attribution guidance. Updated the application README to link to the convention and organized the log around Phase 1 planning and substantive setup tasks.

**Checked:** Compared the convention with the assignment README and summary and checked co-author syntax against GitHub's official instructions. The commit-message example was validated previously with `git interpret-trailers --parse`, without creating a commit. Reviewed the revised log for consistent fields, contextual summaries, retained verification evidence, and unchanged pending review states. Documentation changes did not require rerunning application tests.

**Kept / changed / rejected:** Kept the substantive Phase 1 records and their actual outcomes. Used a fenced reusable template and clearly labeled professional request summaries. Retained `Co-Authored-By: Codex <noreply@openai.com>` for this tool and record exact model names only when known. Human authorship and the requirement for five real student contributors remain separate from AI attribution.

**Human review:** Pending. The convention is documented for review; this entry does not claim approval of a commit.

**Commit / PR:** Not created; no commit or push has been authorized by this step.

---

## Setup: Git author identity (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 7: configure my Git author identity for this repository. Use my GitHub username as the author name and the exact GitHub-provided no-reply email supplied from my account settings, so future local commits use my selected private identity.

**Got:** Configured repository-local `user.name` as `AsierMarmol` and `user.email` with the exact no-reply address shown in the user's GitHub settings screenshot. The missing-email prerequisite is resolved. GitHub sign-in and commit authorship were treated as separate settings; the personal profile email was not substituted.

**Checked:** Read back the local and effective name/email settings and verified both `GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT` resolve to the selected identity without creating a commit. Confirmed global name/email settings, HEAD, and the Git index were unchanged. Application tests were not rerun because this task changed identity configuration and records only.

**Kept / changed / rejected:** Kept the user's username and private-email preference. Scoped the settings to this repository. GitHub's account-wide web-operation privacy setting was not changed. Other teammates will configure their own identities during onboarding.

**Human review:** The user selected the username and supplied the exact GitHub no-reply address. Review and approval of the initial commit remain pending.

**Commit / PR:** Not created for this task; nothing was staged, committed, or pushed.

---

## Setup: initial repository snapshot review (2026-11-05)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 8: rerun the initial snapshot review after completing the Git identity. Verify the current files, private no-reply author details, credential protections, project documentation, and installation from a fresh local source copy, and confirm whether the setup is ready for Step 9 without staging, committing, or pushing.

**Got:** Reverified the complete 15-file initial baseline on `main` for `AsierMarmol/weather-insights`. Confirmed the configured no-reply identity and prepared a concrete initial commit message with the agreed Codex co-author trailer. Updated the external Phase 1 checklist and review manifest. Technical checks for the initial setup commit passed; explicit authorization for the commit is still pending.

**Checked:** The rerun verified the root/branch/remote, empty initial Git state, local/effective author and committer identity, all 15 candidate files, candidate-only common secret/email/credential-URL patterns, blank publishable example, Python/TOML syntax, 24 ignore cases, seven consistently structured AI records, and the proposed commit trailer. A fresh temporary source copy with a new environment passed locked installation, Python version, dependency consistency, package imports, the one existing placeholder test, Streamlit runner syntax, and both starter views. The documented credential-copy command created a blank file and preserved an existing dummy file. Four isolated loading checks passed for missing/blank keys, working-directory independence, and environment precedence. No private credential file, existing environment, Git metadata, or phase plan was copied. Original source/lockfile, HEAD, and index were unchanged by verification. No real key or live API request was used; a real GitHub clone remains for verification after the first push.

**Kept / changed / rejected:** Kept the reviewed 15-file starter baseline and its documented limitations. Retained the selected username/no-reply identity and excluded local secrets, environments, generated artifacts, and external planning documents. Updated this existing review entry rather than adding a separate administrative rerun entry. The passing arithmetic placeholder is recorded as a setup check, not evidence that weather features exist.

**Human review:** Pending user review and explicit authorization of the proposed initial commit. Successful technical checks do not imply commit approval.

**Commit / PR:** Not created for this task; nothing was staged, committed, or pushed.

---

## Setup: Phase 1 baseline publication and team collaboration (2026-11-10)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Steps 9-15: guide the initial commit and publication, the `main`, `dev`, and personal branch setup, branch protection, collaborator invitations, and local onboarding. Keep commits, pushes, and GitHub configuration under manual user control, and verify the completed setup against the assignment before proceeding. Consolidate the already-recorded outcomes and evidence in the repository's AI log.

**Got:** Asier manually created the initial commit, amended it to include the agreed Codex co-author trailer, published `main`, and created/published `dev` and `asier/feature`. The assistant guided the manual protection and invitation steps and checked the published setup. The shared repository now contains the five personal branches listed in README.md, and GitHub marks `main` and `dev` protected. Asier reports that all four teammates have access and have completed onboarding. This entry brings those existing session/checklist records into the ongoing repository log.

**Checked:** The earlier 5 November audit verified the actual GitHub clone: locked installation, dependency consistency, package import, the one arithmetic placeholder test, both starter views, safe credential-file copying with dummy values, and published author/co-author metadata passed. On 10 November, the connected GitHub branch listing confirmed all seven branches and protection enabled for `main`/`dev`; those shared branches and published `asier/feature` still reference initial commit `0223991`. Before the Step 16 documentation edits, local `asier/feature` was clean and tracked `origin/asier/feature` at that commit. The protection-option screenshots show the selected review rules; the first real PR must still exercise their enforcement. Individual teammate installation checks, Git identities, and app operation are reported rather than independently verified. No private credential file was read and no new live API or application test was run for this record update.

**Kept / changed / rejected:** Kept the published starter baseline, the user's personal-branch-to-`dev`-to-`main` flow, individual human authorship, and the agreed AI trailer. Preserved the seven historical entries and their actual earlier review states. Used recorded checks and live branch metadata to add completed outcomes without inventing teammate contributions, review approvals, or per-machine test results. Branch publication and onboarding do not replace the course requirement for meaningful contributions from all five students.

**Human review:** Asier performed the initial commit/publication and GitHub setup manually and provided the protection-setting screenshots. No peer review of the initial direct publication is claimed. Individual onboarding confirmations and the first reviewed documentation PR remain pending.

**Commit / PR:** Published initial baseline: [0223991f05005d0420c7be2c760c2c6850fbfd88](https://github.com/AsierMarmol/weather-insights/commit/0223991f05005d0420c7be2c760c2c6850fbfd88), authored by AsierMarmol with `Co-Authored-By: Codex <noreply@openai.com>`. This reference identifies the initial setup changes; the new log record itself is part of the pending Step 16 documentation change. No PR reference exists for that change yet.

---

## Setup: Phase 1 first reviewed documentation change (2026-11-10)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Continue Phase 1 - **Team and Environment Setup**, Step 16: prepare the first useful documentation change on `asier/feature`. Update README.md to reflect the published branches and current collaboration process, and update PROMPTS.md with completed manual setup outcomes and actual commit references. Leave the commit, push, PR creation, and merge for the user to perform manually.

**Got:** Removed the README's obsolete empty-repository instruction and replaced future branch-setup wording with the current shared/personal branches, selected review policy, PR sequence, and onboarding status. Added historical-status context and the preceding evidence-based publication record to PROMPTS.md. Kept this entry ready for the upcoming peer review and actual commit/PR references.

**Checked:** Compared the changes with the assignment's README/AI-record requirements, the existing setup evidence, current branch metadata, and the user's reported onboarding status. Verified that the seven historical entries and all README command blocks remain unchanged, each of the nine task entries has the same eight fields, local Markdown links resolve, and only README.md and PROMPTS.md differ in the checkout. `git diff --check` passed; HEAD and the index were unchanged. Application code, dependency versions, and credential files were not edited, so application tests were not rerun for this documentation-only change. Branch-protection enforcement remains for the real PR.

**Kept / changed / rejected:** Kept the install/run commands, secure credential guidance, honest starter limitations, and original historical records. Replaced stale setup status with verified facts and clearly labeled user reports. Left CI, PR templates, feature development, and any claimed review approval outside this change so the first PR stays focused and understandable.

**Human review:** Pending peer review of the documentation diff. Asier requested preparation; this entry does not claim a teammate's approval or completion of the PR workflow.

**Commit / PR:** Pending. The assistant has not staged, committed, pushed, opened a PR, or merged these changes. Add the actual commit/PR reference after the user creates it; `0223991` above refers only to the already-published initial baseline.

---

## Setup: Phase 1 publication and Phase 2 plannings (2026-11-10)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Finish Phase 1 - **Team and Environment Setup** by moving PHASE1_SETUP.md back beside the repository README, then commit and publish the documentation on `asier/feature`, open a PR into `dev`, and request Gabriel's review. Keep Step 17 pending while Asier obtains teammate confirmations, and prepare Phase 2 - **Ideation and Project Flexibility** using the same ordered steps and completion checks.

**Got:** Relocated PHASE1_SETUP.md into the repository and updated its current location policy, checklist, and next-phase status. Added PHASE2_SCOPE.md as a planning draft, linked both plans from README.md, and retained the existing documentation updates and historical AI records. Confirmed Gabriel's account as `gabrielstec` with repository write access. Committed and published the authorized four-file documentation snapshot as `a81d470` and opened [PR #1](https://github.com/AsierMarmol/weather-insights/pull/1) from `asier/feature` into `dev`. Gabriel is the selected reviewer; no approval, merge, or teammate confirmation is invented.

**Checked:** Compared the plans with the authoritative assignment and supporting summary. Verified the preserved historical AI entries, uniform eight-field task records, repository-local Markdown links, unchanged install/run command blocks, code fences, whitespace, and the four-file documentation scope. Reviewed staged candidates for credentials and confirmed that source, dependencies, the lockfile, and instructor references are unchanged. Checked the selected no-reply Git identity and Codex trailer. Application tests were not rerun for these documentation-only changes. The actual PR will provide review-state evidence; individual teammate checks remain Asier's pending confirmations.

**Kept / changed / rejected:** Kept the tested package/environment, real-data and credential rules, five-person workflow, and honest starter limitations. Applied Asier's updated root-level phase-plan organization and explicit publication authorization in place of the earlier preferences. Phase 2 remains a draft with unapproved decisions; feature development, bypassing review, and claiming Phase 1 complete are outside this change.

**Human review:** Asier explicitly authorized the move, commit, publication, and Gabriel review request. Gabriel's peer review is pending. Asier is collecting the Step 17 confirmations; none are recorded as received by this entry.

**Commit / PR:** Published documentation snapshot: [a81d4708d3251f1d83b2ea9b6d1fbd8165f6c8dc](https://github.com/AsierMarmol/weather-insights/commit/a81d4708d3251f1d83b2ea9b6d1fbd8165f6c8dc). Review: [PR #1, asier/feature into dev](https://github.com/AsierMarmol/weather-insights/pull/1), with Gabriel (`gabrielstec`) selected for review. The snapshot and this reference update use AsierMarmol's configured no-reply identity and the Codex trailer. Peer approval, merging, and Step 17 confirmations remain pending.

---

---

## Planning: Separate phase-plan templates (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Create separate Markdown templates for every project phase, following the detailed structure of PHASE1_SETUP.md and PHASE2_SCOPE.md, ready to fill and update after the group agrees on the business idea. The follow-up clarified that a single overview was insufficient.

**Got:** Added PHASE3_CORE_DATA.md, PHASE4_ANALYTICS_UI.md, PHASE5_QUALITY_REVIEW.md, and PHASE6_DELIVERY.md with ordered steps, finish conditions, phase-specific specification tables, responsibilities, decisions, risks, and completion evidence. Converted PROJECT_PHASES.md into the navigation index and updated its README link.

**Checked:** Verified ten ordered steps and the common planning sections in each new phase, checked local Markdown links and whitespace, and confirmed the existing Phase 1 and Phase 2 files were unchanged. Application tests were not run because this task changes documentation only.

**Kept / changed / rejected:** Preserved existing setup evidence and the Phase 2 draft. Replaced the single detailed overview with separate maintainable plans. Product choices, assignments, reviews, and completion evidence remain pending; no business idea or feature implementation is introduced.

**Human review:** Pending team review; these templates do not establish an approved product scope or completed phase.

**Commit / PR:** Not created; these documentation changes remain local and uncommitted.

---

## Phase 2: P2.1 scope-to-rubric review (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Review the current project state and carry out the next phase task. For P2.1, prepare the scope-to-rubric checklist and unresolved-proposal register for the agreed mainland-Spain weather getaway application. Assigned task owner: Asier; assigned peer reviewer: Gabriel (gabrielstec).

**Got:** Added the P2.1 deliverable inside PHASE2_SCOPE.md, separating agreed scope, sixteen assignment-requirement mappings, unresolved decisions with authors/reviewers, and Gabriel's review checklist. Updated PROJECT_PHASES.md to show the deliverable awaiting review and the subsequent P2.2/P2.3 next steps.

**Checked:** Read the instructor assignment and supporting summary, checked the actual branch/status and starter files, verified referenced task IDs, local document links, Markdown structure/whitespace, preserved earlier log entries, and confirmed unrelated files and Git HEAD/index were unchanged. No application tests or live API requests were run: this is a specification task, and the existing arithmetic placeholder is not feature coverage.

**Kept / changed / rejected:** Kept the agreed Madrid/mainland-Spain, Car/Train, activity, 24/48/72-hour and three-component weather-scoring scope with a one-point-per-hour penalty capped at five. Kept unverified catalog/API/storage/UI defaults pending their named tasks. Marked the deliverable prepared, not peer-approved; no Claude contribution or other student's authorship is claimed for this Codex-assisted work requested by Asier.

**Human review:** Pending Gabriel's actual review. No review request was sent, and no teammate approval or group walkthrough was fabricated.

**Commit / PR:** Not created; the deliverable and prior planning changes remain local and uncommitted. No push or merge was performed.


---

## Phase 2: destination CSV categories and size integration (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex

**Asked:** I manually selected and confirmed the destination categories and the separate size classification in our discussion. Integrate the destination CSV into the project's data/reference folder, update its activities to Coast, Nature, History and heritage, Food and gastronomy, and Urban experiences, add destination_size, and align the affected documentation. This is my P2.2 catalog task, using ChatGPT/Codex to help integrate it into the repository.

**Got:** Updated data/reference/destinations.csv in its existing project location. Retained all 83 destinations and their identifiers, regions, driving estimates and coordinates. Replaced mixed activity/size labels with five experience categories and a separate size value derived from the previously retained GeoNames reference populations. Updated both project READMEs and directly affected phase/role schema references. No weather feature was implemented.

**Checked:** Parsed the saved CSV; verified 83 unique records, nine exact columns, allowed nonempty activity tags, one valid size per row, preserved original non-category values, and classifications against the source population bands. Result: 14 large cities, 26 medium cities and 43 small cities or towns. Inspected before/after table previews, checked local Markdown targets and Git whitespace, and preserved application code, dependency files, Phase 1 and instructor references. Application tests were not rerun because this changes reference data/documentation and no catalog loader exists yet.

**Kept / changed / rejected:** Kept the car-only scope, catalog ownership and route/source limitations. Adopted the group-approved activity/size separation. Size is a project population convention and does not change scores. Activity labels remain proposals pending source and Christian's peer review. Preserved the earlier CSV draft's actual AI-assisted provenance; this entry records Asier's manual category choice and Codex's integration, not a claim that the full dataset was manually authored.

**Human review:** Asier confirmed the taxonomy and separate size field. Final catalog-content and peer review remain pending; no approval from Christian is claimed.

**Commit / PR:** Not created for this task. No commit, push or merge was performed.


---

## Phase 2: P2.3 weather-source verification and usage contract (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Proceed with P2.3 of Phase 2: verify the OpenWeatherMap data source and prepare its usage contract for the car-only mainland-Spain getaway application. Safely test current conditions and the five-day forecast using catalog coordinates and my local ignored API credential. Confirm fields, units, timestamps, 24/48/72-hour daytime coverage, expected failures and request/refresh rules. Preserve every successful genuine fetch with a retrieval timestamp, update the affected phase records and READMEs, and record actual verification results. Keep production features and the ongoing collector for their assigned later tasks. Do not expose credentials, commit, push or merge.

**Got:** Added WEATHER_API_CONTRACT.md, the bounded scripts/verify_weather_access.py diagnostic, eight offline diagnostic tests, and genuine verification data plus a README under data/weather. Updated current P2.3 status and relevant README/index/Phase 3 input references. Defined provider field conversions and proposed project defaults for common forecast windows, freshness, request budgets and failure handling; production implementation remains pending.

**Checked:** Read official OpenWeather current/forecast, FAQ and pricing documentation. Six actual requests: Toledo/Segovia current and forecast all returned 200; deliberately invalid key returned 401; unknown city returned 404. Each forecast had 40 unique consecutive three-hour periods and complete 24/48/72-hour daytime coverage with 3/6/9 relevant periods in this run. Appended four genuine responses with UTC retrieval and provider times, including two observations and 80 prediction periods. Ran pytest: 9 passed, comprising eight offline diagnostic checks and the original placeholder. Checked redaction, missing probability/coverage, failure/timeout sanitization, local documentation targets and whitespace. Confirmed the key was absent from new artifacts without printing it. No live quota/outage was induced; account billing settings and full 83-city behavior were not verified.

**Kept / changed / rejected:** Kept existing application modules, credentials, catalog and completed setup unchanged. Adopted coordinate requests with metric units, explicit wind/probability conversions, separate retrieval and valid times, and native three-hour forecast sampling. Kept predictions separate from observed history. Rejected treating four verification fetches as an ongoing collector, a historical trend, or proof that application features work. P2.4 still owns final shared schemas and independently checked examples; P2.5 starts ongoing collection.

**Human review:** Pending Gabriel's actual review of the prepared P2.3 contract and evidence. No review request or teammate approval was fabricated.

**Commit / PR:** Not created for this task. All changes remain local; no commit, push or merge was performed.


---

## Phase 2: P2.3 full-catalog access and city-name audit (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Extend P2.3 verification to every destination in the current 83-city CSV. Test current conditions and the full forecast using each catalog coordinate pair, and verify that returned location names correspond to the intended city. Compare country and coordinate proximity as well as spelling. Preserve authentic timestamped successes and existing data, protect credentials, and bring ambiguous names or possible location matches to me for confirmation before changing the catalog.

**Got:** Added an --all-cities diagnostic mode with safe pacing and early authentication/quota stops. Added separate normalized-name, country and 10 km review-threshold checks, two relevant offline tests, a complete city-location review report (later consolidated into the catalog source notes) table and a derived JSON audit snapshot under data/weather. Updated affected README/contract/phase evidence. All 83 CSV destinations remain unchanged.

**Checked:** 166 actual current/forecast requests; 166 successful responses appended; 83/83 cities passed access, required fields and complete 24/48/72-hour daytime coverage. 6 cities require name/location confirmation. Six supplemental official direct-geocoding requests returned 200 and were saved separately: five support language/bilingual variants; Lugo remains a distinct label/location question, not an approved Puente alias. Ran the offline suite: 11 passed. Country/proximity checks are separate from label matching; returned coordinates alone cannot prove municipal identity. Checked preserved catalog hash, prior fetch-log prefix, credential absence from artifacts, local document targets and Git whitespace.

**Kept / changed / rejected:** Kept car-only scope, existing CSV values and original fetch evidence. Retained all successful real responses, separating predictions from observed conditions. Did not silently approve translations/bilingual variants or substitute nearby cities. The earlier deliberate 401/404 tests are not catalog failures and were not repeated in the full-catalog mode. This audit does not create a production app, final storage schema or ongoing collector.

**Human review:** 6 city-name/location flags await Asier's confirmation; Gabriel's P2.3 peer review remains pending. No teammate approval is claimed.

**Commit / PR:** Not created for this task. No commit, push or merge was performed.


---

## Phase 2: P2.2/P2.3 API-standard city names and Lugo identity (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Standardize the catalog against the weather API as our source of truth so city names remain consistent across the CSV and weather data. Update the CSV names to the provider standard, resolve Lugo's actual city coordinates, and keep its driving reference consistent with any coordinate change. Verify the result, preserve genuine raw responses, document provider inconsistencies and update the affected project records without committing or pushing.

**Got:** Aligned eight CSV city labels to the actual forecast labels, including accent/spelling changes, while preserving all 83 IDs, rows, regions, activities and sizes. Added a small provider-overrides reference for two current/forecast label variants and Lugo city ID 3117814. Updated Lugo to API city reference coordinates 43, -7.5667 and refreshed its route to 498 km / 329 minutes. The diagnostic now consumes the explicit aliases and city-ID override. Preserved original audit evidence, added candidate dispositions and reconciled the latest name/coverage snapshot. Updated the relevant READMEs, API contract and phase inputs/statuses.

**Checked:** City-ID requests for Lugo returned 200 and name Lugo in both products. Geocoding and coordinate trials revealed that coordinate weather requests label this area Puente, while generic Lugo lookup resolves province ID 3117813; those were not silently accepted as the city. Province trials were explicitly excluded from city-history migration. Refreshed OSRM driving distance/time from the original fixed approximate Madrid Km0 origin. Reconciled existing all-city responses and actual Lugo city-ID evidence: 83 exact forecast names, 81 exact current names plus two documented aliases, valid country/proximity/required fields/24-48-72h coverage, no unresolved identity flags. Ran pytest: 12 passed. Checked exact nine-column schema, intended cell changes only, preserved raw history, prior AI-log entries, secret absence, document targets and whitespace. No new complete 166-call run is claimed.

**Kept / changed / rejected:** Kept INE-based city IDs and all unrelated catalog/application fields. Adopted forecast names as the canonical CSV/UI display convention; preserved raw current labels as explicit aliases. Rejected the misleading province-level Lugo point and avoided renaming Lugo to Puente. Used the actual legacy city-ID path only for the documented Lugo exception; an unavailable ID must fail clearly rather than fall back to a different location. The coordinate is a coarse weather-product reference, not a surveyed tourist centre. Kept genuine diagnostic fetches for audit while identifying rejected candidates separately.

**Human review:** Asier authorized API-based naming and the Lugo correction. Gabriel's technical peer review and separate catalog activity/source review remain pending; no teammate approval is claimed.

**Commit / PR:** Not created for this task. No commit, push or merge was performed.


---

## Phase 2: P2.1 finalized product decisions and aligned project plans (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Apply the agreed product decisions across the project and update every affected current specification, phase, role, reference/default and verification file. Use rolling 1-5-day windows from use, default 3 days; editable seasonal temperature defaults in Europe/Madrid (winter 10-18 C, spring 18-26 C, summer 22-30 C, autumn 16-24 C), rain <=30%, wind <=25 km/h and visible All activity/size selections. Preserve manual preferences. Keep any-selected activity matching, five leading recommendations plus the full ranking, stable tie-breaks and two interactive Searcher/Dashboard views. Replace the required historical-trend feature and separate collector with ranking, weather comparison, all-preferences-period metrics and automatic timestamped saving on fresh successful fetches. Record actual changes/checks professionally, preserve historical evidence and mark unbuilt features pending. Do not commit, push or merge.

**Got:** Finalized the P2.1 product specification, two-view outline and rubric checklist. Added data/reference/product_defaults.json as the shared initial-value reference. Updated PROJECT_PHASES.md, Phases 2-6, TEAMROLES.MD, WEATHER_API_CONTRACT.md and the project/reference/weather READMEs. P2.5 is now the initial bounded fetch-and-save foundation, not a scheduler or user collection routine. P2.4 retains technical schemas/function examples and component briefs, resolving the former P2.1/P2.4 overlap. Updated the diagnostic to check 24/48/72/96/120-hour windows, added fifth-day/clock-change regression checks, and checked an offline five-day coverage snapshot (later removed as a derived report). Renamed the existing starter headings/navigation to Searcher and Dashboard and updated placeholder comments; no later-phase controls, charts, scoring engine or production persistence were implemented.

**Checked:** Ran pytest: 14 passed. Streamlit AppTest opened both renamed starter views without exceptions. Replayed the retained genuine forecasts at their original common search time: all 83 cities passed each 1-5-day daytime window; no new live requests or current-freshness claim. Checked five season/default/filter settings against the approved specification, all 12 month assignments, phase task IDs/dependencies/owners, local document targets, source syntax and Git whitespace. Verified unchanged CSV/provider overrides, original raw response/run evidence, completed Phase 1, unrelated implementation/configuration files, dependency files and instructor references. Preserved previous PROMPTS entries and historical phase results.

**Kept / changed / rejected:** Kept the nine-column/83-city catalog, API naming/Lugo exception, three equal weather checks and capped driving-time deduction. The simultaneous-all-preferences percentage is explanatory, not a new score weight. Corrected the earlier claim that the teacher mandates a historical-trend chart: timestamped logging remains mandatory and actual records must accumulate through normal use and be submitted, while the chosen analyses span comparison and derived metrics. Removed required continuous/manual collection and forecast-versus-reality work. Defaults are product preferences, not climate averages; seasonal initialization must never silently overwrite user edits. Shared defaults exist as reference configuration; runtime preference loading and application features remain assigned future work.

**Human review:** The user approved the product choices. Gabriel's specification/API peer review and Christian's independent catalog content/source review remain pending. No teammate approval or completed application behavior is claimed.

**Commit / PR:** Not created for this task. Changes remain local; no commit, push or merge was performed.


---

## Phase 2: P2.4 shared data and calculation specification (2026-11-11)

**Requested by:** AsierMarmol.

**AI collaborator:** OpenAI Codex.

**Asked:** Define a simple shared data and calculation specification for the agreed project, with clear component boundaries and independently checked examples. Align the phases with the actual shared files, retain the corrected nine-column catalog, remove unused categories and duplicated implementation work, and keep production components assigned to their owners.

**Got:** Documented P2.4 directly in PHASE2_SCOPE.md: domain fields, normalized weather CSV schema, shared component inputs/outputs, units, time/save/error rules and a small worked scoring example. Aligned phase dependencies and roles so P2.5 verifies the actual shared API/store after P3.1/P3.2 rather than building a second implementation. Simplified current READMEs/provider notes and retained the established product decisions. Configuration now reads credentials only when requested, and the diagnostic handles malformed location payloads and storage failures safely. Removed the arithmetic placeholder; actual production classes and UI features remain pending.

**Checked:** Worked examples were independently checked: Toledo ranks before Segovia and Seville; equal weather scores can have different simultaneous-suitability percentages. The earlier baseline had 14 passing tests including one arithmetic placeholder. Verification after these revisions: 25 offline tests passed; both starter views passed AppTest. Python/TOML/JSON parsing, local document links and Git whitespace checks passed. The catalog, defaults, dependency files, .gitignore and instructor references remained unchanged. No live requests or peer approvals are claimed.

**Kept / changed / rejected:** Kept the catalog's corrected values, provider request override, timestamped real-data requirement, seasonal preferences, three analyses and component ownership. Removed duplicated specification/status text and unsupported size options. Retained accurate Asier/Codex attribution and separated planned interfaces from implemented behavior.

**Human review:** User approved the simplification and data-investigation removal. Christian's P2.4/catalog review and Gabriel's specification/API reviews remain pending.

**Commit / PR:** Not created. Changes remain local; no commit, push or merge was performed.

---

## Phase 3: P3.1 models, catalog loading and weather-record storage (2026-11-12)

**Requested by:** Alejandra Medina (alemedinabarreto).

**AI collaborator:** Claude Code (Anthropic Claude Opus 5.5).

**Asked:** Synchronize the personal branch with the latest dev, then implement the owned P3.1 deliverable from PHASE3_CORE_DATA.md against the P2.4 shared specification: validated domain models with a meaningful special method and computed property, the nine-column catalog loader, and safe CSV saving/reloading of normalized weather records, with tests and documentation.

**Got:** `src/weather_app/models.py`: frozen keyword-only dataclasses `Destination`, `SearchPreferences` and `WeatherRecord` that validate types, finite values, coordinate/percentage ranges, allowed activity/size labels, UUID fetch IDs and timezone-aware times (normalized to UTC); properties `drive_hours`, `horizon`, `lead_time` and `key`; `__str__`/`__repr__` and chronological `__lt__`; exact CSV serialization with blank cells for missing values. `src/weather_app/storage.py`: `load_destinations()`, `WeatherStore.append/load/latest_forecast`, `CatalogError` and `StorageError`, repository-rooted default paths, idempotent retries, conflict detection, atomic copy-append-replace writes, a per-file process lock held in a name-mangled class attribute, and newest-single-group forecast selection. `tests/test_models.py` and `tests/test_storage.py`.

**Checked:** Baseline before changes: 25 offline tests passed and both starter views passed AppTest. After changes: `uv run --locked python -m pytest -q` passed 107 tests (82 new). The real catalog loads 83 destinations with 14/26/43 size counts and unchanged Lugo values. Storage tests use pytest temporary directories only and cover round trips, filters, retries, distinct fetches, conflicts, byte-for-byte preservation, newest-group selection, failed replace, unwritable paths, damaged/partial files and concurrent appends. Optionally compared the private handoff fixtures against the models (header, three catalog rows, preferences and 12 synthetic records accepted); they are not a repository or test dependency. No live API request was made and no `weather_records.csv` was created.

**Kept / changed / rejected:** Kept the P2.4 field names, CSV header, entry-point signatures and `None`-not-zero rule. Added `append()` returning the count of new rows, and explicit error classes for P3.2 to map to the `storage`/`invalid_data` codes. Rejected the earlier unpublished local prototype (single-snapshot OpenWeatherMap client, comfort index and collector) because it predates the agreed scope and overlaps Gabriel's P3.2; it remains on a separate local branch and is not part of this change. Deferred importing the retained JSONL evidence until P3.2 provides the provider mapping, so original retrieval times are preserved without a second mapping implementation.

**Human review:** Alejandra directed the work and approved proceeding while Christian's P2.4/catalog review is outstanding. Christian's P3.1 review is pending; no approval is claimed.

**Commit / PR:** Pending.

---

## Phase 3: P3.3 analytics and ranking engine (2026-11-12)

**Requested by:** Christian Sawaya (christiansawaya-code).

**AI collaborator:** Claude Code (Anthropic Claude Opus 5.5).

**Asked:** Synchronize the personal branch with the latest dev, then implement the owned P3.3 deliverable from PHASE3_CORE_DATA.md against the P2.4 specification in PHASE2_SCOPE.md: a pure analytical engine covering the rolling daytime window, activity/size filters, weather checks, capped driving penalty, tie-breaking and unavailable states, with independently checked tests.

**Got:** `src/weather_app/analytics.py`: `analyse_destinations(destinations, forecasts_by_city, preferences, run_at_utc)` returning the full ordered list of P2.4 result dictionaries (ranking, cross-city weather comparison and all-preferences periods as columns of one result), plus `expected_period_times`, `is_daytime`, `is_eligible` and `ranking_key`. It uses the shared P3.1 `Destination`, `SearchPreferences` and `WeatherRecord` models, requires an explicit UTC run time, and performs no network, file, credential, UI or clock access. `tests/test_analytics.py` with 30 offline tests.

**Checked:** Baseline before changes: 107 offline tests passed and the starter app ran under AppTest. After changes: `uv run --locked python -m pytest -q` passed 137 tests. Expected answers in the tests are written by hand from PHASE2_SCOPE.md (Toledo 5939/60, Segovia 785/12, Seville 185/3; clock-change and five-day period lists). The tests cover inclusive bounds, out-of-window/night records, the 25 October 2026 clock change, the staleness boundary, identity/mixed-group, duplicate, missing-period and missing-metric reasons and their precedence, filters on the real 83-row catalog, ties, invalid inputs and no network use. Deliberately altered comparisons, the penalty cap, window end, staleness boundary and daytime bounds each made tests fail. The private handoff fixtures were compared optionally outside the repository and agree; they are not a repository or test dependency. No live request was made and no weather data was written.

**Kept / changed / rejected:** Kept the P2.4 entry point, field names, reason codes and precedence, and unrounded ordering. Added small public helpers so the Searcher can show the forecast window and the daytime boundaries can be tested directly. Chose to ignore off-grid, night and out-of-window records rather than reject them, because a full provider forecast always contains them. Rejected the starter comfort-index idea and any new thresholds or weights as outside the agreed scoring rules.

**Human review:** Christian directed the work. Selin (selin-atalar) approved PR #5 and merged it into dev on 12 November 2026. Genuine-data verification waits for Gabriel's P3.2 service and Asier's P2.5 check.

**Commit / PR:** Commit fa1d552; [PR #5](https://github.com/AsierMarmol/weather-insights/pull/5), merged into dev as 46675ea.

---

## Phase 3: P3.2 reusable API client and request/save service (2026-11-12)

**Requested by:** Gabriel Polan Barros Stec (Gabrielstec).

**AI collaborator:** Claude Code (Anthropic Claude Opus 5.5).

**Asked:** Synchronize the personal branch with the latest dev, which now includes the reviewed P3.1 models and store, then implement the owned P3.2 deliverable from PHASE3_CORE_DATA.md against the P2.4 specification and WEATHER_API_CONTRACT.md: a generic JSON API base class, an OpenWeatherMap subclass, the request/cache/save service and configuration loaders, with tests and documentation. Also record Gabriel's completed P2.1/P2.3 review in the Phase 2 log.

**Got:** `src/weather_app/client.py`: `JSONAPIClient` (key and key-parameter name held as name-mangled private attributes, masked `__repr__`, context manager, `request_count` property, protected `_get_json`/`_error_for_status`), a shared 40-calls/minute `RateLimiter`, `APIError` subclasses for each safe error code, and `OpenWeatherClient` (`request_parameters`, `current`, `forecast`, `map_current`, `map_forecast`, location checks, field mapping). `src/weather_app/service.py`: `WeatherService` with `current`, `forecast`, `forecast_many`, `retry_unsaved`, `clear_cache`, `unsaved_record_count` and `from_environment`. `src/weather_app/config.py`: `load_product_defaults()` and `load_location_overrides()` alongside the existing `get_api_key()`. Tests in `tests/test_client.py`, `tests/test_service.py`, `tests/test_config.py` and the offline doubles in `tests/weather_fakes.py`. Updates to PHASE3_CORE_DATA.md, PHASE2_SCOPE.md and README.md.

**Checked:** Baseline after synchronizing to dev `7ac93c1`: 107 offline tests passed. After changes: `uv run --locked python -m pytest -q` passed 172 tests (65 new). Tests use fake HTTP sessions, synthetic weather payloads and the real `WeatherStore` in pytest temporary directories. They cover every status/network failure code, one retry for transient failures only, no key in messages/reprs/exception chains, pacing including retries, Lugo's city-ID request, unit conversion, None for missing values, identity rejection, save-once-then-cache, TTL boundaries, reuse after restart, storage failure and recovery, and batch skip/stop behavior over the whole 83-city catalog. A read-only replay of the 168 retained genuine responses mapped all of them (84 current, 3,360 forecast periods) and passed every location check without HTTP or file writes. The replay found no problem; writing the tests found a boundary defect in the conversion (0.3 x 100 = 30.000000000000004), which was fixed by rounding conversions to nine decimals. Bounded live check with Gabriel's local key: Toledo current and forecast through `WeatherService.from_environment()`. It made 2 HTTP requests with no errors and saved 41 genuine rows to the new `data/weather/weather_records.csv` (1 current, 40 forecast periods, one fetch_id). Readback matched, and repeat or restarted-service calls caused no HTTP and no new rows. Full-catalog live requests were not run.

**Kept / changed / rejected:** Kept the P2.4 entry points, result dictionary and error codes, the contract's TTLs, pacing and Lugo override, and P3.1's store unchanged. Reused the 10 km plausibility tolerance from the P2.3 verification instead of inventing a new threshold. Classified identity mismatches as `invalid_data` to match the analytics reason codes. Kept saving inside the service only; the client maps but never saves. Rejected silently dropping unsaved data: a storage failure returns no records, and the batch is kept in memory and saved before the next write. Did not import the retained JSONL into `weather_records.csv`; that remains a team decision.

**Human review:** Gabriel directed the work and chose to start after P3.1 was merged, while Christian's P2.4 review is still outstanding. Alejandra's P3.2 review is pending; no approval is claimed.

**Commit / PR:** Pending.

---

## Phase 3: P3.3 integration with the API/save service and genuine data (2026-11-12)

**Requested by:** Christian Sawaya (christiansawaya-code).

**AI collaborator:** Claude Code (Anthropic Claude Opus 5.5).

**Asked:** Synchronize with the latest dev after Gabriel's P3.2 merge, then complete the remaining P3.3 dependency work: connect the analytics engine to the actual `WeatherService`/`WeatherStore` and check it on genuine saved forecasts.

**Got:** `forecasts_from_service()` in `src/weather_app/analytics.py`, which converts `WeatherService.forecast_many` results into the engine's `forecasts_by_city` input (errors give no records, so the city is `fetch_failed`). `tests/test_analytics_integration.py` with 5 tests: the real service with fake HTTP and a temporary store feeding the engine, cache reuse on rerun without new rows, save-and-reload equivalence for 1/3/5 days, adapter validation, and a read-only replay of the genuine Toledo forecast saved during the P3.2 live check.

**Checked:** Full suite after changes: 207 passed. Expected answers are by hand: the synthetic service case from the fake payload (18/19/20 C, 30 %, 10.8 km/h; scores 100 - 61/60 and 100 - 75/60), and the genuine Toledo one-day case from the three saved CSV rows inside the window (passes 2/0/1, score 100/3 - 61/60, mean 16.4 C). Five days give 15 complete genuine periods, and the same forecast four hours later is stale. The genuine CSV is byte-for-byte unchanged by the tests. A first draft wrongly expected no HTTP on rerun; the service correctly retries the failed city, and the test now asserts that.

**Kept / changed / rejected:** Kept the engine's interface unchanged and added only the adapter. Did not make a new live fetch: this machine's clock was about an hour off UTC, which would have saved wrong retrieval times. Did not import the retained JSONL evidence (a team decision noted in P3.2) and did not duplicate Asier's P2.5 verification.

**Human review:** Christian directed the work. Selin's review of this integration is pending; no approval is claimed.

**Commit / PR:** Pending.
