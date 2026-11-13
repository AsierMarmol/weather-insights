# Weather Insights

A five-person Python/Streamlit project recommending mainland-Spain car trips from Madrid using weather preferences and driving time.

## Current status

The Searcher and independent Dashboard are implemented. Phases 1-4 and P5.1-P5.4 are reviewed and merged. P5.5 was approved by Gabriel and merged in PR #19 (dev `2999dae`). Mac test results and desktop/mobile visual confirmation remain unconfirmed. P6.1 delivery documentation is pushed for review; a storage-recovery follow-up is tested locally and awaits review before final delivery; P6.2 clean-clone verification and P6.3 submission remain pending. See [Project phases](PROJECT_PHASES.md) for PR history, owners and remaining gates.

Searcher behavior: rolling next 1-5 days (default 3), adjustable seasonal temperature preferences, rain <=30%, wind <=25 km/h and All activity/size filters. Weather matching earns points; driving time subtracts up to five. Searcher shows five leading recommendations and the full ranking. The Dashboard is an independent weather overview: a map of all 83 destinations ranked by weather alone for its own next 1-5 days, with weather comparison and all-criteria charts. Every fresh successful weather fetch saves automatically.

## Requirements

Use **Windows PowerShell** or **macOS Terminal** as labeled below. Shared `uv` commands work in both; no environment activation is needed.

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

On Windows, run these commands from a folder where you want to keep your clone:

```powershell
git clone --branch dev https://github.com/AsierMarmol/weather-insights.git
Set-Location -LiteralPath .\weather-insights
uv sync --locked
```

On macOS, after installing Git and uv using their official instructions:

```bash
git clone --branch dev https://github.com/AsierMarmol/weather-insights.git
cd weather-insights
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

On macOS:

```bash
if [ ! -e variables.env ]; then
    cp variables.env.example variables.env
fi
```

Both guards preserve an existing credential file. Open `variables.env` locally and enter your personal [OpenWeatherMap API key](https://openweathermap.org/appid) after the equals sign:

```dotenv
OPENWEATHER_API_KEY=
```

The key can remain blank while you explore the Searcher controls. Configure it before clicking Search destinations or deliberately running the live API diagnostic.

`variables.env` and common secret-file variants are excluded by `.gitignore`. Keep `variables.env.example` blank and safe to publish. Keep real keys out of commits, screenshots, chat, logs, and the app interface. The configuration uses `python-dotenv` to load this file from the project root; an existing `OPENWEATHER_API_KEY` environment variable takes precedence.

## Select Python in VS Code

1. Open this repository folder in VS Code.
2. Press **Ctrl + Shift + P** and select **Python: Select Interpreter**.
3. Choose the workspace interpreter ending in `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS. On macOS, open the command palette with **Cmd + Shift + P**.

It may be labeled **weather-app (3.14.x)** because `weather-app` is the package name. Python code imports the package as `weather_app`.

The `uv run` commands below use the project environment automatically, so manual environment activation is not necessary.

## Run the app

From the project directory:

```powershell
uv run --locked streamlit run app.py
```

