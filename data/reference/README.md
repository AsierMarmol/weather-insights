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

Prepared 11 November 2026 using [INE hotel-tourism table 2078](https://www.ine.es/jaxiT3/Tabla.htm?t=2078), [GeoNames](https://www.geonames.org/about.html) reference populations/coordinates, [Spain.info](https://www.spain.info/en/destinations/) visitor information and [OSRM/OpenStreetMap](https://project-osrm.org/docs/v5.24.0/api/) route estimates. Retain source attribution. Selection used populated places of at least 20,000, excluding Madrid and islands; it is a curated list, not every tourist destination.

All routes use origin 40.4168,-3.7038 (approximate Madrid Km0), snapped by OSRM about 90 metres to a road. Estimates exclude live traffic, parking, stops and access guarantees. Kilometres are informational; driving minutes supply the capped penalty in [Phase 2](../../PHASE2_SCOPE.md).

Names follow the forecast provider. Current-product Vitoria-Gasteiz and Lleida are accepted variants of Gasteiz / Vitoria and Lérida. [weather_location_overrides.json](weather_location_overrides.json) contains these aliases and the necessary Lugo city-ID request: 3117814. Lugo's CSV values are 43,-7.5667, 498 km and 329 minutes. Updating coordinates alone does not replace this provider request override.

[product_defaults.json](product_defaults.json) holds shared seasonal/search defaults. Weather fetches belong in the separate weather dataset, not this catalog. The whole file has passed structure checks, and Christian approved the catalog foundation in PR #3. The estimates and activity tags retain the source/access limitations above; approval does not make them live traffic data or an exhaustive tourism/access audit. Earlier API checks do not prove tourism or road-access claims.


## Source credit and reuse review - 12 November 2026

Reference coordinates/population estimates use GeoNames; its [data terms](https://www.geonames.org/export/) specify CC BY attribution and provide data without an accuracy/completeness warranty. Project selection, rounded routes, activity tags and size categories are adaptations described above.

Route estimates were obtained using OSRM and OpenStreetMap data. Credit **OpenStreetMap contributors**, with the [copyright notice](https://www.openstreetmap.org/copyright) and [Open Database License](https://opendatacommons.org/licenses/odbl/). These are modeled driving estimates, not a live routing service or a claim of road access. Source license obligations continue to apply to derived data; attribution alone is not a blanket redistribution clearance.

INE table 2078 and Spain.info are selection/content references. The [INE legal notice](https://www.ine.es/aviso_legal/) was not readable through the review tool, so its conditions are not asserted verified. Confirm applicable INE/Spain.info reuse conditions before final delivery; no tourism prose or imagery is newly copied by this documentation update. OpenWeather canonical names/overrides and weather-data terms are described in the [weather provenance record](../weather/README.md).
