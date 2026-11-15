"""Independent numeric oracle for frozen CSV acceptance, no app imports."""

from math import ceil


def reference_score(values, mode="dashboard", low=16, high=24,
                    rain_band=(0, 30), wind_band=(0, 25)):
    scores = []
    for t, rain, wind, cloud in values:
        temperature = 100 - (low - t) * 5 if t < low else (
            100 - (t - high) * 7.5 if t > high else 100)
        temperature = max(0, temperature)
        if mode == "dashboard":
            wind_points = (100 if wind <= 10 else
                           115 - 1.5 * wind if wind <= 20 else
                           135 - 2.5 * wind if wind <= 30 else
                           150 - 3 * wind if wind <= 40 else
                           90 - 1.5 * wind if wind <= 60 else 0)
            scores.append((45 * temperature + 35 * (100 - rain)
                           + 15 * wind_points + 5 * (100 - cloud)) / 100)
        else:
            rain_gap = max(rain_band[0] - rain, rain - rain_band[1], 0)
            wind_gap = max(wind_band[0] - wind, wind - wind_band[1], 0)
            scores.append((45 * temperature + 35 * max(0, 100 - 2 * rain_gap)
                           + 20 * max(0, 100 - 5 * wind_gap)) / 100)
    tail = sorted(scores)[:ceil(len(scores) / 4)]
    return (4 * sum(scores) / len(scores) + sum(tail) / len(tail)) / 5
