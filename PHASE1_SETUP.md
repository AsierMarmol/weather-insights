# Phase 1 - Team and Environment Setup

Updated: 11 November 2026.

## Current checkpoint

**Completed setup - carried out by Asier**, as explicitly confirmed by Asier. Keep this phase closed and retain the existing repository, Python/uv environment, package, credential protection and collaboration setup. Later role allocations do not reassign or imply authorship of the completed setup.

This is the setup reference for the project, not a new round of onboarding work. Historical evidence remains below with its original dates and observations. No new teammate-machine tests or remote merges are claimed by this documentation update.

Current work is tracked in [Project phases](PROJECT_PHASES.md) and [Phase 5](PHASE5_QUALITY_REVIEW.md). Future responsibilities are in [TEAMROLES.MD](TEAMROLES.MD); navigation and plan-maintenance rules are in [PROJECT_PHASES.md](PROJECT_PHASES.md). No commit, push or merge is authorized by this planning check.

## Next phase

Preserve the existing repository and environment; no setup restart is needed. Phase 2 was the next phase after setup and is now complete. The application has since been implemented; use the current checkpoint above for its acceptance status. The historical starter checks below prove setup only.

## Updating this phase when something changes

The task owner records the change and reason before dependent work continues. Check all six phase plans for impact, then update every affected step, dependency, finish condition and acceptance check in the same change. Also update the Phase 2 specification, TEAMROLES.MD, PROJECT_PHASES.md and application README when affected. Do not rewrite unaffected history or invent completion evidence.

Keep task IDs stable and assign one owner per broad deliverable, including its tests and documentation. If a previously completed check is invalidated, retain its old evidence and mark the affected task Needs recheck with a named owner; do not leave it silently Done. Distinguish Pending, In progress, Blocked (with reason), Needs recheck and Done (with evidence).

The implementation owner updates affected steps and records the change in the active phase's progress log. The named peer reviewer checks technical and documentation consistency. Follow [Plan maintenance](PROJECT_PHASES.md#plan-maintenance); no separate change register is required.

## Historical setup checklist and verification records

The following is the previous detailed setup record, retained with heading/navigation wording updated. Its dates, former locations, authorizations, branch snapshots and pending statements apply at the time they were recorded; they are not new actions or current publication authorization.

Updated: 10 November 2026.

Complete one step, verify its finish condition, and review the result before moving to the next step. Application design, API features, analytics, and data enrichment belong to later phases.

### Current checkpoint

Checkpoint: 10 November 2026. The environment, initial publication, and seven team/shared branches are in place. GitHub marks main/dev protected; prior screenshots show the selected review options. The first real PR still needs to exercise those requirements. The shared branches and asier/feature start from baseline 0223991; teammate branches can advance independently.

