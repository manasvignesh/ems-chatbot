import calendar
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo
from app.core.config import settings

# Global time provider hook for testing
_MOCK_DATETIME: Optional[datetime] = None


def set_mock_datetime(dt: Optional[datetime]):
    """Set a mock datetime for automated tests."""
    global _MOCK_DATETIME
    _MOCK_DATETIME = dt


def get_timezone(timezone_name: Optional[str] = None):
    """Retrieve timezone object with fallback to Asia/Kolkata +05:30."""
    tz_str = timezone_name or settings.EMS_TIMEZONE
    try:
        return ZoneInfo(tz_str)
    except Exception:
        # Fallback to IST +05:30
        return timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")


def get_current_time(timezone_name: Optional[str] = None) -> datetime:
    """Get the authoritative current datetime in the specified timezone."""
    tz = get_timezone(timezone_name)

    if _MOCK_DATETIME is not None:
        if _MOCK_DATETIME.tzinfo is None:
            return _MOCK_DATETIME.replace(tzinfo=tz)
        return _MOCK_DATETIME.astimezone(tz)

    return datetime.now(tz)


def format_human_date(d: date) -> str:
    """Format a date in a clean, human-friendly style (e.g., 'Friday, 4 September 2026')."""
    return d.strftime("%A, %d %B %Y").replace(" 0", " ")


def format_human_datetime(dt: datetime) -> str:
    """Format datetime with friendly time (e.g., 'Friday, 4 September 2026 at 9:30 AM')."""
    date_part = format_human_date(dt.date())
    time_part = dt.strftime("%I:%M %p").lstrip("0")
    return f"{date_part} at {time_part}"


def build_time_context_prompt(dt: Optional[datetime] = None, timezone_name: Optional[str] = None) -> str:
    """Build an authoritative current time context string to inject into Gemini prompt."""
    now = dt or get_current_time(timezone_name)
    tz_str = timezone_name or settings.EMS_TIMEZONE

    return (
        f"[CURRENT AUTHORITATIVE TIME CONTEXT]\n"
        f"Current Date: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})\n"
        f"Current Local Time: {now.strftime('%I:%M %p')} ({tz_str})\n"
        f"Current Year: {now.year}, Month: {now.strftime('%B')}\n"
        f"All event dates and schedules are relative to this current time."
    )


def parse_relative_date_range(
    text: str, current_dt: Optional[datetime] = None
) -> Tuple[Optional[date], Optional[date], Optional[str]]:
    """
    Parse relative date expressions in text and return (start_date, end_date, matched_expression).
    Handles 'today', 'tomorrow', 'this week', 'next week', 'this weekend', 'this month', 'next month', etc.
    """
    now = current_dt or get_current_time()
    today = now.date()
    lower_text = text.lower()

    # 1. Today / Todai
    if re.search(r"\b(today|todai|tonight|this\s+evening|this\s+morning)\b", lower_text):
        return today, today, "today"

    # 2. Tomorrow / Tomorow
    if re.search(r"\b(tomorrow|tomorow|tommorow|tomrw)\b", lower_text):
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow, "tomorrow"

    # 3. Yesterday
    if re.search(r"\b(yesterday)\b", lower_text):
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday, "yesterday"

    # 4. This Weekend
    if re.search(r"\b(this\s+weekend|weekend)\b", lower_text):
        # Saturday is weekday 5, Sunday is weekday 6
        days_until_saturday = (5 - today.weekday()) % 7
        saturday = today + timedelta(days=days_until_saturday)
        sunday = saturday + timedelta(days=1)
        return saturday, sunday, "this weekend"

    # 5. This Week
    if re.search(r"\b(this\s+week|current\s+week)\b", lower_text):
        # Monday is weekday 0, Sunday is weekday 6
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return monday, sunday, "this week"

    # 6. Next Week
    if re.search(r"\b(next\s+week)\b", lower_text):
        next_monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
        next_sunday = next_monday + timedelta(days=6)
        return next_monday, next_sunday, "next week"

    # 7. This Month
    if re.search(r"\b(this\s+month|current\s+month)\b", lower_text):
        first_day = today.replace(day=1)
        _, last_day_num = calendar.monthrange(today.year, today.month)
        last_day = today.replace(day=last_day_num)
        return first_day, last_day, "this month"

    # 8. Next Month
    if re.search(r"\b(next\s+month)\b", lower_text):
        if today.month == 12:
            first_day = date(today.year + 1, 1, 1)
        else:
            first_day = date(today.year, today.month + 1, 1)
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        last_day = first_day.replace(day=last_day_num)
        return first_day, last_day, "next month"

    return None, None, None
