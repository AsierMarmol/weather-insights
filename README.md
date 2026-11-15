# Weather Insights

## Project overview and features

Weather Insights is a five-person Python/Streamlit project that recommends
mainland-Spain car trips from Madrid using weather preferences and driving time.
It combines live OpenWeather forecasts with a curated catalogue of 83 destinations.

- **Landing:** project introduction and seasonal temperature suggestions.
- **Trip Searcher:** personal recommendations for the next 1–5 days, with
  weather preferences, activity/size filters, five recommendations and a full ranking.
- **Dashboard:** an independent overview of all 83 destinations, with a map,
  summary cards, rankings, a driving-time scatter plot, driving bands and a daily heatmap.
- **Reproducible data and analytics:** timestamped weather history, shared scoring
  functions and an installable object-oriented Python package with automated tests.

See [project phases](PROJECT_PHASES.md) for progress and
[Phase 6](PHASE6_DELIVERY.md) for acceptance and publication status.

## Requirements and complete setup

These instructions apply to teammates, the instructor and other readers.
Use **Windows PowerShell** or **macOS Terminal** as labelled below.

- [Git](https://git-scm.com/downloads).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python and
  dependency management; setup was verified with uv 0.12.23.
- Python **3.14**, selected by `.python-version`; uv can download it if needed.
  Setup was verified with Python 3.14.7.
- Internet access and a personal [OpenWeather API key](https://openweathermap.org/appid)
  with access to the 5-day/3-hour forecast for fresh weather.
- VS Code with the Python extension is optional.

If uv is missing, follow its linked installation instructions. On Windows with WinGet:

```powershell
winget install --id astral-sh.uv --exact
```

Open a new terminal after installation so `uv` is available.

### Clone and install

Windows, from a folder where you want to keep the project:

```powershell
git clone --branch main https://github.com/AsierMarmol/weather-insights.git
Set-Location -LiteralPath .\weather-insights
uv sync --locked
```

macOS:

```bash
git clone --branch dev https://github.com/AsierMarmol/weather-insights.git
cd weather-insights
uv sync --locked
```

During development, `dev` contains the reviewed team version. Final submission
will use reviewed `main`; see the publication checklist before switching branches.
For an existing clone, run `uv sync --locked` from the folder containing `pyproject.toml`.
This creates `.venv`, installs the local `weather-app` package and its dependencies,
and includes pytest, Flake8 and pinned Pyright. `--locked` checks that the committed
lockfile matches the project configuration. No manual environment activation is needed.

### Configure your local API key

Create the credential file without overwriting an existing one. Windows:

```powershell
if (-not (Test-Path -LiteralPath .\variables.env)) {
    Copy-Item -LiteralPath .\variables.env.example -Destination .\variables.env
}
```

macOS:

```bash
if [ ! -e variables.env ]; then
    cp variables.env.example variables.env
fi
```

Open `variables.env` locally and enter your personal key after the equals sign:

```dotenv
OPENWEATHER_API_KEY=
```

Keep the published example blank. `variables.env` is ignored by Git; never put
real keys in commits, screenshots, chat or logs. The app loads this file from the
project root using `python-dotenv`; an existing `OPENWEATHER_API_KEY` environment
variable takes precedence. Landing and Searcher controls work without a key;
configure it before opening Dashboard, searching or running the live diagnostic.

### Optional VS Code setup

Open the repository folder. Use **Python: Select Interpreter** from the command
palette (Ctrl+Shift+P on Windows, Cmd+Shift+P on macOS) and select
`.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS.
It may appear as **weather-app (3.14.x)**; the import name is `weather_app`.
After changing environments, use **Python: Restart Language Server**.
The `uv run` commands use the project environment automatically.

## Running and using the application

From the project directory, on either operating system:

```powershell
uv run --locked streamlit run app.py
```

Open the terminal's Local URL, usually http://localhost:8501, in your browser or
VS Code's Simple Browser. Streamlit's welcome email is optional. Stop with Ctrl+C;
use one writing Streamlit process per clone.

In **Trip Searcher**, choose a rolling next 1–5 days (default 3), a temperature
band, preferred rain/wind categories, activities and destination size. Both filters
default to **All**. Rain/wind categories describe desired conditions, not maximum
tolerances. Click **Search destinations**; controls and reset alone do not fetch.
Selections survive navigation until reset. High-wind notices and red markers
identify affected top-five recommendations.

**Dashboard** loads automatically on first opening and when its independent
forecast window changes. It always represents all 83 destinations, without
Searcher filters. Expand the heatmap and sortable catalogue for daily scores,
weather metrics, driving times, timestamps and unavailable reasons.

## Data, scores and limitations

| Score | Meaning | Where it is used |
| --- | --- | --- |
| **Trip score /100** | Match to the traveller's preferences, including the driving-time penalty | Searcher cards and full ranking |
| **Destination score /100** | Standard seasonal weather criteria, including the driving-time penalty | Dashboard map, summary cards, top five, scatter, driving bands and catalogue |

Scores are indices, not probabilities. Each view uses one consistent whole-window
score; the views can differ because their criteria differ. The heatmap applies the
Dashboard formula per day and sorts by its labelled **Daily avg**. That daily mean
can differ from the nonlinear whole-window score. [SCORING.md](SCORING.md) defines
the formulas, aggregation and missing-data rules.

- Both views fetch/save the provider's full five-day forecast, then select the
  requested rolling window using native three-hour slots during Madrid daytime
  (09:00 inclusive, 18:00 excluded, Europe/Madrid).
- Suitable saved forecasts up to three hours old are reused when complete and
  matching the current provider city ID. Fresh data loads on search or Dashboard
  load/refresh, not on a background timer. A cold all-city load can take several
  minutes; ordinary navigation does not repeat it.
- Successful fresh fetches must save before ranking. The committed weather CSV
  preserves genuine accumulated history and retrieval timestamps. Forecast times
  describe predictions, not observations collected in the future. Changing
  preferences or scoring does not rewrite raw weather.
- Missing weather stays grey/blank with a reason; values are never invented.
  A failed refresh keeps the previous snapshot explicitly labelled. Dashboard
  rain/wind cards show equal-city daytime averages and N/83 contributors;
  catalogue rain/wind columns show maximum slot values.
- The 83 destinations are an AI-assisted curated selection, not an exhaustive
  tourism list. Activities and size are project classifications. One-way routes
  from approximate Madrid Km0 exclude live traffic, parking and stops. Driving
  displays use h:mm; source data and calculations retain minutes.
- Seasonal temperatures are comfort suggestions, not climate measurements.
  Map tiles and web fonts need internet; the catalogue remains usable if tiles fail.
  Map colours use a fixed red-to-green 0–100 scale, a numeric legend and grey for
  missing weather. Blue identifies Madrid as the origin.

The three analyses are **destination ranking**, **score versus journey effort**
and **destination-by-day comparison**, covering cross-location comparisons and
derived metrics. No observed historical weather trend is claimed. The
[course rubric walkthrough](PHASE5_QUALITY_REVIEW.md#checkpoint-6-validation--13-november-2026)
links requirements to implementation and evidence.

## Testing and troubleshooting

Stop app writes in this clone before testing, or test a separate frozen copy.
From the project directory:

```powershell
uv run --locked python --version
uv pip check
uv run --locked python -c "import weather_app; print('weather_app import OK')"
uv run --locked python -m pytest -q
uv run --locked flake8 src tests scripts app.py
uv run --locked pyright
```

Expect Python 3.14.x, compatible dependencies, a successful import and passing
offline tests. Tests cover models, API/service, storage, scoring, UI and integration;
synthetic requests/writes use fake HTTP and temporary files. Genuine-data checks
read saved records without modifying them. Two POSIX permission tests skip on
Windows. Flake8 reports no findings on success. Pyright's first run may download
Node.js; also inspect VS Code's Pylance diagnostics. Keep the 79-character Python
line limit and fix genuine diagnostics rather than disabling checks.

The full suite includes bounded stress/error simulations; to run those separately:

```powershell
uv run --locked python -m pytest -q -s tests/test_stress.py
```

These use synthetic data and do not stress the live API. Dated results, scope and
limitations are recorded in [Phase 5](PHASE5_QUALITY_REVIEW.md); independent
clean-clone and live-save evidence is in [Phase 6](PHASE6_DELIVERY.md).

| Symptom | Action |
| --- | --- |
| `uv` is not recognized | Install uv, then reopen the terminal. |
| `missing ScriptRunContext` | Use the Streamlit launch command above, not VS Code's Run Python File button. |
| API key missing or rejected | Check your local key and environment-variable override. Restart Streamlit after replacing a loaded key; refreshing the browser alone does not reload it. |
| Credential file cannot be read or is not UTF-8 | Check access and save `variables.env` as UTF-8. Create it with the guarded copy command above; Windows PowerShell redirection can produce UTF-16. |
| Load crosses a daytime forecast-slot boundary | Search or refresh again to start a new window. Coverage rules do not invent missing slots or silently shorten the window. |
| Weather cannot be saved | Close Excel or another program holding the CSV; check permissions/free disk space and follow the displayed recovery instructions. Keep the session open for pending saves and retry Search/Refresh. Never delete genuine history to hide the error. |
| Map background is missing | Check internet/tile access; use the catalogue while tiles are unavailable. |
| Port 8501 is in use | Stop the other server or add `--server.port 8502` to the launch command. |
| Lockfile is outdated | Ensure `pyproject.toml` and `uv.lock` came from the same reviewed change; coordinate dependency updates and commit both together. |

## Compact project structure

| Location | Purpose |
| --- | --- |
| `app.py` | Page navigation and application entry point |
| `src/weather_app/` | Installable package: models, API/configuration, storage/service, analytics/scoring and UI |
| `tests/` | Unit, integration, acceptance and bounded stress tests |
| `scripts/verify_weather_access.py` | Optional live diagnostic; requests and saves real data |
| `data/reference/` | Destination catalogue, defaults, provider mappings and source notes |
| `data/weather/` | Genuine timestamped weather history and provenance |
| `assets/`, `.streamlit/config.toml` | Local visual assets, credits and theme |
| `pyproject.toml`, `uv.lock`, `.python-version` | Package, locked dependencies and Python selection |
| `variables.env.example` | Blank credential template; each user creates their own ignored `variables.env` |
| Phase documents, `TEAMROLES.MD`, `PROMPTS.md` | Plans/progress, ownership and actual AI collaboration records |

`src/weather_app/__init__.py` marks the Python package without performing setup,
API calls or file writes. `.venv/`, `*.egg-info/`, caches, `build/` and `dist/` are
generated locally and ignored by Git; do not copy or commit them. Source, tests,
locked setup, reference inputs, genuine weather history and assets belong in Git.

## Team and workflow

**Team:** Asier, Alejandra, Gabriel, Christian and Selin.
[TEAMROLES.MD](TEAMROLES.MD) records component ownership, reviewers and actual
attribution, including later cross-component changes.

Work follows **personal feature branch → reviewed `dev` → reviewed `main`**.
Start from current `dev`, implement and test the change, then open a pull request
for teammate review. Personal branches are `asier/feature`, `Alejandra/feature`,
`christian/feature`, `gabrielstec/feature` and `selin/feature`; capitalization matters.
Resolve review conversations and follow branch protections before merging.

Each member must make genuine contributions and understand the application.
Record actual AI assistance in [PROMPTS.md](PROMPTS.md) and credit the tools used;
Codex-authored work uses `Co-Authored-By: Codex <noreply@openai.com>`.
Assignments alone are not evidence of authorship. Keep credentials local and
update affected phase steps when project decisions change.

## Sources and links to detailed documentation

Weather data is provided by [OpenWeather](https://openweathermap.org/); its official
logo and link are displayed in the app. Reference coordinates/population estimates
use [GeoNames](https://www.geonames.org/export/); route estimates use OSRM with
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright) data.
Canva supplied visual direction only, not weather or scoring. Source terms continue
to apply; the project does not grant a new licence over third-party data or branding.

- [Catalogue sources and limitations](data/reference/README.md#sources-and-limits),
  [weather provenance](data/weather/README.md) and [asset credits](assets/README.md).
- [Scoring definitions](SCORING.md), [API contract and live diagnostic](WEATHER_API_CONTRACT.md)
  and [shared data specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification).
- [Project phases](PROJECT_PHASES.md), [validation evidence](PHASE5_QUALITY_REVIEW.md)
  and [delivery checklist](PHASE6_DELIVERY.md#delivery-contents-and-final-checklist).

Submission is the **GitHub repository URL**, with the reviewed final version on
`main`, accessible to the instructor. Retain the genuine accumulated dataset and
AI records; exclude real API keys. The instructor should be able to clone, install
and run using this README and their own key. Final review/submission status belongs
in Phase 6; public app hosting is optional.
