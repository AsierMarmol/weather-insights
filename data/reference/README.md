# Destination catalog

`destinations.csv` is the single editable catalog: 83 mainland-Spain destinations, car travel from a fixed approximate Madrid Km0 reference. Asier owns its content; Christian reviews it. Alejandra implements its loader.

| Field | Meaning |
| --- | --- |
| city_id | Stable ES- plus five-digit INE municipality code |
| city | Canonical OpenWeather forecast display name, lang=en |
| region | Autonomous community |
| car_distance_km | Rounded one-way road distance in km |
| car_duration_min | Rounded one-way modeled driving duration in minutes |
| latitude, longitude | Destination reference coordinates |
| activities | Semicolon-separated visitor experiences |
| destination_size | Population-based project size category |

## Categories

Activities: **Coast**, **Nature**, **History and heritage**, **Food and gastronomy**, **Urban experiences**. Multiple tags are allowed. Nature requires an identifiable outdoor attraction nearby; heritage refers to distinctive local heritage; urban experiences is not inferred solely from city size. Tags remain subject to content review.

| Size | Reference population | Catalog rows |
| --- | --- | --- |
| Large city | 250,000 or more | 14 |
| Medium city | 100,000-249,999 | 26 |
| Small city or town | 10,000-99,999 | 43 |

These are project conventions based on GeoNames populated-place estimates, not official municipal classifications or a current census. Populate UI options from actual catalog values and default visibly to All. Activities and size filter eligibility; neither adds score points.

## Sources and limits

Prepared 11 November 2026. On 14 November the requester clarified that the destinations were selected with AI assistance using the agreed project criteria: mainland-Spain car trips from Madrid and the activity categories above. This is a curated project selection, not an official tourism ranking or an exhaustive destination list. Activity tags are project classifications, not weather API fields or verified official labels. Earlier references to INE/Spain.info do not establish that an INE tourism dataset was imported to generate the list.

