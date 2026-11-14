# Weather Insights

> **Current delivery candidate:** P4.5 is prepared on `asier/feature` for
> review into `dev`. Gabriel's approval and the reviewed-commit clean-clone check remain pending. [SCORING.md](SCORING.md) is the current formula;
> [Latest quality review](PHASE5_QUALITY_REVIEW.md#feature-integration-validation--14-november-2026)
> records current verification. Dated baseline records below are historical,
> not acceptance of this redesign. No publication or peer approval is implied.

A five-person Python/Streamlit project recommending mainland-Spain car trips from Madrid using weather preferences and driving time.

## Current status

The local preview includes Landing, Trip Searcher and the independent all-83
Dashboard. It retains the original OOP/API/store architecture and genuine data.
The Canva template supplies visual direction only; its example weather and
scoring are not used. P4.1–P4.4 and P5.5 have historical review records; the
redesign has the requester's final preview review (14 November 2026),
while teammate review and the reviewed-commit clean-clone check remain pending. See
[project phases](PROJECT_PHASES.md) for the remaining work and owners.

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

The key can remain blank while you explore Landing and Searcher controls.
Configure it before opening Dashboard (which loads automatically), clicking
Search destinations or deliberately running the live API diagnostic.

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

Leave Streamlit's optional welcome email blank if desired. Open the Local URL
printed by the terminal, usually http://localhost:8501, or use VS Code's Simple
Browser. Stop the server with Ctrl+C. Use one writing Streamlit process per clone.

- **Landing:** explains the product and shows the current Madrid season using
  `product_defaults.json`. The ranges are comfort suggestions, not climate data.
- **Trip Searcher:** choose a rolling next 1–5 days (default 3), temperature
  band, preferred rain/wind categories, activities and size. Both filters visibly
  default to All. Low/Medium/High rain expresses desired conditions, not a
  maximum tolerance. Click Search destinations to calculate results. Controls
  and reset alone do not fetch. Five cards and the full eligible ranking show
  the identical **Trip score /100**, including driving. Missing scores stay
  blank with reasons. A high-wind notice appears only for affected top-five
  recommendations. Manual choices survive navigation until explicitly reset.
- **Dashboard:** loads automatically on first opening and when its independent
  1–5-day window changes. No city/activity/size filters apply. Map, KPI, leader,
  top five, scatter, driving bands and catalogue use the same whole-window
  **Destination score /100**, including driving. All 83 destinations remain
  represented, with grey/blank values for unavailable weather. The daily heatmap
  evaluates the same formula per day and sorts by its labelled Daily avg;
  this is distinct from nonlinear whole-window aggregation. Expand the sortable
  catalogue for source metrics, driving, timestamps and unavailable reasons.

Scores are indices, not probabilities. [SCORING.md](SCORING.md) owns their
definitions. Searcher and Dashboard can differ because their criteria differ;
within each view all whole-window score displays must agree.

Both views request/save the provider's full five-day forecast. Shared analytics
selects the requested rolling window from native three-hour Madrid daytime
slots (09:00 inclusive, 18:00 excluded). Forecasts up to three hours old are
reused when complete and matching the current provider city ID.
The app fetches missing/stale data on an explicit search
or Dashboard load/refresh, not on a background timer. A cold all-city load can
take several minutes. Ordinary reruns and navigation do not repeat the load.
Failed changes keep the old snapshot explicitly labelled. Every successful
fresh fetch must save before it can be ranked; raw weather is not rewritten
when preferences or scoring change.

Dashboard rain/wind KPI cards are equal-city averages of daytime forecasts;
they show N/83 contributors and never fill missing values with zero. Catalogue
rain/wind columns explicitly show maximum slot values. Travel is a reference
one-way estimate from Madrid Km0, without traffic. Durations display h:mm;
calculations and source data keep their original minute values.

The map uses OSM tiles, a fixed red-to-green 0–100 score scale and a separate
blue Madrid origin. The numeric legend supplements colour. Tiles/web fonts
need internet; local assets and the catalogue provide fallbacks. See
[asset credits](assets/README.md).

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
| Map background is missing | The browser loads OpenStreetMap raster tiles over the internet. Check browser connectivity and tile access. The catalogue remains available if tiles cannot load. |
| `Cannot read variables.env` appears | Check access to your credential file. A supplied nonblank process environment key takes precedence and does not require reading the file. |
| Port 8501 is already in use | Stop your other server or run `uv run --locked streamlit run app.py --server.port 8502`. Follow the Local URL printed by that process. |
| `uv sync --locked` reports that the lockfile is outdated | Check that `pyproject.toml` and `uv.lock` came from the same reviewed change. Coordinate dependency updates with the team and include both files in that change. |


## Project structure

| Location | Purpose |
| --- | --- |
| app.py | Landing, Trip Searcher and Dashboard navigation; shared attribution |
| assets/openweather-logo.jpg | Unmodified official provider logo; attribution source below |
| src/weather_app/ | Installable package: configuration (`config.py`), domain models (`models.py`), catalog/weather storage (`storage.py`), OpenWeather client (`client.py`), request/save service (`service.py`) analytics/ranking engine (`analytics.py`), pure scoring (`scoring.py`) and executive summaries (`executive.py`), shared presentation (`presentation.py`/`executive_view.py`), Searcher controls/presentation (`searcher.py`) and Dashboard views/charts (`dashboard.py`) |
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
| Weather/trip ranking | Separate seasonal comfort and personal preference modes; Searcher subtracts the capped driving penalty, Dashboard uses seasonal comfort and the same driving penalty | Searcher cards/full ranking; Dashboard map, top five and catalogue |
| Weather versus journey effort | Compare Destination score with driving hours; identify strong options within driving-time bands | Dashboard scatter and driving bands |
| Destination-by-day comparison | Compare daily forecast suitability across destinations and future windows; equal-weight mean of available daily scores orders rows | Dashboard heatmap, average column and missing-data explanations |

The map and scatter remain two labeled real-data charts. Simultaneous
suitability remains calculated internally but is not displayed; its
separate Dashboard chart was removed. Daily averages exclude unavailable days,
show partial coverage, and put entirely unavailable destinations last. Ties use
city ID and sorting uses unrounded values. This average can differ from the
whole-window score because worst-quarter aggregation is nonlinear.

The rolling window starts at the time of the load. Daytime is 09:00 inclusive to 18:00 exclusive in Europe/Madrid, sampled at the provider's three-hour slots. A forecast timestamp describes a prediction, not an observation collected in the future. Retrieval timestamps record when the app actually fetched the data. Missing/stale coverage produces an unavailable result, never fabricated values.

The [Phase 5 rubric walkthrough](PHASE5_QUALITY_REVIEW.md#checkpoint-6-validation--13-november-2026) maps all six grading criteria to code and tests: reusable client inheritance, deliberate encapsulation, model special methods/properties, safe API handling, timestamped persistence, charts and team/AI evidence. The [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification) owns schema; [SCORING.md](SCORING.md) owns current formulas.

## Sources and delivery

Weather data provided by [OpenWeather](https://openweathermap.org/). The application displays its official logo and link in the sidebar; the unmodified logo comes from the [official logo archive](https://openweathermap.org/payload/api/files/file/logo_files.zip), linked by the [attribution FAQ](https://openweathermap.org/faq#license). The asset is provider branding, not a project-owned logo.

Destination references use [GeoNames](https://www.geonames.org/export/) and tourism sources; route estimates use OSRM with **[OpenStreetMap contributors](https://www.openstreetmap.org/copyright)** data. See [catalog credits and limitations](data/reference/README.md#sources-and-limits) and [weather provenance](data/weather/README.md) for details. Provider/source terms remain applicable; this project does not grant a new license over third-party data or branding.

The submission is the **GitHub repository URL**, with the reviewed final version on `main`. Use the [Phase 6 delivery checklist](PHASE6_DELIVERY.md#delivery-contents-and-final-checklist) to retain the code, locked setup, reference inputs, genuine accumulated data and AI records. An isolated wheel or a copied virtual environment is not the deliverable. Clean-clone acceptance, instructor submission channel/access and final review remain pending; public hosting is optional.

## Team workflow

Use personal branch -> reviewed dev -> reviewed main. Existing personal branches are `asier/feature`, `Alejandra/feature`, `christian/feature`, `gabrielstec/feature` and `selin/feature`; preserve their exact capitalization. Start from current dev, push the personal branch and request a teammate's review before merging. The selected main/dev protections require one approval, renewed approval after changes and resolved conversations, including for the owner. Check live enforcement when publishing; this cleanup did not change GitHub settings.

Each member owns a complete implementation with tests/docs/fixes and makes genuine contributions. [TEAMROLES.MD](TEAMROLES.MD) records assignments, not proof of authorship. Follow the actual-tool logging and co-author convention in [PROMPTS.md](PROMPTS.md). Codex-authored work uses `Co-Authored-By: Codex <noreply@openai.com>`; credit other tools only when actually used.

## Bounded stress simulations

```powershell
uv run --locked python -m pytest -q -s tests/test_stress.py
```

These repeat all-83 window changes, exercise eight same-process writers and
load a 33,200-row synthetic history, using fake HTTP and temporary files only.
The full suite also injects quota, timeout, invalid-response and storage errors.
Never stress the live provider or deliberately damage the real CSV. Stop the
app before testing its clone, or use a frozen isolated copy. These bounded
checks are not a multi-server concurrency guarantee.

## Data and development

Read the [catalog sources](data/reference/README.md), [saved-data record](data/weather/README.md), [API contract](WEATHER_API_CONTRACT.md) and [shared specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification). The CSV remains 83 destinations and nine fields; weather records are separate. Christian approved the catalog foundation in PR #3; retain the source/access limitations described in its notes. Genuine development weather must be retained and submitted; no scheduler or historical-trend chart is required.

The optional live diagnostic commands are documented in the API contract. They make real requests and append data; ordinary tests are offline. Do not run repeated full-catalog checks merely to reproduce old reports.

Start at [PROJECT_PHASES.md](PROJECT_PHASES.md). Current local Windows
validation: **505 passed, 2 POSIX-only skips**, lint clean, including bounded
stress checks. VS Code preview evidence is dated 13 November; the requester
confirmed final preview review on 14 November. Phone/Mac checks are outside
this local audit. P6.1 documentation is prepared for Gabriel's review; catalogue
selection provenance is clarified in the reference notes. After authorized reviewed publication, perform P6.2
on the adopted reviewed commit and P6.3 delivery. A tested local snapshot is
not a reviewed GitHub version or an instructor grade. Every member must still
be able to explain the application.

## Latest audit

The [14 November semantic audit](PHASE5_QUALITY_REVIEW.md#semantic-and-test-quality-audit--14-november-2026) checked active wording, reference
defaults, batch-stop handling, obsolete Dashboard filters and test validity.
That audit passed **506 tests**, with two POSIX-only skips. The subsequent
[cleanup review](PHASE5_QUALITY_REVIEW.md#feature-integration-validation--14-november-2026)
passed **505 tests**, with the same two skips, after removing one duplicate test.
Lint, locked installation and package builds passed. The earlier installed-wheel
check remains dated evidence.
Tests rejected three deliberately wrong calculation variants in disposable
copies. No synthetic weather or credentials were added to the dataset.
These are local checks, not peer approval or a fresh live-provider guarantee.

## Reproducing the project on another computer

The setup instructions apply equally to teammates, the instructor and other
readers. Install Git and uv, clone the reviewed repository, run `uv sync --locked`,
create your own `variables.env` from the blank example, and launch
`uv run --locked streamlit run app.py`. Internet access and an active personal
OpenWeather key are needed for fresh weather; the key is never supplied in Git.
The locked Python/dependencies, reference catalogue/mappings/defaults, local
assets, theme and genuine accumulated dataset travel with the repository.
Nothing in the runtime source requires Asier's Windows path or copied settings.

For grading, use the final reviewed `main` commit after publication. Until then,
`dev` is the reviewed team baseline and these uncommitted feature changes cannot
be obtained by cloning GitHub. Record the tested commit with `git rev-parse HEAD`
and follow the verification commands above. P6.2 is the independent test of that
exact published commit; a local test-copy run does not replace it.

### Source files versus generated files

- `src/weather_app/__init__.py` is a regular-package marker. It deliberately
  performs no setup, API calls or file writes; a package marker may validly be
  empty. Its module description now documents this intent.
- `src/weather_app.egg-info/` (including `SOURCES.txt` and `top_level.txt`) is
  installation metadata generated by setuptools. Do not hand-edit or commit it.
- `.venv/`, `__pycache__/`, `.pytest_cache/`, `build/` and `dist/` are local
  generated artifacts, ignored by Git and recreated when needed.
- Keep `pyproject.toml`, `uv.lock`, `.python-version`, `.streamlit/config.toml`,
  `variables.env.example`, source/tests, assets, data and documentation in Git.
  The optional `scripts/verify_weather_access.py` diagnostic remains available.
- `tests/`, `scripts/`, `data/` and `assets/` do not need empty `__init__.py` files
  merely because they are directories. Exception classes with only a docstring
  and intentional callback parameters are not unfinished implementations.
