
from apps.listings.iso_weeks import iso_week_range_to_dates, weeks_overlap


def test_iso_week_range():
    start, end = iso_week_range_to_dates(2026, 44, 46)
    assert start.weekday() == 0
    assert end.weekday() == 6
    assert start.isocalendar().week == 44


def test_weeks_overlap_adjacent():
    assert weeks_overlap(2026, 44, 46, 2026, 45, 48)
    assert not weeks_overlap(2026, 10, 12, 2026, 20, 22)
