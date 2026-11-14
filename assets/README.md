# Presentation assets

- `openweather-logo.jpg`: existing unmodified official OpenWeather logo.
- `travel-globe.jpg`: Porapak Apichodilok, *Person Holding World Globe Facing
  Mountain*, Pexels photo 346885. Downloaded 13 November 2026 from the image
  URL in the supplied visual template, resized by Pexels to 1280 pixels.
  [Photo](https://www.pexels.com/photo/person-holding-world-globe-facing-mountain-346885/)
  · [Pexels license](https://www.pexels.com/license/).
  Used as decorative travel imagery, not a photograph of a catalog destination.
- `design.css`: project presentation styles. The supplied Canva design is a
  visual reference only; its data, JavaScript scoring and bootstrap are not used.

DM Sans and Fraunces are requested from Google Fonts through Streamlit's theme.
The app remains usable with fallback fonts if those requests are unavailable.
The hero and provider logo are local; loading them needs no external request.
Map geometry/tiles and web fonts can require internet access.

Responsive CSS includes version-sensitive Streamlit selectors. Recheck desktop
and mobile navigation after upgrading Streamlit. No credentials enter these
assets, HTML or CSS.

The P4.5 map background uses standard OpenStreetMap raster tiles rendered by
Plotly/MapLibre. The map style and caption credit
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
Browser tile requests use normal caching; no offline tile download is provided.
See the [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).
The blue origin and fixed red-to-green/grey destination circles are generated from project
coordinates and weather results, not from template example data.

Current P4.5 implementation: [comfort-v2 scoring](../SCORING.md) uses seasonal Dashboard comfort, preferred Searcher ranges and a driving penalty in both views. Raw sources/assets remain unchanged; no scores or synthetic weather are written to the genuine weather CSV.

KPI columns adapt to available container width; recheck them inside VS Code
as well as a standalone browser. Responsive styling does not change data.
