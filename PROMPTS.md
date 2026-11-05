# AI collaboration log

Keep this file at the repository root and update it while work happens. Record each substantial AI-assisted feature, class, or setup task. A brief explanation or routine command does not need its own entry unless it changes a meaningful decision or result. Routine file moves and editorial housekeeping do not need separate entries; keep the record focused on substantive planning, setup, and development.

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
