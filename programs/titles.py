from datetime import date
from typing import Optional
from programs.dates import fmt_mon_period_dd_yyyy, fmt_mon_d_yyyy, fmt_month_dd_yyyy, fmt_yyyymmdd_dot


def build_cta_title(season: str, session_label: str, recording_type: str, d: date) -> str:
    return f"The Call To Awaken - {season} - {session_label} - {recording_type} - {fmt_mon_period_dd_yyyy(d)}"


def build_rwwa_title(title: str, part_num: int, d: date) -> str:
    return f"RWWA - {title} - Part {part_num} - {fmt_mon_period_dd_yyyy(d)}"


def build_bhakti_sastri_title(verses: str, part_num: Optional[int], d: date) -> str:
    part_str = f" - Part {part_num}" if part_num else ""
    return f"Bhakti Sastri - Bhagavad Gita - {verses}{part_str} - {fmt_month_dd_yyyy(d)}"


def build_committed_bhakti_title(session_num: int, topics: str, d: date) -> str:
    return f"Session {session_num} - Committed Bhakti ({fmt_yyyymmdd_dot(d)}) {topics}"


def build_morning_rounds_title(session_num: int, topic: str, d: date) -> str:
    return f"Morning Rounds - {session_num} - {topic} - {fmt_mon_d_yyyy(d)}"


def build_library_live_title(episode_num: int, title: str, d: date) -> str:
    return f"{episode_num} - {title} ({fmt_yyyymmdd_dot(d)})"
