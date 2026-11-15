# Scoring specification — comfort-v2.2

Approved group product decisions, implemented in P4.5 and merged into dev
through PR #21 after Gabriel's review.
This supersedes the earlier equal-weight pass/fail scoring, weather-only
Dashboard ranking and maximum-only Searcher controls. These are tourism
preferences, not a validated physiological index, probability of good weather,
or safety assessment. Publication and remaining acceptance gates are recorded
in [project phases](PROJECT_PHASES.md).

## Data and calculation ownership

`scoring.py` owns pure slot functions and aggregation; `analytics.py` validates
saved forecast groups and applies them. Models validate mode/preferences.
Searcher and Dashboard share API/storage paths but have independent preferences
and calculation modes. UI code formats results; it does not duplicate scoring.
The version identifier invalidates old session results after a formula change,
while retaining the service and any unsaved records awaiting recovery.

Only real, saved forecasts enter production calculations. The service always
requests the full provider forecast; analytics slices it locally for each view. Each rolling next
1–5-day window starts at load time: start < valid_at <= start + 24*N hours.
Evaluate native three-hour UTC slots whose Europe/Madrid local hour is 09:00
inclusive to 18:00 exclusive. Daily heatmap columns are consecutive 24-hour
slices, not calendar-day forecasts. No interpolation of missing weather occurs.

## Dashboard: seasonal weather comfort

Season follows each forecast slot's Madrid date. Meteorological months:
December–February Winter 10–18°C; March–May Spring 18–26°C; June–August
Summer 22–30°C; September–November Autumn 16–24°C. The validated reference
`data/reference/product_defaults.json` provides these bands. No new seasonal
API or climate dataset is needed.

For temperature T and ideal band [L,U]:

`temperature = max(0, 100 - 5*max(L-T,0) - 7.5*max(T-U,0))`

Full points inside the band; gradual decline on both sides. A warm autumn day
above 24°C is still displayed and can score well. This seasonal-band rule
replaces the previously discussed fixed 18–26°C year-round curve.

`rain = 100 - precipitation_probability_pct`

Wind component anchors (km/h, points): (0,100), (10,100), (20,85), (30,60),
(40,30), (60,0). Interpolate linearly between anchors; 60+ scores zero.

`clear_sky = 100 - cloud_pct`

`slot_comfort = .45*temperature + .35*rain + .15*wind + .05*clear_sky`

Humidity is stored but not independently scored. Clear versus fully overcast
can change a slot by at most five overall points. Rain probability is not
rain intensity or a whole-trip probability. Wind is forecast speed, not gusts.

## Searcher: preferred conditions

Selected temperature band stays fixed for the whole search. Seasons only seed
the initial/reset values. The same temperature decline applies.

Rain targets: Low [0,30]%, Medium (30,60]%, High (60,100]%. These express desired
conditions, not maximum tolerance. High rewards high probability; Medium
rewards the middle and penalizes both drier and wetter conditions.