If Streamlit asks for an email during its welcome prompt, you can leave it blank and press Enter. Follow the **Local URL** printed in the terminal, usually [http://localhost:8501](http://localhost:8501).

In **Searcher**, choose the next 1-5 days, comfortable temperature range, maximum precipitation probability and wind. Activities and size default to **All**; choosing a specific value clears All, while choosing All or clearing the selection restores it. Click **Search destinations** to request forecasts for matching cities. A full 83-city search can take a few minutes because requests are paced. Each fresh successful response saves automatically; suitable saved forecasts are reused.

The top five recommendations and full ranking use identical scores. Unavailable cities have an explanation rather than a zero score. Results show their search window, preferences, forecast age and coverage. Editing controls does not fetch automatically; click Search again to update results. **Reset to seasonal defaults** resets preferences explicitly; normal reruns/navigation preserve your choices. Driving estimates are one-way from Madrid Km0 and do not include live traffic.

Open **Dashboard** at any time; it does not need a Searcher run. A map shows all 83 destinations. Choose the next 1-5 days (default 3) and click **Load weather overview** to rank every destination by weather alone using the seasonal temperature range, precipitation probability <=30% and wind <=25 km/h (no driving penalty; equal scores share a rank). Hover over a marker for its activities, average daytime temperature, weather rank and score; grey markers have no weather rank yet and explain why. Saved forecasts under three hours old are reused and others are fetched and saved automatically; a first full load can take about two minutes. Tabs compare weather and show the share of three-hour daytime forecast slots meeting all three criteria (9/9 means all nine required slots have data, not nine days or hours of good weather). Filters only highlight markers and narrow the charts; they never remove destinations, change ranks or make requests. Dashboard and Searcher keep separate settings and results but share the same saved forecasts. Stop the app with **Ctrl + C** in its terminal. Run one Streamlit process per clone: file-write locking coordinates sessions in that process, not separately launched servers.

## Verify the installation

```powershell
uv run --locked python --version
uv pip check
uv run --locked python -c "import weather_app; print('weather_app import OK')"
uv run --locked python -m pytest -q
uv run --locked flake8 src tests scripts app.py
```

Expect Python 3.14.x, compatible dependencies, a successful package import and passing offline tests. Tests cover configuration, the diagnostic, models, catalog loading, storage, the analytics engine, the API client and the request/save service. Simulated requests and writes use fake HTTP and temporary files; genuine-data replay tests read fixed saved fetch groups without modifying them. Searcher interaction tests use headless AppTest with fake HTTP/temp stores or a read-only historical replay; Dashboard tests use AppTest with the full 83-destination catalog, fake HTTP, temporary stores and a read-only genuine replay; P4.3 integration tests run complete journeys through app.py, and P5.1 acceptance tests check model/storage behavior on the genuine data read-only. Synthetic tests do not write to the genuine weather dataset. Run tests while no app process is writing to that clone's weather CSV, or use a separate frozen copy: integrity tests intentionally detect changes to genuine data during a test. The two POSIX permission checks skip on Windows; see the [remaining acceptance checks](PHASE5_QUALITY_REVIEW.md#remaining-cross-platform-and-visual-checks) for the Mac/Linux command. Run Flake8 before committing; a successful run prints no findings. Keep Python lines within 79 characters and wrap long expressions, comments and docstrings rather than suppressing the checks.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `uv` is not recognized | Install uv using the official instructions above, then reopen the terminal. |
| `missing ScriptRunContext` warnings appear after using VS Code's Run Python File button | Launch the app with `uv run --locked streamlit run app.py` in the terminal. Streamlit needs its own runner. |
| `OPENWEATHER_API_KEY is not set` appears when requesting API access | Fill the key in your local `variables.env` or supply it through the environment. If replacing a previously loaded/rejected key, stop Streamlit with Ctrl+C and restart it; a browser refresh does not clear the process environment or session client. |
| `variables.env is not UTF-8 text` appears | The file was saved as UTF-16 (for example by Windows PowerShell 5 `echo ... > variables.env` or Notepad's "Unicode" option). Save it again as UTF-8, or create it with the `Copy-Item` command above and edit it. |
| A load crossed a daytime forecast-slot boundary | Run Search again or Refresh overview to start a new window. The app keeps strict coverage rules; it never invents missing periods or quietly shortens the window. Suitable saved forecasts are reused. |
| Weather loading stops with a storage error | Read the storage guidance above the results. Close Excel or another program holding the CSV, check folder permissions or free disk space as indicated, then use Search destinations or Refresh weather overview in the same session. Collected records waiting to save are shown explicitly; keep the tab/app running until saved. Windows access/lock failures get at most three file-operation attempts with 0.1/0.2-second waits. Other failures are not retried automatically. Never delete the genuine data to hide an error. |
| Map country outlines are missing | Plotly loads its geographical base map from its CDN. Check browser connectivity; the map is not guaranteed to render fully offline. |
| `Cannot read variables.env` appears | Check access to your credential file. A supplied nonblank process environment key takes precedence and does not require reading the file. |
| Port 8501 is already in use | Stop your other server or run `uv run --locked streamlit run app.py --server.port 8502`. Follow the Local URL printed by that process. |
| `uv sync --locked` reports that the lockfile is outdated | Check that `pyproject.toml` and `uv.lock` came from the same reviewed change. Coordinate dependency updates with the team and include both files in that change. |


## Project structure

| Location | Purpose |
| --- | --- |
| app.py | Navigation between the Searcher and Dashboard views, with shared source attribution |
| assets/openweather-logo.jpg | Unmodified official provider logo; attribution source below |
| src/weather_app/ | Installable package: configuration (`config.py`), domain models (`models.py`), catalog/weather storage (`storage.py`), OpenWeather client (`client.py`), request/save service (`service.py`) analytics/ranking engine (`analytics.py`), Searcher controls/presentation (`searcher.py`) and Dashboard views/charts (`dashboard.py`) |
| tests/ | Offline diagnostic, configuration, model, storage, analytics, client, service, Searcher and Dashboard tests (fake HTTP and temporary files only); acceptance tests include storage cache invalidation, strict slot boundaries and complete app journeys |
| scripts/verify_weather_access.py | Optional bounded live diagnostic, not the production service |
| data/reference/ | Nine-column catalog, product defaults, provider overrides and source notes |
| data/weather/ | Genuine timestamped responses and run summaries; normalized application CSV accumulates through normal use; see its dated snapshot notes for coverage |
| PHASE1_SETUP.md through PHASE6_DELIVERY.md | Owned tasks, dependencies and actual progress |
| PROJECT_PHASES.md / TEAMROLES.MD | Navigation and whole-component ownership |
| WEATHER_API_CONTRACT.md | Provider fields, requests and safe save/error rules |
| PROMPTS.md | Actual AI collaboration record |
| pyproject.toml / uv.lock / .python-version | Package/dependencies and shared Python selection |

## Analytics and course evidence

The app uses logged OpenWeather forecasts for three distinct analyses across **cross-location comparison** and **derived metrics**. An observed historical trend is not claimed.

| Analysis | What it means | Where to see it |
| --- | --- | --- |
| Weather/trip ranking | Percentage of temperature, precipitation and wind checks passed across daytime forecast slots; Searcher subtracts a capped driving-time penalty, Dashboard uses weather only | Searcher recommendations and Dashboard Weather ranking |
| Cross-location weather comparison | Mean daytime temperature (C), highest single-slot rain probability (%) and maximum wind (km/h), over the same window | Dashboard Weather comparison |
| Simultaneous suitability | Percentage of slots meeting all three weather preferences at once; this differs from the average of separate checks | Dashboard All three criteria |

The rolling window starts at the time of the load. Daytime is 09:00 inclusive to 18:00 exclusive in Europe/Madrid, sampled at the provider's three-hour slots. A forecast timestamp describes a prediction, not an observation collected in the future. Retrieval timestamps record when the app actually fetched the data. Missing/stale coverage produces an unavailable result, never fabricated values.

The [Phase 5 rubric walkthrough](PHASE5_QUALITY_REVIEW.md#p55-integrated-acceptance---12-november-2026) maps all six grading criteria to code and tests: reusable client inheritance, deliberate encapsulation, model special methods/properties, safe API handling, timestamped persistence, charts and team/AI evidence. The [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification) owns exact formulas and schema.

## Sources and delivery

Weather data provided by [OpenWeather](https://openweathermap.org/). The application displays its official logo and link in the sidebar; the unmodified logo comes from the [official logo archive](https://openweathermap.org/payload/api/files/file/logo_files.zip), linked by the [attribution FAQ](https://openweathermap.org/faq#license). The asset is provider branding, not a project-owned logo.

Destination references use [GeoNames](https://www.geonames.org/export/) and tourism sources; route estimates use OSRM with **[OpenStreetMap contributors](https://www.openstreetmap.org/copyright)** data. See [catalog credits and limitations](data/reference/README.md#sources-and-limits) and [weather provenance](data/weather/README.md) for details. Provider/source terms remain applicable; this project does not grant a new license over third-party data or branding.

The submission is the **GitHub repository URL**, with the reviewed final version on `main`. Use the [Phase 6 delivery checklist](PHASE6_DELIVERY.md#delivery-contents-and-final-checklist) to retain the code, locked setup, reference inputs, genuine accumulated data and AI records. An isolated wheel or a copied virtual environment is not the deliverable. Clean-clone acceptance, instructor submission channel/access and final review remain pending; public hosting is optional.

## Team workflow

Use personal branch -> reviewed dev -> reviewed main. Existing personal branches are `asier/feature`, `Alejandra/feature`, `christian/feature`, `gabrielstec/feature` and `selin/feature`; preserve their exact capitalization. Start from current dev, push the personal branch and request a teammate's review before merging. The selected main/dev protections require one approval, renewed approval after changes and resolved conversations, including for the owner. Check live enforcement when publishing; this cleanup did not change GitHub settings.

Each member owns a complete implementation with tests/docs/fixes and makes genuine contributions. [TEAMROLES.MD](TEAMROLES.MD) records assignments, not proof of authorship. Follow the actual-tool logging and co-author convention in [PROMPTS.md](PROMPTS.md). Codex-authored work uses `Co-Authored-By: Codex <noreply@openai.com>`; credit other tools only when actually used.

## Data and development

Read the [catalog sources](data/reference/README.md), [saved-data record](data/weather/README.md), [API contract](WEATHER_API_CONTRACT.md) and [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). The CSV remains 83 destinations and nine fields; weather records are separate. Christian approved the catalog foundation in PR #3; retain the source/access limitations described in its notes. Genuine development weather must be retained and submitted; no scheduler or historical-trend chart is required.

The optional live diagnostic commands are documented in the API contract. They make real requests and append data; ordinary tests are offline. Do not run repeated full-catalog checks merely to reproduce old reports.

Start at [PROJECT_PHASES.md](PROJECT_PHASES.md). Next: Gabriel reviews the prepared P6.1 documentation and confirms the remaining Mac tests and desktop/mobile map check on the merged version. Latest local automated acceptance (13 November): 438 tests passed and 2 Windows-inapplicable permission tests skipped; Flake8 clean. The store reuses validated records only when freshly read file bytes match, reducing repeated CSV parsing while detecting edits and read errors. The supported deployment is an editable installation from the repository; the built wheel alone does not include app.py or the external data files. Phase 6 still requires approval of the prepared delivery documentation, a clean-clone run, the reviewed main branch and actual submission. Git history contains contributions from all five members; each person must still be able to explain the application.
