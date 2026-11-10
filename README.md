# Weather Insights

A Python weather analytics project using OpenWeatherMap and Streamlit, developed by a team of five.

## Current status

The project is at the setup stage. The starter app opens two views, **Live Conditions** and **Analytics**, with headings and sidebar navigation. Weather requests, saved observations, analytical calculations, and charts are still to be implemented.

You can run the starter interface without an API key. Importing the API configuration requires a configured key; live authentication has not been tested yet.

## Requirements

These instructions use **Windows PowerShell**.

- [Git](https://git-scm.com/downloads) for cloning and collaboration.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python and dependency management. Setup was verified with uv 0.12.23.
- Python **3.14**, selected by `.python-version`. uv can download it if it is not already installed; setup was verified with Python 3.14.7.
- VS Code with the Python extension is recommended.

If uv is missing, use its official installation instructions. On Windows with WinGet:

```powershell
winget install --id astral-sh.uv --exact
```

Open a new terminal after installation so `uv` is available.

## Get the project and install dependencies

Run these commands from a folder where you want to keep your clone:

```powershell
git clone https://github.com/AsierMarmol/weather-insights.git
Set-Location -LiteralPath .\weather-insights
uv sync --locked
```

If you already have the project open, run only `uv sync --locked` from the directory containing `pyproject.toml` and `uv.lock`.

This creates `.venv`, installs the local `weather-app` package and its dependencies, and includes the development tools such as pytest. `--locked` uses the checked-in dependency resolution and reports an error if it no longer matches `pyproject.toml`. Share `.python-version` and `uv.lock` with the team; each person creates their own `.venv`.

## Configure your local API key

Create your local credential file if it does not exist:

```powershell
if (-not (Test-Path -LiteralPath .\variables.env)) {
    Copy-Item -LiteralPath .\variables.env.example -Destination .\variables.env
}
```

The guard preserves an existing credential file. Open `variables.env` locally and enter your personal [OpenWeatherMap API key](https://openweathermap.org/appid) after the equals sign:

```dotenv
OPENWEATHER_API_KEY=
```

The key can remain blank while you explore the starter interface. Configure it before testing actual weather requests later in development.

`variables.env` and common secret-file variants are excluded by `.gitignore`. Keep `variables.env.example` blank and safe to publish. Keep real keys out of commits, screenshots, chat, logs, and the app interface. The configuration uses `python-dotenv` to load this file from the project root; an existing `OPENWEATHER_API_KEY` environment variable takes precedence.

## Select Python in VS Code

1. Open this repository folder in VS Code.
2. Press **Ctrl + Shift + P** and select **Python: Select Interpreter**.
3. Choose the workspace interpreter ending in `.venv\Scripts\python.exe`.

It may be labeled **weather-app (3.14.x)** because `weather-app` is the package name. Python code imports the package as `weather_app`.

The `uv run` commands below use the project environment automatically, so manual environment activation is not necessary.

## Run the app

From the project directory:

```powershell
uv run --locked streamlit run app.py
```

If Streamlit asks for an email during its welcome prompt, you can leave it blank and press Enter. Follow the **Local URL** printed in the terminal, usually [http://localhost:8501](http://localhost:8501).

Switch between **Live Conditions** and **Analytics** in the sidebar. Both currently show starter headings; empty views are expected at this stage. Stop the app with **Ctrl + C** in its terminal.

## Verify the installation

```powershell
uv run --locked python --version
uv pip check
uv run --locked python -c "import weather_app; print('weather_app import OK')"
uv run --locked python -m pytest -q
```

Expect Python 3.14.x, compatible installed dependencies, a successful package import, and one passing starter test. That test is currently an arithmetic placeholder. It does not verify weather retrieval or analytics; meaningful feature tests will be added with implementation.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `uv` is not recognized | Install uv using the official instructions above, then reopen the terminal. |
| `missing ScriptRunContext` warnings appear after using VS Code's Run Python File button | Launch the app with `uv run --locked streamlit run app.py` in the terminal. Streamlit needs its own runner. |
| `OPENWEATHER_API_KEY is not set` appears when importing the API configuration | Fill the key in your local `variables.env` or supply it through the environment. Restart the app after changing configuration. |
| Port 8501 is already in use | Stop your other server or run `uv run --locked streamlit run app.py --server.port 8502`. Follow the Local URL printed by that process. |
| `uv sync --locked` reports that the lockfile is outdated | Check that `pyproject.toml` and `uv.lock` came from the same reviewed change. Coordinate dependency updates with the team and include both files in that change. |

## Project structure

```text
weather-insights/
|-- .python-version          # Shared Python series
|-- .gitignore               # Local environments, generated files, and secrets
|-- pyproject.toml           # Package metadata and dependencies
|-- uv.lock                  # Resolved dependency versions
|-- app.py                   # Streamlit entry point
|-- variables.env.example    # Blank credential example, safe to publish
|-- variables.env            # Local credentials; ignored by Git
|-- .venv/                   # Local environment; ignored by Git
|-- src/
|   `-- weather_app/
|       |-- __init__.py
|       |-- config.py        # Environment loading
|       |-- client.py        # API client placeholder
|       |-- models.py        # Object model placeholder
|       |-- storage.py       # Observation persistence placeholder
|       `-- analytics.py     # Analytics placeholder
|-- tests/                   # Currently one starter placeholder test
|-- PHASE1_SETUP.md          # Team/environment checklist and evidence
|-- PHASE2_SCOPE.md          # Ideation and project-flexibility draft
`-- PROMPTS.md               # Ongoing AI collaboration record
```

## Project phases

Shared phase plans live beside this README and are reviewed with the repository:

- [Phase 1 - Team and Environment Setup](PHASE1_SETUP.md): final review and team confirmations are in progress.
- [Phase 2 - Ideation and Project Flexibility](PHASE2_SCOPE.md): an ordered draft for agreeing on the product, scope, data/history, OOP, analytics, optional enrichment, and team responsibilities. It begins after Phase 1 closes.

## Team collaboration

The team has five members. Names and contribution summaries will be recorded as responsibilities and work are agreed.

The agreed branch flow is `<member>/feature` -> `dev` -> `main`. `main` holds the stable shared version; `dev` brings together reviewed team changes. Both branches are published and protected.

The five published personal branches are `Alejandra/feature`, `asier/feature`, `christian/feature`, `gabrielstec/feature`, and `selin/feature`. Use the exact branch names, including capitalization. Personal branches remain available for normal commits and pushes.

The team's selected protection settings require a pull request, one approving teammate, fresh approval after new commits, and resolved review conversations before changes enter `dev` or `main`. The selected settings also apply to the repository owner and keep force pushes and branch deletion disabled. The first reviewed PR will verify that these requirements are enforced; protection is enabled, but the complete review-and-merge workflow has not yet been exercised.

1. Start personal work from the latest `dev` and make a focused change on your own branch.
2. Push your branch, open a PR with `dev` as the base, and ask another teammate to review it. Address feedback before merging and preserve the relevant author/co-author attribution.
3. Promote reviewed changes from `dev` to `main` through another reviewed PR.

Asier reports that all four teammates have repository access and have completed local onboarding. Published personal branches are verified. Asier is collecting each person's confirmation that the starter app runs and that they understand the branch, credential, and AI-record rules. The documentation PR and these confirmations are the remaining Phase 1 checkpoints.

Use your own Git identity and make meaningful contributions. Follow the [AI collaboration convention and reusable entry template in PROMPTS.md](PROMPTS.md). Log substantial AI-assisted work while it happens, including actual checks and what was kept, changed, or rejected. Use `Co-Authored-By: Codex <noreply@openai.com>` on commits containing substantial Codex-authored code, setup, or documentation, and preserve attribution when merging. Other AI tools must be credited accurately. AI credit does not replace the five members' own meaningful contributions.

When observation logging is implemented, retain genuine timestamped weather history and include the collected data in Git. Do not fabricate observations or blanket-ignore the CSV/SQLite history needed for the final submission.