Wind targets: Gentle [0,20), Moderate [20,29), Fresh [29,39), Strong [39,50)
km/h. 50+ is displayed as near gale or stronger, not offered as a preferred
tourism category. Descriptions group the [Beaufort scale](https://www.rmets.org/metmatters/the-beaufort-wind-scale).
Labels are not official warning levels. Searcher indicates high forecast wind (39+ km/h) only when
one of its top five recommendations is affected, regardless of score.
Dashboard does not show this warning banner.

For a chosen band [L,U], distance outside = max(L-x, x-U, 0):

- Rain component: max(0, 100 - 2*distance outside), per percentage point.
- Wind component: max(0, 100 - 5*distance outside), per km/h.
- Searcher slot match: .45*temperature + .35*rain_match + .20*wind_match.

Clouds are excluded from Searcher scoring to avoid contradicting a preference
for rain. At shared category boundaries the continuous score reaches 100 from
both sides; exact categorical membership follows the intervals above. The
internal all-preferences percentage uses exact membership, not rounded scores.
It is retained as an analytical diagnostic and is not displayed in the Searcher.
Initial/reset categories derive from the validated product reference. Its
current 30% rain and 25 km/h wind values seed Low rain and Moderate wind.
If those reference values change, both category labels and numeric widget
codes move to the same next accepting preset; scoring must not retain the old
labels. Existing numeric widget values migrate in the same way.

## Window aggregation and driving

For N available required daytime slots, k = ceil(N/4).

`weather_score = .8*mean(all slot scores) + .2*mean(lowest k slot scores)`

Use full precision until display. This rewards consistency. No future days
are weighted differently. Missing required slots make a window unavailable,
not a shorter, selectively favourable sample.

Both views: `driving_penalty = min(2*one_way_driving_hours, 15)`.

`destination_or_trip_score = max(0, weather_score - driving_penalty)`

Examples: weather 90 and a five-hour drive -> 80; weather 86 and a one-hour
drive -> 84. Reference driving estimates are from Madrid Km0, not live traffic.

Dashboard ranking: descending unrounded destination score; exact ties share
competition rank (1,1,3), displayed in city-ID order. Searcher ordering:
final score descending, match descending, driving minutes ascending, city ID.

## Visual contract

| Visual | Metric |
| --- | --- |
| Dashboard average/leader/top five/map rank and color | Destination score after driving |
| Driving-band top three | Destination score within each band |
| Destination-score-versus-driving scatter vertical axis | Whole-window Destination score after driving; horizontal axis is hours |
| Daily weather heatmap | Daily Destination score after driving, same engine and 80/20 aggregation |
| Heatmap row order | Mean of available daily Destination scores; missing days excluded and partial coverage labelled |
| Searcher cards/full ranking | Trip score after driving |
| Full Dashboard table | Destination score, penalty, source metrics, coverage, dates, freshness and unavailable reasons |

Only **Trip score /100** (Searcher) and **Destination score /100** (Dashboard)
are displayed, both from `final_score`. Every whole-window Dashboard visual
uses the same loaded rows and `destination_ranks`; the scatter scale is 0–100.
A one-day overview must equal its one-day heatmap score. Daily avg is the
equal-weight mean of available daily scores, with missing days/partial counts
labelled. It can differ from nonlinear whole-window aggregation and does not
replace that score.

`weather_match_pct` retains its internal name for compatibility but means an
index out of 100, not a probability. Pre-driving match, pass counts and
`all_preferences_pct` remain internal diagnostics. Searcher omits its Status
and daytime-slot-count columns; unavailable explanations remain visible.
Completeness is still validated: hidden diagnostics do not permit partial
forecasts into rankings. Scores are recomputed, never stored in the raw CSV.

Concise hovers show relevant values; diagnostic metadata stays in the catalogue.
Duration display uses h:mm; source/internal driving values remain minutes.
A high score is not safety advice.

The map uses fixed bands: red [0,20), orange [20,40), yellow [40,60), light green
[60,80), dark green [80,100], with a numeric legend. It never stretches the
scale to the current sample. Grey means unavailable; blue is the unranked
Madrid origin. Heatmap cells retain a green daily-score scale and numeric text.

Rain and wind KPI cards first average each destination's selected daytime
slots, then average equally across complete ranked destinations. With all data
present the denominator is 83; otherwise show N/83 and never zero-fill missing
cities. These are forecast averages, not rainfall totals, probability of rain
anywhere in Spain, or maximum values. Catalogue rain/wind columns explicitly
show slot maxima; temperature is the mean. Empty KPIs show an em dash.

## Missing data, refresh and validation

Required for both modes: temperature, rain probability, wind. Dashboard also
requires cloud cover. Missing cloud is not assumed clear and weights are not
redistributed. Searcher may still score those records because it does not use
cloud cover. Unavailable destinations stay visible with no invented score.

New searches, first Dashboard opening, window changes and Refresh recalculate
from suitable saved data. The [API contract](WEATHER_API_CONTRACT.md#current-reuse-and-scoring-boundary)
owns three-hour/provider-identity reuse, refresh and save/recovery rules.
There is no background collector; availability is not guaranteed and errors
remain explicit.

Acceptance uses independently calculated synthetic examples, frozen genuine
CSV replays, season and interval boundaries, missing fields, travel caps,
mode separation, request/cache/storage recovery and Streamlit integration.
Teacher requirements remain: genuine accumulated data, OOP/API/package design,
three analyses across comparison and derived metrics, two labelled charts,
transparent AI records and actual team contributions. A passing test suite
does not substitute for browser/Mac/clean-clone review or authorize publication.

`comfort-v2.2` identifies the current session-result contract, including the
added mean fields. Reruns discard incompatible results. A stale service object
after Python code reload is replaced only after its pending unsaved records
have been recovered; failure keeps the old service and recovery guidance.
This supports local editing, not lossless recovery after a process crash.

## Current displayed metrics and data refresh

See the consolidated [visual contract](#visual-contract) and
[missing-data/refresh rules](#missing-data-refresh-and-validation) above.
Validation evidence is indexed in [Phase 5](PHASE5_QUALITY_REVIEW.md);
[Phase 6](PHASE6_DELIVERY.md) owns acceptance and publication gates.