Asier reports that all four teammates have access and completed onboarding. He is collecting the individual Step 17 confirmations now; they are not yet recorded as received. Step 16 is in progress: [PR #1](https://github.com/AsierMarmol/weather-insights/pull/1) is open from asier/feature into dev, publishing [documentation commit a81d470](https://github.com/AsierMarmol/weather-insights/commit/a81d4708d3251f1d83b2ea9b6d1fbd8165f6c8dc). Gabriel (gabrielstec) is the intended reviewer; his review remains pending. Approval, merge into dev, reviewed promotion into main, and final confirmations remain pending. Phase 2 is drafted but has not begun.

The latest user request explicitly authorizes moving this plan into the repository, committing/publishing the documentation, and requesting Gabriel's review. It supersedes the earlier external-plan location and manual-only publication preference for this change. It does not authorize bypassing review or declaring a phase complete.

### Where phase plans belong

Keep PHASE1_SETUP.md, PHASE2_SCOPE.md, and future phase plans at the repository root beside the application README.md. These are shared team documents and are included in GitHub review. This placement follows Asier's updated instruction of 10 November 2026.

The instructor's assignment README.md and supporting summary.md remain external reference files in the local parent directory. Do not confuse the instructor's assignment with the application README or copy those reference files into the repository as part of this move. Installation remains self-contained in the application README.

Historical verification sections below describe the locations, files, and review status at the time of each check. Earlier references to an external phase plan document the former arrangement; the current location policy is the one in this section.

### Project locations

- Shared repository: <https://github.com/AsierMarmol/weather-insights>.
- Application setup and run instructions: [README.md](README.md).
- Current phase checklist: [PHASE1_SETUP.md](PHASE1_SETUP.md).
- Next phase draft: [PHASE2_SCOPE.md](PHASE2_SCOPE.md).
- Ongoing AI record: [PROMPTS.md](PROMPTS.md).
- External reference files available locally: the instructor's README.md and summary.md in the parent directory. They are not dependencies needed to install or run the app.

### Ordered checklist

| Step | Small action | Finish condition | Status |
| --- | --- | --- | --- |
| 1 | Confirm the new repository and copy the instructor starter into its root. | The Git root is `weather-insights`; `src/`, `tests/`, and `pyproject.toml` are directly inside it. | Done |
| 2 | Create `.venv`, select Python 3.14, install the package and dependencies, and add pytest. | Locked installation, dependency checks, package imports, starter test, and both starter views pass. | Done |
| 3 | Select the new environment in VS Code. | User screenshot confirms VS Code invoked this repository's `.venv\Scripts\python.exe` to run `app.py`. | Done |
| 4 | Finish local credential protection. | Secret variants and backups are ignored; safe examples remain publishable; loading is verified using dummy values. A blank local `variables.env` is ready for a personal key before API testing. | Done |
| 5 | Update the project README with verified setup and run instructions. | Self-contained Windows installation/run instructions passed fresh-copy and actual GitHub-clone checks. Team-machine results remain part of onboarding confirmation. | Done |
| 6 | Agree how to record AI assistance. | Root PROMPTS.md has the eight-field convention, preserved records, and Codex trailer. Initial setup attribution is published in 0223991; new changes retain their actual peer-review status. | Done |
| 7 | Configure Asier's Git identity for this repository. | Local author name is `AsierMarmol`; the exact user-supplied GitHub no-reply email and resolved author/committer identities are verified. Global settings are unchanged. | Done |
| 8 | Review and rerun verification of the initial snapshot. | The documented file, identity, credential, install, placeholder-test, and starter-view checks passed before the initial commit. Preserve this historical evidence without treating placeholder tests as feature coverage. | Done - verified before initial commit |
| 9 | Make the initial commit on `main`. | User-created commit `0223991f05005d0420c7be2c760c2c6850fbfd88` contains the 15 reviewed files, the correct no-reply author/committer, and the required Codex co-author trailer. Working tree is clean. | Done - performed manually |
| 10 | Push the initial `main` branch. | The user performed the first push manually. GitHub screenshot confirms `main`, commit `0223991`, the reviewed file layout, and Codex attribution. | Done - performed manually |
| 11 | Create `dev` from `main` and publish it. | Read-only Git verification confirms local `dev` tracks `origin/dev`, the working tree is clean, and published `main` and `dev` both point to `0223991`. | Done - performed manually |
| 12 | Create asier/feature from dev and publish it. | Asier's personal branch was created and published at 0223991 with the correct origin upstream. Current edits/publication status are recorded in the checkpoint above. | Done - performed manually and verified |
| 13 | Configure the branch and review rules. | GitHub marks main/dev protected; prior screenshots show the agreed review settings. Validate that an actual PR requires a peer approval and resolved conversations before merging. | Configured - protection flags verified; enforcement check in Step 16 |
| 14 | Invite the other four members and record the five-person team. | The user reports all four have access. Four teammate personal branches are published. Exact collaborator identities and initial responsibilities can be recorded when confirmed. | Done - access reported by user |
| 15 | Onboard all four teammates. | All four personal branches are published and onboarding is reported complete. Asier is collecting each person's starter-app, identity, and collaboration-rule confirmation under Step 17. | Reported complete - confirmations being collected |
| 16 | Exercise the PR process with a useful setup change. | [PR #1](https://github.com/AsierMarmol/weather-insights/pull/1) publishes the four documentation files from asier/feature into dev. Gabriel's review, protection enforcement check, merge into dev, and reviewed promotion into main remain pending. | PR open - awaiting Gabriel's review |
| 17 | Close Phase 1 together. | Asier confirms that all five can run the starter and understand branch, credential, and AI-record rules. Finish the reviewed setup PR workflow before closing the phase and starting Phase 2. | Pending - Asier is collecting confirmations |

### Alignment with the assignment and technical reference

Validated on 5 November 2026 against the complete instructor assignment README.md and technical summary.md, kept outside this repository. The instructor's assignment README is authoritative. The summary provides implementation patterns rather than extra deliverables.

| Requirement or reference | How Phase 1 addresses it | What remains after setup |
| --- | --- | --- |
| Assignment section 5 and summary section 8: a real GitHub repository, installable package, `src/` layout, and `pyproject.toml`. | Steps 1-2 preserve and verify the starter package; steps 8-12 establish the reviewed GitHub baseline and requested branches. | Keep the package installable as application features are added. |
| Assignment sections 2, 4, and submission rules; summary section 4: `variables.env` loaded through `python-dotenv`, with no key committed or exposed. | Step 4 reviews the inherited configuration and ignore rules; step 15 repeats the local credential setup for each teammate. | Environment loading was verified safely with dummy values in step 4; keep all later API errors, UI output, and logs free of keys. A live weather request is not needed to create the environment. |
| Assignment section 5: a top-level application README that supports a clean clone. | Steps 5 and 15 require self-contained install/run instructions and onboarding from other machines. | Describe implemented behavior accurately and verify a final clean clone before submission. |
| Assignment section 5 and summary section 9: a continuing root `PROMPTS.md` with actual requests, results, decisions, and named AI co-author trailers for substantially AI-authored code. | Step 6 establishes the convention; step 8 reviews the record before the first commit. `PROMPTS.md` and the shared phase plans now remain in the application repository. | Continue recording AI assistance as work happens and check relevant commit trailers. |
| Assignment team-collaboration rubric: every member contributes real commits and can explain any part of the code. | Steps 7 and 14-17 establish individual identities, access, working environments, and review practice. | Each of the five must make meaningful contributions during development and understand the whole application; completing onboarding alone does not satisfy the final team rubric. |
| Assignment data/submission rules and summary section 6: actual observations must accumulate with timestamps and the real data log must be submitted in Git. | Step 8 prevents blanket CSV/database ignore rules from excluding the eventual observation history. | Implement logging and begin collecting genuine observations as soon as API/storage features are ready. Do not fabricate history or treat an empty file as satisfying this requirement. |
| Assignment sections 1-4 and summary sections 1-3, 5-7: meaningful inheritance, encapsulation, a special method, a computed property, robust multi-location API calls, three analytical views across at least two categories, and two Streamlit views with interaction and two labeled charts. | The starter layout is retained and dependencies are ready. Phase 1 deliberately prepares the environment without implementing these features. | Design and implement these requirements in later phases. Empty starter pages and one arithmetic test do not establish compliance with these functional rubric rows. |
| Assignment submission rules: submit the repository URL; public is acceptable, or a private repository needs instructor access. | The selected repository is public. Step 14 covers the five team members' collaboration access. | Confirm the submission channel with the instructor and perform the final submission review later. |

#### Course requirements versus our setup choices

- **Required by the course:** the package/GitHub structure, root README and AI log, credential protection, individual contribution history, real logged data, and the functional requirements mapped above.
- **Chosen by this team:** Python 3.14, uv and its lockfile, VS Code, the `asier/feature` -> `dev` -> `main` branch flow, and working one small step at a time. The instructor starter allows Python 3.11 or newer; the assignment does not mandate Python 3.14 or particular branch names.
- **Helpful tooling, not separate grading requirements:** pytest, a PR template, automated checks, and branch-protection settings. These support reliable collaboration; optional automation is not a blocker for finishing Phase 1.
- **Updated team organization:** keep phase plans beside the application README in the repository. The instructor's assignment README and summary remain external references. Earlier records retain the old external-plan arrangement as historical evidence.

**Validation result:** the Phase 1 plan aligns with both reference documents as a setup phase. Credential protection, package installation, the published GitHub baseline, and the actual clean-clone setup checks are verified. The reviewed PR workflow and Asier's individual onboarding confirmations remain open; the completed ten-point functional rubric is not claimed by setup.

### Verified environment

- Interpreter: Python 3.14.7 in this project's `.venv`.
- Team version selection: `.python-version` contains `3.14`.
- Dependency resolution: `uv.lock` records exact application and development dependencies.
- Installable local package: `weather-app` 0.1.0, imported as `weather_app`.
- Test runner: pytest is declared in the development dependency group.
- `uv sync --locked`: passed.
- `uv pip check`: passed.
- `uv run --locked python -m pytest -q`: one instructor placeholder test passed. It only checks `1 + 1 == 2` and is not evidence that analytics exist.
- Package/dependency imports and automatic loading of both starter Streamlit views: passed without credentials or live API calls.
- Step 4 credential review passed: 22 ignore checks and four isolated loading checks. Local secret variants/backups are excluded while safe examples and real observation logs remain eligible for tracking. The personal key is not yet configured.

This setup created no commits, pushed nothing, and implemented no weather features. Step 3 is complete: the user screenshot confirms VS Code invoked the project-local `.venv\Scripts\python.exe`. The visible Streamlit ScriptRunContext warnings occurred because `app.py` was launched as an ordinary Python script. To open the web app from the project terminal, use `uv run --locked streamlit run app.py`.

### Credential protection verification

- The local `variables.env` file is ignored by Git. It was created blank; no real key was required or supplied.
- `variables.env.example` has a blank key and is eligible for tracking.
- Common environment-file variants/backups and `.streamlit/secrets.toml` are ignored.
- Configuration loading was tested using a temporary copy of the unchanged instructor code, dummy values, and a different working directory. Missing/blank keys raise the intended clear error; an existing environment variable takes precedence.
- No key was printed or transmitted, and no live API call was made. No possible secret files are currently tracked.
- CSV and SQLite observation history remain eligible for Git tracking, as required by the assignment. Actual history collection belongs to later API/storage work.
- A personal API key still needs to be added locally before real API testing. Credential protection is complete; live authentication has not been tested.

### Application README verification

- The application README includes portable PowerShell setup commands, safe credential-file creation, the correct Streamlit launch command, installation checks, troubleshooting, project structure, and honest starter status.
- Nine verification checks passed in a fresh local source copy with its own environment. The existing `.venv`, real `variables.env`, Git metadata, and external phase plans were not copied.
- Both starter views loaded with AppTest. Streamlit command syntax was checked without starting another server; the user had already verified the documented launch command in a browser.
- The lockfile and all application source files remained unchanged. The one passing pytest case is still an instructor placeholder rather than feature coverage.
- GitHub clone instructions remain conditional on publishing the baseline. Repeat verification with an actual remote clone after the first authorized push and during teammate onboarding.
- The application README and AI log remain inside the repository; this phase checklist remains outside it.

### AI collaboration convention verification

- Root PROMPTS.md uses the same eight fields for all substantive entries: Requested by, AI collaborator, Asked, Got, Checked, Kept / changed / rejected, Human review, and Commit / PR.
- Asked fields are professional summaries of the actual requests, including phase/step context; they are explicitly not verbatim quotations. Short chat navigation messages are expanded only using their established task context.
- The log begins with the user's Phase 1, Team and Environment Setup, and its purpose. It retains environment, credential protection, application README, and collaboration-convention records. Routine file movements do not receive separate development-log entries.
- The actual environment, credential, and fresh-source verification results were retained. Human review and commit/PR references are not invented. This formatting revision did not rerun application tests.
- The Codex trailer remains `Co-Authored-By: Codex <noreply@openai.com>`; its example was previously validated by Git's trailer parser without creating a commit. The README still links to the convention.
- The course attribution requirement covers substantial AI-authored code; the team also credits substantial AI-authored setup and documentation. Human authorship and the five-member contribution requirement are preserved.

### Initial snapshot review

Reviewed 15 untracked files on `main` for the new repository. The configured remote matches `AsierMarmol/weather-insights`; there are no existing commits, tracked files, or staged changes.

```text
.gitignore
.python-version
PROMPTS.md
README.md
app.py
pyproject.toml
src/weather_app/__init__.py
src/weather_app/analytics.py
src/weather_app/client.py
src/weather_app/config.py
src/weather_app/models.py
src/weather_app/storage.py
tests/test_analytics.py
uv.lock
variables.env.example
```

- Candidate-only checks found no common secret patterns or personal-email patterns. This is a targeted review, not a guarantee that a pattern scan detects every possible secret.
- The example key is blank. The private `variables.env` was not read and is excluded, together with environment files, backups, generated package/test files, and Streamlit secrets.
- Phase plans and assignment references remain outside the repository. Future genuine CSV/SQLite observation data remains eligible for tracking.
- All Python files parse and both TOML files parse. Source/configuration hashes and README command blocks match the fresh-source verification completed in Step 5. Its passing installation, dependency, placeholder-test, and two-view checks remain applicable; no redundant application test run was needed.
- The baseline is still a scaffold: no weather fetch, history logging, or analytic charts have been implemented, and the existing test is only a placeholder.
- The previously missing author identity is now configured: local name `AsierMarmol` and the exact GitHub no-reply email supplied by the user are verified. The file review and identity settings do not authorize a commit or push; human review and explicit commit approval remain pending.

### Git identity verification

- Step 7 is complete: local name `AsierMarmol` and the exact no-reply email shown in the user's GitHub settings are configured and effective.
- Both author and committer identity checks resolved to the selected account alias. Global Git name/email settings, HEAD, and the index were unchanged.
- No account-wide GitHub privacy settings were changed. The setting verified here applies to commits created through this local repository.
- The existing identity log entry was updated using the agreed eight-field structure. No separate screenshot or administrative entry was added.

### Step 8 verification rerun

The current 15-file baseline was freshly reverified after Git identity setup. The user's exact no-reply address is configured and effective for author and committer identities. All candidate checks, 24 ignore cases, blank example, source/TOML parsing, log structure, and proposed co-author trailer passed.

A fresh local source copy with a new `.venv` passed `uv sync --locked`, Python version, dependency consistency, package import, the existing pytest placeholder, Streamlit runner syntax, and both starter views. Credential-copy creation/preservation and four isolated dummy-value configuration checks also passed. The real `variables.env` was not read or copied. No real weather request was made, and no additional web server was started.

The original application files and lockfile were unchanged by verification. The existing Step 8 AI record was updated with the actual rerun results and its file fingerprint refreshed. Git HEAD and index remained unchanged; nothing is staged or committed.

The setup is technically ready for the initial commit. The existing test remains an arithmetic placeholder; weather API, storage, and analytics features belong to later phases. A real GitHub clone can be verified after the first authorized push.

Proposed initial commit message:

```text
chore: initialize Weather Insights starter

Add the installable starter package and Python 3.14 development setup.
Include locked dependencies, credential exclusions, setup instructions,
and the AI collaboration record.

Co-Authored-By: Codex <noreply@openai.com>
```

### Initial local commit verification

- The user manually created and amended commit `0223991f05005d0420c7be2c760c2c6850fbfd88` on `main`.
- Read-only verification confirmed the 15 reviewed files, the correct no-reply author and committer, a clean working tree, and the exact trailer `Co-Authored-By: Codex <noreply@openai.com>`.
- The original local commit was replaced by the user's amendment to add the trailer. The current subject is `initialize Weather Insights starter`; the optional conventional prefix is not an assignment requirement.
- The repository's tracked files were not edited during this verification. The assistant did not stage, amend, commit, or push anything. An update to the AI log can record this commit in a subsequent approved documentation change.

### First push confirmation

The user performed Step 10 manually. Their GitHub screenshot shows the public weather-insights repository on `main`, one commit with short ID `0223991`, the reviewed source/configuration/documentation files, and AsierMarmol plus Codex attribution. One branch is shown; `dev` and `asier/feature` are still pending. This confirmation is based on the screenshot, not a new clone test. A clean-clone verification remains part of onboarding/final validation.

### Development branch verification

Step 11 is complete. Read-only local branch/status checks and `git ls-remote` confirm `main` and `dev` are both published at commit `0223991f05005d0420c7be2c760c2c6850fbfd88`. The current local branch is `dev`, its upstream is `origin/dev`, and the working tree is clean. The assistant did not create or push branches.

### Audit against the assignment and best practices

Completed on 5 November 2026 against the authoritative assignment README and technical summary beside this plan, the live local/remote branch state, the published commit, and an actual temporary GitHub clone. GitHub metadata also confirms a public repository, default branch `main`, and owner administration permission. No repository files, commits, branches, GitHub permissions, or private credentials were changed during this audit.

| Area | Evidence and result | Course alignment |
| --- | --- | --- |
| Repository and branches | All three local/published branches resolve to `0223991`; each local branch tracks the corresponding origin branch. The working tree is clean and the published default is main. | The shared repository foundation is correct. Exact branch names and the dev integration layer are team choices, not teacher requirements. |
| Package and dependencies | Actual GitHub clone contains the 15 intended files. `uv sync --locked`, Python 3.14 selection, dependency consistency, and importing the installed local package succeed. | README section 5 and summary section 8: installable package, src layout, pyproject, and working clean-clone instructions. |
| Credentials and history files | Published example is blank. Candidate pattern checks and ignore rules pass. Real variables.env, local environments, and phase plans are absent from the clone; genuine CSV/SQLite history remains eligible for tracking. | README API/submission rules and summary section 4. Real observation collection still belongs to later API/storage work. |
| AI attribution | Published initial commit uses the selected human no-reply identity and the required Codex trailer. Root PROMPTS.md has seven consistently structured substantive entries and clearly labeled contextual summaries. | README AI-collaboration rules and summary section 9. Continue recording actual output, verification, decisions, and true commit/PR references. |
| Starter UI and checks | The existing placeholder pytest case passes. Both starter views load in the cloned environment; runner syntax is valid. The credential-copy command creates a blank file and preserves an existing dummy file. | Valid setup evidence. The arithmetic test and empty views do not establish completed weather/analytics functionality. |
| Team contribution evidence | Only Asier has a human-authored commit so far. Codex attribution is AI assistance, not a second student contributor. | All five students must eventually make meaningful contributions and understand any part of the code; onboarding alone is not final grading evidence. |
| Functional rubric | API/OOP classes, robust real requests, persistent timestamped observations, analytical calculations, interaction, and real charts are still placeholders or unimplemented. | Expected later-phase work: these requirements are not claimed complete by Phase 1 setup. |

#### Documentation follow-up identified at the 5 November audit

1. Update the application README's branch-status wording: all three branches are now published, while protection/review settings remain to be configured.
2. Update the AI record with the real initial commit reference and the user's completed manual commit, push, and branch outcomes. Preserve historical verification and do not invent PRs or approvals.
3. Keep these as a focused documentation change on the personal branch, reviewed into dev and then promoted to main through the agreed process after review rules and collaborator access are ready. This is a useful first PR exercise; it is not a reason to rewrite the published baseline.

#### Remaining work at the 5 November audit

- Step 13: configure and verify main/dev protection and PR rules. A peer approval and resolved review conversations are the selected team policy. GitHub's documentation supports protected branches for public repositories; no existing enforcement was assumed by this audit.
- Step 14: invite the other four intended teammates and verify acceptance.
- Step 15: each teammate verifies a clone/environment and their own Git identity on their actual machine. This audit validated Windows, not every teammate's operating system.
- Step 16: exercise review with the focused documentation update. A PR template and CI checks are optional additions; require automated checks only after a real workflow exists and succeeds.
- Step 17: close the phase only when the five-person working setup is confirmed. Continue meaningful contributions and AI records throughout later development.

Reference for the collaboration practices: [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) and [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

**Audit conclusion:** completed setup is technically sound and aligned with the teacher's setup requirements. The real clean-clone check now passes. No blocking setup defect was found before Step 13. Documentation status needs a normal follow-up PR, and the team/functional grading requirements remain work in progress.

### Next action only

Request and await Gabriel's review of [PR #1](https://github.com/AsierMarmol/weather-insights/pull/1). Do not merge before the required review. Asier is collecting Step 17 confirmations in parallel. After the approved change is merged into dev, promote reviewed dev into main through another reviewed PR. Close Phase 1 only when that workflow and the confirmations are complete, then start Phase 2 using PHASE2_SCOPE.md.

### Team onboarding checkpoint - 10 November 2026

- User report: all four teammates have access and supposedly completed the local setup steps. Treat individual machine checks as reported until confirmed; do not rerun or claim tests on their behalf.
- GitHub evidence: Alejandra/feature, christian/feature, gabrielstec/feature, selin/feature, and asier/feature are published alongside main/dev. All seven branches resolve to 0223991f05005d0420c7be2c760c2c6850fbfd88.
- Protection evidence: GitHub's branch listing returns protected=true for main/dev and false for each personal branch. This verifies that protection exists, rather than proving every configured review requirement. Earlier screenshots establish the selected options; an actual PR will exercise them.
- Local evidence: asier/feature is clean at the initial commit and tracks origin/asier/feature. The local shell could not reach GitHub; the connected GitHub API supplied the live remote evidence instead.
- No application tests were rerun for this tracking-only update. Repository source, README, PROMPTS, Git state, GitHub settings, and private credentials were unchanged.

### Step 16 documentation preparation - 10 November 2026

- Updated the repository README's stale branch/publication status, exact personal branch names, selected review policy, PR sequence, and reported onboarding status.
- Preserved the seven historical PROMPTS entries and added two eight-field records covering the documented manual setup/publication outcomes and this first documentation change. Linked the real initial commit 0223991 and left actual review/publication of the new documentation pending.
- Verification passed: README command blocks unchanged, nine uniform log entries, preserved historical content, local Markdown links, code fences, whitespace, only two unstaged documentation files changed, unchanged HEAD/index and other 13 tracked files. No application tests were rerun for these documentation-only edits.
- Live branch metadata still shows main/dev protected and the five personal branches published. Teammate branches may advance independently; the latest check showed gabrielstec/feature ahead of the initial baseline. No claim about its contents or authorship is made here.
- User review, manual commit/push, peer-reviewed PRs, protection enforcement, and per-person onboarding confirmations remain open. Phase 1 is not closed yet.

### Authorized publication and Phase 2 planning - 10 November 2026

- Asier explicitly requested that this phase plan return to the repository root beside README.md and that the documentation be committed/published from asier/feature for Gabriel's review into dev. This supersedes the earlier location/manual-publication preference for this task.
- Gabriel's account is gabrielstec; connected GitHub checks confirm write access. A review request is authorized. Approval, merge, and Step 17 confirmations are not claimed by this preparation record.
- PHASE2_SCOPE.md uses the same ordered-checklist/finish-condition structure. It is a draft for ideation and project flexibility, including minimum scope, real-history planning, meaningful OOP, analytics/UI decisions, optional enrichment, and five-person responsibilities.
- Asier is collecting the team confirmations. Phase 1 remains open until review/promotion and confirmations are complete; no weather feature is implemented by this documentation change.
- Publication: [documentation commit a81d470](https://github.com/AsierMarmol/weather-insights/commit/a81d4708d3251f1d83b2ea9b6d1fbd8165f6c8dc) and [PR #1 into dev](https://github.com/AsierMarmol/weather-insights/pull/1). Gabriel's review and Step 17 confirmations remain pending. No credentials or instructor reference files are included in the publication.
