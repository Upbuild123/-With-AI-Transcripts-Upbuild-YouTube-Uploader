from datetime import date, timedelta, datetime, timezone
from typing import Optional
import zoneinfo

EASTERN = zoneinfo.ZoneInfo("America/New_York")

WEEKDAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6,
}

def today_eastern() -> date:
    return datetime.now(EASTERN).date()

def most_recent_weekday(weekday_name: str, _today: Optional[date] = None) -> date:
    today = _today or today_eastern()
    target = WEEKDAY_MAP[weekday_name]
    days_behind = (today.weekday() - target) % 7
    return today - timedelta(days=days_behind)

def fmt_mon_period_dd_yyyy(d: date) -> str:
    return f"{d.strftime('%b')}. {d.day}, {d.year}"

def fmt_mon_d_yyyy(d: date) -> str:
    return f"{d.strftime('%b')} {d.day}, {d.year}"

def fmt_month_dd_yyyy(d: date) -> str:
    return f"{d.strftime('%B')} {d.day}, {d.year}"

def fmt_yyyymmdd_dot(d: date) -> str:
    return d.strftime("%Y.%m.%d")
