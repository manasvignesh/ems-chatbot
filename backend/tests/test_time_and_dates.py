from datetime import date, datetime
import pytest
from app.core.time import (
    build_time_context_prompt,
    format_human_date,
    format_human_datetime,
    get_current_time,
    get_timezone,
    parse_relative_date_range,
    set_mock_datetime,
)


@pytest.fixture(autouse=True)
def cleanup_mock_time():
    yield
    set_mock_datetime(None)


def test_authoritative_timezone():
    kolkata_tz = get_timezone("Asia/Kolkata")
    now = get_current_time("Asia/Kolkata")
    assert now.tzinfo is not None


def test_relative_date_parsing_standard_wednesday():
    # Mock Wednesday, 2026-09-02
    kolkata_tz = get_timezone("Asia/Kolkata")
    mock_dt = datetime(2026, 9, 2, 14, 30, tzinfo=kolkata_tz)
    set_mock_datetime(mock_dt)

    # Today
    start, end, label = parse_relative_date_range("What events are today?")
    assert start == date(2026, 9, 2)
    assert end == date(2026, 9, 2)
    assert label == "today"

    # Tomorrow / Tomorow
    start, end, label = parse_relative_date_range("What is happening tomorow?")
    assert start == date(2026, 9, 3)
    assert end == date(2026, 9, 3)
    assert label == "tomorrow"

    # Yesterday
    start, end, label = parse_relative_date_range("events yesterday")
    assert start == date(2026, 9, 1)

    # This Week (Monday Aug 31 to Sunday Sep 6)
    start, end, label = parse_relative_date_range("workshops this week")
    assert start == date(2026, 8, 31)  # Monday
    assert end == date(2026, 9, 6)    # Sunday
    assert label == "this week"

    # This Weekend (Saturday Sep 5 to Sunday Sep 6)
    start, end, label = parse_relative_date_range("events this weekend")
    assert start == date(2026, 9, 5)  # Saturday
    assert end == date(2026, 9, 6)    # Sunday
    assert label == "this weekend"

    # This Month (Sep 1 to Sep 30)
    start, end, label = parse_relative_date_range("any hackathons this month")
    assert start == date(2026, 9, 1)
    assert end == date(2026, 9, 30)
    assert label == "this month"


def test_year_and_month_boundary_rollover():
    # Mock Dec 31, 2026 at 23:55 PM
    kolkata_tz = get_timezone("Asia/Kolkata")
    mock_dt = datetime(2026, 12, 31, 23, 55, tzinfo=kolkata_tz)
    set_mock_datetime(mock_dt)

    # Tomorrow should roll over to Jan 1, 2027
    start, end, label = parse_relative_date_range("events tomorrow")
    assert start == date(2027, 1, 1)
    assert end == date(2027, 1, 1)

    # Next month should be Jan 2027
    start, end, label = parse_relative_date_range("events next month")
    assert start == date(2027, 1, 1)
    assert end == date(2027, 1, 31)


def test_sunday_week_boundary():
    # Mock Sunday, 2026-09-06
    kolkata_tz = get_timezone("Asia/Kolkata")
    mock_dt = datetime(2026, 9, 6, 10, 0, tzinfo=kolkata_tz)
    set_mock_datetime(mock_dt)

    # This week should be Aug 31 to Sep 6
    start, end, label = parse_relative_date_range("events this week")
    assert start == date(2026, 8, 31)
    assert end == date(2026, 9, 6)

    # Next week should be Sep 7 to Sep 13
    start, end, label = parse_relative_date_range("events next week")
    assert start == date(2026, 9, 7)
    assert end == date(2026, 9, 13)


def test_format_human_date():
    d = date(2026, 9, 4)
    formatted = format_human_date(d)
    assert formatted == "Friday, 4 September 2026"
