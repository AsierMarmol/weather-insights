# Weather Insights

A five-person Python/Streamlit project recommending mainland-Spain car trips from Madrid using weather preferences and driving time.

## Current status

Phase 1 setup is complete. Phase 2 product rules, 83-city catalog, API contract and shared specification are prepared; peer/source reviews remain open. The application currently displays Searcher and Dashboard headings only. Domain models, catalog loading and the weather-record store (P3.1) are reviewed and merged. The pure analytics/ranking engine (P3.3) is implemented and awaiting review; production weather retrieval, controls and charts remain pending.

Planned behavior: rolling next 1-5 days (default 3), adjustable seasonal temperature preferences, rain <=30%, wind <=25 km/h and All activity/size filters. Weather matching earns points; driving time subtracts up to five. Searcher shows five leading recommendations and the full ranking. Dashboard provides ranking, weather comparison and periods meeting all preferences, with at least two real-data charts. Every fresh successful weather fetch saves automatically.

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

The key can remain blank while you explore the starter interface. Configure it before deliberately running the live API diagnostic or later application requests.

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

Switch between **Searcher** and **Dashboard** in the sidebar. Both currently show starter headings; empty views are expected at this stage. Stop the app with **Ctrl + C** in its terminal.

## Verify the installation

```powershell
uv run --locked python --version
uv pip check
uv run --locked python -c "import weather_app; print('weather_app import OK')"
uv run --locked python -m pytest -q
```

Expect Python 3.14.x, compatible dependencies, a successful package import and passing offline tests. Tests cover configuration, the diagnostic, models, catalog loading, storage and the analytics engine; the production API and application features remain pending. Synthetic tests do not write to the genuine weather dataset.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `uv` is not recognized | Install uv using the official instructions above, then reopen the terminal. |
| `missing ScriptRunContext` warnings appear after using VS Code's Run Python File button | Launch the app with `uv run --locked streamlit run app.py` in the terminal. Streamlit needs its own runner. |
| `OPENWEATHER_API_KEY is not set` appears when requesting API access | Fill the key in your local `variables.env` or supply it through the environment. Retry after saving the file. |
| Port 8501 is already in use | Stop your other server or run `uv run --locked streamlit run app.py --server.port 8502`. Follow the Local URL printed by that process. |
| `uv sync --locked` reports that the lockfile is outdated | Check that `pyproject.toml` and `uv.lock` came from the same reviewed change. Coordinate dependency updates with the team and include both files in that change. |


## Project structure

| Location | Purpose |
| --- | --- |
| app.py | Streamlit entry point; currently two starter views |
| src/weather_app/ | Installable package: configuration, domain models (`models.py`) and catalog/weather storage (`storage.py`), analytics/ranking engine (`analytics.py`); client placeholder |
| tests/ | Offline diagnostic, configuration, model and storage tests (temporary files only); further component tests added with implementation |
| scripts/verify_weather_access.py | Optional bounded live diagnostic, not the production service |
| data/reference/ | Nine-column catalog, product defaults, provider overrides and source notes |
| data/weather/ | Genuine timestamped responses and run summaries; normal application CSV comes with storage implementation |
| PHASE1_SETUP.md through PHASE6_DELIVERY.md | Owned tasks, dependencies and actual progress |
| PROJECT_PHASES.md / TEAMROLES.MD | Navigation and whole-component ownership |
| WEATHER_API_CONTRACT.md | Provider fields, requests and safe save/error rules |
| PROMPTS.md | Actual AI collaboration record |
| pyproject.toml / uv.lock / .python-version | Package/dependencies and shared Python selection |

## Team workflow

Use personal branch -> reviewed dev -> reviewed main. Existing personal branches are `asier/feature`, `Alejandra/feature`, `christian/feature`, `gabrielstec/feature` and `selin/feature`; preserve their exact capitalization. Start from current dev, push the personal branch and request a teammate's review before merging. The selected main/dev protections require one approval, renewed approval after changes and resolved conversations, including for the owner. Check live enforcement when publishing; this cleanup did not change GitHub settings.

Each member owns a complete implementation with tests/docs/fixes and makes genuine contributions. [TEAMROLES.MD](TEAMROLES.MD) records assignments, not proof of authorship. Follow the actual-tool logging and co-author convention in [PROMPTS.md](PROMPTS.md). Codex-authored work uses `Co-Authored-By: Codex <noreply@openai.com>`; credit other tools only when actually used.

## Data and development

Read the [catalog sources](data/reference/README.md), [saved-data record](data/weather/README.md), [API contract](WEATHER_API_CONTRACT.md) and [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). The CSV remains 83 destinations and nine fields; weather records are separate. Source/activity/access review is still pending. Genuine development weather must be retained and submitted; no scheduler or historical-trend chart is required.

The optional live diagnostic commands are documented in the API contract. They make real requests and append data; ordinary tests are offline. Do not run repeated full-catalog checks merely to reproduce old reports.

Start at [PROJECT_PHASES.md](PROJECT_PHASES.md). Next: finish the Phase 2 reviews, build the three Phase 3 components, then have Asier verify their single fetch/save path in P2.5. Pending functionality is not claimed complete by passing setup/diagnostic tests. A final clean-clone run and real contributions from all five remain delivery requirements.
