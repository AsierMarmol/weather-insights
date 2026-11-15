"""Pure executive summaries over the validated overview and catalog.

No network, storage, clocks or alternative scoring formulas here.
"""

from weather_app.analytics import AVAILABLE, destination_ranks

DRIVING_BANDS = (
    ("Under 2 hours", 0, 120),
    ("2–under 4 hours", 120, 240),
    ("4–under 6 hours", 240, 360),
    ("6 hours or more", 360, float("inf")),
)


def executive_summary(rows, catalog):
    """One destination, one vote; unavailable rows never imply safe weather.

    Equal destination scores share competition ranks. Stable city IDs break
    display-order ties, never rounded scores.
    Final scores include driving penalties.
    """
    places = {d.city_id: d for d in catalog}
    available = sorted(
        (dict(r) for r in rows if r["status"] == AVAILABLE),
        key=lambda r: (-r["final_score"], r["city_id"]),
    )
    scores = [r["final_score"] for r in available]
    ranks = destination_ranks(available)
    for row in available:
        place = places[row["city_id"]]
        row.update(
            destination=place.city, region=place.region,
            car_distance_km=place.car_distance_km,
            car_duration_min=place.car_duration_min,
            rank=ranks[row["city_id"]],
        )
    count = len(available)
    bands = {
        label: [r for r in available
                if low <= r["car_duration_min"] < high][:3]
        for label, low, high in DRIVING_BANDS
    }
    return {
        "total": len(catalog), "available": count,
        "average_score": sum(scores) / count if count else None,
        "average_rain_probability_pct": sum(
            r["mean_precipitation_probability_pct"] for r in available
        ) / count if count else None,
        "average_wind_kmh": sum(
            r["mean_wind_kmh"] for r in available
        ) / count if count else None,
        "leaders": [r for r in available if r["rank"] == 1],
        "top_five": available[:5], "rows": available, "bands": bands,
    }


def decision_signal(summary):
    """Deterministic statements of computed facts, including tied leaders."""
    if not summary["available"]:
        return (
            "No complete usable forecasts are available for this window. "
            "All destinations remain on the map; load or refresh the "
            "overview to check their weather."
        )
    leaders = summary["leaders"]
    first = leaders[0]
    lead = (
        f'{first["destination"]} leads'
        if len(leaders) == 1 else
        f'{len(leaders)} destinations share first place, including '
        f'{first["destination"]},'
    )
    return (
        f'{lead} with a destination score of '
        f'{first["final_score"]:.1f}/100. '
        f'Among {summary["available"]} ranked destinations, '
        f'average daytime rain probability is '
        f'{summary["average_rain_probability_pct"]:.1f}% and average wind '
        f'is {summary["average_wind_kmh"]:.1f} km/h. '
        'Ranking includes 2 points per driving '
        'hour, capped at 15; all views use Destination score.'
    )


def daily_score_order(cells, catalog):
    """Order by equal-weight mean of available daily scores; no-data last.

    Use unrounded scores and city ID for deterministic ties. Missing days
    never count as zero; expose coverage so partial averages are explicit.
    This ordering does not replace the whole-window Dashboard ranking.
    """
    days = {cell['day'] for cell in cells}
    lookup = {(c['city_id'], c['day']): c['score'] for c in cells}
    result = []
    for place in catalog:
        scores = [lookup[(place.city_id, day)] for day in days
                  if lookup.get((place.city_id, day)) is not None]
        result.append({
            'city_id': place.city_id,
            'average_score': sum(scores) / len(scores) if scores else None,
            'available_days': len(scores), 'total_days': len(days),
        })
    return sorted(result, key=lambda row: (
        row['average_score'] is None,
        -row['average_score'] if row['average_score'] is not None else 0,
        row['city_id'],
    ))