Selection is separate from field provenance: retain the documented [GeoNames](https://www.geonames.org/about.html) coordinate/population references, [OSRM/OpenStreetMap](https://project-osrm.org/docs/v5.24.0/api/) route estimates and OpenWeather identity checks below. This clarification does not change or independently revalidate those numeric fields.

All routes use origin 40.4168,-3.7038 (approximate Madrid Km0), snapped by OSRM about 90 metres to a road. Estimates exclude live traffic, parking, stops and access guarantees. Kilometres are informational; driving minutes supply the capped penalty in [Phase 2](../../PHASE2_SCOPE.md).

Names follow the forecast provider. Current-product Vitoria-Gasteiz and Lleida are accepted variants of Gasteiz / Vitoria and Lérida. [weather_location_overrides.json](weather_location_overrides.json) contains these aliases and the necessary Lugo city-ID request: 3117814. Lugo's CSV values are 43,-7.5667, 498 km and 329 minutes. Updating coordinates alone does not replace this provider request override.

[product_defaults.json](product_defaults.json) holds shared seasonal/search defaults. Weather fetches belong in the separate weather dataset, not this catalog. The whole file has passed structure checks, and Christian approved the catalog foundation in PR #3. The estimates and activity tags retain the source/access limitations above; approval does not make them live traffic data or an exhaustive tourism/access audit. Earlier API checks do not prove tourism or road-access claims.


## Source credit and reuse review - 12 November 2026

Reference coordinates/population estimates use GeoNames; its [data terms](https://www.geonames.org/export/) specify CC BY attribution and provide data without an accuracy/completeness warranty. Project selection, rounded routes, activity tags and size categories are adaptations described above.

Route estimates were obtained using OSRM and OpenStreetMap data. Credit **OpenStreetMap contributors**, with the [copyright notice](https://www.openstreetmap.org/copyright) and [Open Database License](https://opendatacommons.org/licenses/odbl/). These are modeled driving estimates, not a live routing service or a claim of road access. Source license obligations continue to apply to derived data; attribution alone is not a blanket redistribution clearance.

Clarified 14 November: the earlier INE/Spain.info selection attribution was not established by the requester's AI-assisted selection process. The unreadable INE notice is therefore not a project acceptance gate. Do not describe the catalogue as an INE-derived tourism ranking. The INE-style municipality identifiers are separate from the destination-selection method. OpenWeather canonical names/overrides and weather-data terms remain described in the [weather provenance record](../weather/README.md).

## Barcelona identity follow-up — 13 November 2026

During the dashboard experiment, a live coordinate forecast request returned
Eixample and was correctly rejected by the existing city-name check. The
historical Barcelona records identify provider city **3128760**. A live explicit
ID request verified Barcelona, Spain, at 41.3888, 2.159 and successfully saved
40 forecast periods. The existing override file now requests that ID and checks
both the ID and Barcelona name. Eixample is not accepted as an alias. Catalog
coordinates, driving estimates, IDs and names are unchanged. This dated correction was incorporated in the reviewed P4.5 integration; see
[Phase 4](../../PHASE4_ANALYTICS_UI.md#p45-canva-inspired-executive-redesign).

Scoring is defined in [SCORING.md](../../SCORING.md); source data is kept
separate from computed scores and synthetic test fixtures.


## Valladolid identity follow-up — 13 November 2026

A live coordinate request for catalog Valladolid (41.65541, -4.72353)
returned Delicias, provider ID 6691623. The client correctly rejected it.
An explicit request using previously recorded Valladolid provider ID 3106672
returned Valladolid, ES, at 41.6552, -4.7237. All 40 forecast records validated
and were saved through WeatherStore. The reference override now requests and
checks that ID; the name, country and proximity safeguards remain in place.
No catalog coordinates, route estimates or accepted district aliases changed.
Restart the local app after changing overrides: a running session's client
retains the configuration with which it was created.


## Complete provider city-ID mapping — 13 November 2026

All **83 destinations** now request a unique verified OpenWeather city ID using
the existing `weather_location_overrides.json`. The nine-column destination CSV
is unchanged. Catalog IDs, names, coordinates and routes remain separate from
provider identifiers. Existing accepted bilingual/translated labels remain;
unreviewed districts are not added as aliases.

Candidates came from genuine saved responses, using the latest provider ID
per destination. Nine destinations had multiple historical municipality/city
IDs; historical observations were preserved, not rewritten. Every selected
ID passed a live explicit-ID request to both current weather and forecast:
**166/166 successful responses**, with name/approved alias, country ES and
distance within 10 km checked. The existing paced service saved all **3,403
genuine records** (83 current + 83 × 40 forecast) with real timestamps.

Requests no longer silently fall back to coordinates when a mapping is absent.
Configuration rejects duplicate IDs and disagreement between requested and
expected IDs. Tests require complete catalog coverage and verify outgoing
parameters, response identity rejection, safe failure and historical replay.
Historical coordinate responses are replayed under their original name/country/
proximity checks; current ID enforcement is tested separately for all 83 cities.

**Maintenance:** when adding or replacing a destination, derive a candidate ID
from trustworthy provider evidence, verify both endpoints and the real location,
save successful observations, then update this mapping and run the suite.
Do not accept a new provider name automatically. Restart Streamlit after mapping
changes so its session client reloads the configuration. This prevents the
observed coordinate-to-district ambiguity; API outages and provider changes can
still produce explicit errors.

Validation: **494 passed, 2 POSIX-only skips on Windows**; Flake8 passed. Automated tests used the isolated
copy; live verification used the actual service/store with app refreshes paused.
Testing worktree only. No staging, commit, push, PR or merge.


## Checkpoint 6 reference audit — 13 November 2026

The 83-row catalogue, product defaults and provider mapping are unchanged by
this validation. All 83 destinations have unique expected provider IDs.
The audit reused the existing live verification evidence; offline stress tests
did not issue provider requests or rewrite catalogue coordinates.
See [validation for this checkpoint](../../PHASE5_QUALITY_REVIEW.md#checkpoint-6-validation--13-november-2026).
