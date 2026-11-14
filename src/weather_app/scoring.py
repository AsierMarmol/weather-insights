"""Pure, versioned tourism scores. These are preferences, not safety advice."""

from math import ceil
from zoneinfo import ZoneInfo

VERSION = "comfort-v2.2"
MADRID = ZoneInfo("Europe/Madrid")
RAIN_BANDS = {"Low": (0, 30), "Medium": (30, 60), "High": (60, 100)}
WIND_BANDS = {
    "Gentle": (0, 20), "Moderate": (20, 29),
    "Fresh": (29, 39), "Strong": (39, 50),
}
WIND_ANCHORS = ((0, 100), (10, 100), (20, 85), (30, 60),
                (40, 30), (60, 0))
SEASONAL_BANDS = ((10, 18),) * 2 + ((18, 26),) * 3 + ((22, 30),) * 3 + (
    (16, 24),) * 3 + ((10, 18),)


def range_score(value, low, high, below, above):
    """Full points inside a band; continuous linear decline on either side."""
    return max(0.0, 100 - below * max(low - value, 0)
               - above * max(value - high, 0))


def dashboard_wind_score(speed):
    for (a, sa), (b, sb) in zip(WIND_ANCHORS, WIND_ANCHORS[1:]):
        if speed <= b:
            return sa + (sb - sa) * (speed - a) / (b - a)
    return 0.0


def wind_label(speed):
    for label, (_, upper) in WIND_BANDS.items():
        if speed < upper:
            return label
    return "Near gale or stronger"


def aggregate(scores):
    """80% mean + 20% mean of the lowest ceil(N/4) slots."""
    if not scores:
        raise ValueError("Cannot score an empty forecast window")
    worst = sorted(scores)[:ceil(len(scores) / 4)]
    return .8 * sum(scores) / len(scores) + .2 * sum(worst) / len(worst)


def slot_score(record, preferences):
    """Return weighted comfort and exact target flags for one daytime slot.

    Dashboard temperature follows each slot's Madrid month. Searcher target
    bands stay fixed for the search. Cloud is required only for Dashboard.
    Exact rain boundaries: Low [0,30], Medium (30,60], High (60,100].
    Wind bands are lower-inclusive, upper-exclusive. Continuous scores meet
    at boundaries even when the exact category label changes.
    """
    p = preferences
    dashboard = p.scoring_mode == "dashboard"
    month = record.valid_at_utc.astimezone(MADRID).month
    low, high = (p.seasonal_bands[month - 1]
                 if dashboard else (p.temperature_min_c, p.temperature_max_c))
    temp = range_score(record.temperature_c, low, high, 5, 7.5)
    t_ok = low <= record.temperature_c <= high
    rain, wind = record.precipitation_probability_pct, record.wind_kmh
    if dashboard:
        score = (.45 * temp + .35 * (100 - rain)
                 + .15 * dashboard_wind_score(wind)
                 + .05 * (100 - record.cloud_pct))
        return score, (t_ok, rain <= p.max_precipitation_probability_pct,
                       wind <= p.max_wind_kmh)
    r_low, r_high = RAIN_BANDS.get(
        p.rain_preference, (0, p.max_precipitation_probability_pct))
    w_low, w_high = WIND_BANDS.get(p.wind_preference, (0, p.max_wind_kmh))
    r_ok = (r_low <= rain <= r_high if r_low == 0 else r_low < rain <= r_high)
    w_ok = (w_low <= wind < w_high if p.wind_preference
            else w_low <= wind <= w_high)
    score = (.45 * temp + .35 * range_score(rain, r_low, r_high, 2, 2)
             + .20 * range_score(wind, w_low, w_high, 5, 5))
    return score, (t_ok, r_ok, w_ok)
