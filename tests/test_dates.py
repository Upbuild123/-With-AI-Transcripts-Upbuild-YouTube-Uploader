from datetime import date
from programs.dates import (
    most_recent_weekday,
    fmt_mon_period_dd_yyyy,
    fmt_mon_d_yyyy,
    fmt_month_dd_yyyy,
    fmt_yyyymmdd_dot,
)

def test_most_recent_weekday_today():
    tuesday = date(2026, 6, 9)  # a Tuesday
    assert most_recent_weekday("Tuesday", _today=tuesday) == date(2026, 6, 9)

def test_most_recent_weekday_past():
    thursday = date(2026, 6, 11)
    assert most_recent_weekday("Tuesday", _today=thursday) == date(2026, 6, 9)

def test_most_recent_weekday_week_wrap():
    monday = date(2026, 6, 8)
    assert most_recent_weekday("Friday", _today=monday) == date(2026, 6, 5)

def test_fmt_mon_period_dd_yyyy():
    assert fmt_mon_period_dd_yyyy(date(2026, 6, 2)) == "Jun. 2, 2026"
    assert fmt_mon_period_dd_yyyy(date(2026, 11, 10)) == "Nov. 10, 2026"

def test_fmt_mon_d_yyyy():
    assert fmt_mon_d_yyyy(date(2026, 6, 2)) == "Jun 2, 2026"
    assert fmt_mon_d_yyyy(date(2026, 11, 10)) == "Nov 10, 2026"

def test_fmt_month_dd_yyyy():
    assert fmt_month_dd_yyyy(date(2026, 6, 2)) == "June 2, 2026"
    assert fmt_month_dd_yyyy(date(2026, 11, 10)) == "November 10, 2026"

def test_fmt_yyyymmdd_dot():
    assert fmt_yyyymmdd_dot(date(2026, 6, 7)) == "2026.06.07"
    assert fmt_yyyymmdd_dot(date(2026, 11, 3)) == "2026.11.03"
