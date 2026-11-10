from datetime import date


def iso_week_range_to_dates(year: int, week_from: int, week_to: int) -> tuple[date, date]:
    """Return Monday of week_from and Sunday of week_to (handles year wrap via caller)."""
    date_from = date.fromisocalendar(year, week_from, 1)
    if week_to >= week_from:
        date_to = date.fromisocalendar(year, week_to, 7)
    else:
        date_to = date.fromisocalendar(year + 1, week_to, 7)
    return date_from, date_to


def weeks_overlap(
    y1: int, wf1: int, wt1: int, y2: int, wf2: int, wt2: int
) -> bool:
    a_start, a_end = iso_week_range_to_dates(y1, wf1, wt1)
    b_start, b_end = iso_week_range_to_dates(y2, wf2, wt2)
    return a_start <= b_end and b_start <= a_end


SEASON_SHORTCUTS = {
    "transatlantic": {"label": "Transatlantique (nov.–déc.)", "week_from": 44, "week_to": 52},
    "pacific_puddle": {"label": "Pacific Puddle Jump (mar.–mai)", "week_from": 10, "week_to": 22},
    "mediterranean": {"label": "Méditerranée (mai–oct.)", "week_from": 18, "week_to": 42},
}
