from datetime import date

from django.utils.formats import date_format


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


def period_months_label(
    date_from: date, date_to: date, *, show_year: bool = True
) -> str:
    """Human period e.g. « nov.–déc. 2026 » or « nov. 2026 – janv. 2027 » (locale-aware)."""
    m_start = date_format(date_from, "M")
    m_end = date_format(date_to, "M")
    y_start = date_from.year
    y_end = date_to.year

    if not show_year:
        if date_from.month == date_to.month and y_start == y_end:
            return m_start
        if y_start == y_end:
            return f"{m_start}–{m_end}"
        return f"{m_start} – {m_end}"

    if y_start == y_end and date_from.month == date_to.month:
        return f"{m_start} {y_start}"
    if y_start == y_end:
        return f"{m_start}–{m_end} {y_start}"
    return f"{m_start} {y_start} – {m_end} {y_end}"


def period_months_from_weeks(
    year: int,
    week_from: int,
    week_to: int,
    *,
    show_year: bool = True,
) -> str:
    date_from, date_to = iso_week_range_to_dates(year, week_from, week_to)
    return period_months_label(date_from, date_to, show_year=show_year)


SEASON_SHORTCUTS = {
    "transatlantic": {"label": "Transatlantique (nov.–déc.)", "week_from": 44, "week_to": 52},
    "pacific_puddle": {"label": "Pacific Puddle Jump (mar.–mai)", "week_from": 10, "week_to": 22},
    "mediterranean": {"label": "Méditerranée (mai–oct.)", "week_from": 18, "week_to": 42},
}
