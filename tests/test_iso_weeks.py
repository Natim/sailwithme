from apps.listings.iso_weeks import (
    iso_week_range_to_dates,
    period_months_from_weeks,
    weeks_overlap,
)


def test_iso_week_range():
    start, end = iso_week_range_to_dates(2026, 44, 46)
    assert start.weekday() == 0
    assert end.weekday() == 6
    assert start.isocalendar().week == 44


def test_weeks_overlap_adjacent():
    assert weeks_overlap(2026, 44, 46, 2026, 45, 48)
    assert not weeks_overlap(2026, 10, 12, 2026, 20, 22)


def test_period_months_no_iso_week_prefix():
    label = period_months_from_weeks(2026, 44, 52, show_year=True)
    assert "S" not in label
    assert "2026" in label


def test_period_months_season_shortcut_style():
    label = period_months_from_weeks(2026, 44, 52, show_year=False)
    assert "2026" not in label
    assert "–" in label or label  # single month or range


def test_popular_route_months_are_written_in_full():
    from django.utils import translation

    with translation.override("fr"):
        label = period_months_from_weeks(2026, 44, 52, show_year=False, full_months=True)
    assert label == "octobre–décembre"

    with translation.override("en"):
        label = period_months_from_weeks(2026, 44, 52, show_year=False, full_months=True)
    assert label == "October–December"

    with translation.override("fr"):
        abbreviated = period_months_from_weeks(2026, 44, 52, show_year=False)
    assert abbreviated != "octobre–décembre"
