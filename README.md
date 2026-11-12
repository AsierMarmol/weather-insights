# Weather Insights

A five-person Python/Streamlit project recommending mainland-Spain car trips from Madrid using weather preferences and driving time.

## Current status

Phase 1 setup and the reviewed Phase 2/3 foundation are complete for interface development. Gabriel and Christian approved P2.5 in merged PR #9. P4.1 Searcher (editable preferences, catalog filters, top-five recommendations, full ranking, coverage/freshness and safe unavailable states) was approved and merged. P4.2 Dashboard (ranking, weather comparison and all-preferences charts over the same results) is implemented and awaiting review; P4.3 integration remains pending. Source limitations remain documented.

Searcher behavior: rolling next 1-5 days (default 3), adjustable seasonal temperature preferences, rain <=30%, wind <=25 km/h and All activity/size filters. Weather matching earns points; driving time subtracts up to five. Searcher shows five leading recommendations and the full ranking. The Dashboard shows ranking, weather comparison and periods meeting all preferences as labeled charts and tables of the same search results. Every fresh successful weather fetch saves automatically.

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
git clone --branch dev https://github.com/AsierMarmol/weather-insights.git
Set-Location -LiteralPath .\weather-insights
uv sync --locked
```

During development, clone `dev` to get the reviewed team version; work on your own feature branch before making changes. The final submission will use reviewed `main`.

If you already have the project open, run only `uv sync --locked` from the directory containing `pyproject.toml` and `uv.lock`.

This creates `.venv`, installs the local `weather-app` package and its dependencies, and includes the development tools pytest and Flake8. `--locked` uses the checked-in dependency resolution and reports an error if it no longer matches `pyproject.toml`. Share `.python-version` and `uv.lock` with the team; each person creates their own `.venv`.

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

The key can remain blank while you explore the Searcher controls. Configure it before clicking Search destinations or deliberately running the live API diagnostic.

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

In **Searcher**, choose the next 1-5 days, comfortable temperature range, maximum precipitation probability and wind. Activities and size default to **All**; remove All before choosing specific values (an empty selection also means All). Click **Search destinations** to request forecasts for matching cities. A full 83-city search can take a few minutes because requests are paced. Each fresh successful response saves automatically; suitable saved forecasts are reused.

The top five recommendations and full ranking use identical scores. Unavailable cities have an explanation rather than a zero score. Results show their search window, preferences, forecast age and coverage. Editing controls does not fetch automatically; click Search again to update results. **Reset to seasonal defaults** resets preferences explicitly; normal reruns/navigation preserve your choices. Driving estimates are one-way from Madrid Km0 and do not include live traffic.

Open **Dashboard** after a search to compare the same results: the suitability ranking, a weather comparison (mean temperature, highest period precipitation probability or highest period wind) and the share of daytime periods meeting all your preferences. Destination, activity and size filters default to **All** and only narrow what is shown; they make no requests and do not change your search settings. Search again in Searcher to change days or preferences. Stop the app with **Ctrl + C** in its terminal.

## Verify the installation

```powershell
uv run --locked python --version
uv pip check
uv run --locked python -c "import weather_app; print('weather_app import OK')"
uv run --locked python -m pytest -q
uv run --locked flake8 src tests scripts app.py
```

Expect Python 3.14.x, compatible dependencies, a successful package import and passing offline tests. Tests cover configuration, the diagnostic, models, catalog loading, storage, the analytics engine, the API client and the request/save service. Simulated requests and writes use fake HTTP and temporary files; genuine-data replay tests read fixed saved fetch groups without modifying them. Searcher interaction tests use headless AppTest with fake HTTP/temp stores or a read-only historical replay; Dashboard tests use AppTest with synthetic rows, a read-only genuine replay and a fake-HTTP search-to-Dashboard journey; final end-to-end integration (P4.3) remains pending. Synthetic tests do not write to the genuine weather dataset. Run Flake8 before committing; a successful run prints no findings. Keep Python lines within 79 characters and wrap long expressions, comments and docstrings rather than suppressing the checks.

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
| app.py | Navigation between the Searcher and Dashboard views |
| src/weather_app/ | Installable package: configuration (`config.py`), domain models (`models.py`), catalog/weather storage (`storage.py`), OpenWeather client (`client.py`), request/save service (`service.py`) analytics/ranking engine (`analytics.py`), Searcher controls/presentation (`searcher.py`) and Dashboard views/charts (`dashboard.py`) |
| tests/ | Offline diagnostic, configuration, model, storage, analytics, client, service, Searcher and Dashboard tests (fake HTTP and temporary files only); further component tests added with implementation |
| scripts/verify_weather_access.py | Optional bounded live diagnostic, not the production service |
| data/reference/ | Nine-column catalog, product defaults, provider overrides and source notes |
| data/weather/ | Genuine timestamped responses and run summaries; normalized application CSV now contains 164 records across three cities |
| PHASE1_SETUP.md through PHASE6_DELIVERY.md | Owned tasks, dependencies and actual progress |
| PROJECT_PHASES.md / TEAMROLES.MD | Navigation and whole-component ownership |
| WEATHER_API_CONTRACT.md | Provider fields, requests and safe save/error rules |
| PROMPTS.md | Actual AI collaboration record |
| pyproject.toml / uv.lock / .python-version | Package/dependencies and shared Python selection |

## Team workflow

Use personal branch -> reviewed dev -> reviewed main. Existing personal branches are `asier/feature`, `Alejandra/feature`, `christian/feature`, `gabrielstec/feature` and `selin/feature`; preserve their exact capitalization. Start from current dev, push the personal branch and request a teammate's review before merging. The selected main/dev protections require one approval, renewed approval after changes and resolved conversations, including for the owner. Check live enforcement when publishing; this cleanup did not change GitHub settings.

Each member owns a complete implementation with tests/docs/fixes and makes genuine contributions. [TEAMROLES.MD](TEAMROLES.MD) records assignments, not proof of authorship. Follow the actual-tool logging and co-author convention in [PROMPTS.md](PROMPTS.md). Codex-authored work uses `Co-Authored-By: Codex <noreply@openai.com>`; credit other tools only when actually used.

## Data and development

Read the [catalog sources](data/reference/README.md), [saved-data record](data/weather/README.md), [API contract](WEATHER_API_CONTRACT.md) and [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). The CSV remains 83 destinations and nine fields; weather records are separate. Christian approved the catalog foundation in PR #3; retain the source/access limitations described in its notes. Genuine development weather must be retained and submitted; no scheduler or historical-trend chart is required.

The optional live diagnostic commands are documented in the API contract. They make real requests and append data; ordinary tests are offline. Do not run repeated full-catalog checks merely to reproduce old reports.

Start at [PROJECT_PHASES.md](PROJECT_PHASES.md). Next: Asier reviews P4.2 Dashboard, then P4.3 completes integration of both views. Pending functionality is not claimed complete by passing setup/diagnostic tests. A final clean-clone run and real contributions from all five remain delivery requirements.
