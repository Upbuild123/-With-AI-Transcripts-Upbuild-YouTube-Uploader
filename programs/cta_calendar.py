from datetime import date
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CTASession:
    date: date
    season: str
    session_label: str
    class_title: str
    facilitators: List[str]


CTA_CALENDAR: List[CTASession] = [
    # ── Spring 2026 (past) ───────────────────────────────────────────────────
    CTASession(date(2026, 3, 17), "Spring 2026", "Orientation",
               "Orientation", []),
    CTASession(date(2026, 3, 24), "Spring 2026", "S1 Part 1",
               "Checkmate! The Yoga of Existential Crisis Part I",
               ["Hari", "Rasanath", "Tzipi"]),
    CTASession(date(2026, 4, 7),  "Spring 2026", "S1 Part 2",
               "Checkmate! The Yoga of Existential Crisis Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 4, 14), "Spring 2026", "S2 Part 1",
               "Identity: Unveiling the Existence of the Soul Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 4, 21), "Spring 2026", "S2 Part 2",
               "Identity: Unveiling the Existence of the Soul Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 4, 28), "Spring 2026", "S3 Part 1",
               "Cracking Karma: The Universal Network of Actions Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 5, 5),  "Spring 2026", "S3 Part 2",
               "Cracking Karma: The Universal Network of Actions Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 5, 12), "Spring 2026", "S4 Part 1",
               "Where's My Mind?: Understanding Vedic Psychology Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 5, 19), "Spring 2026", "S4 Part 2",
               "Where's My Mind?: Understanding Vedic Psychology Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 6, 2),  "Spring 2026", "S5 Part 1",
               "Awakening: Plugging the Mind into the Soul Part I", []),
    # ── Spring 2026 (upcoming) ───────────────────────────────────────────────
    CTASession(date(2026, 6, 9),  "Spring 2026", "S5 Part 2",
               "Awakening: Plugging the Mind into the Soul Part II", []),
    CTASession(date(2026, 6, 16), "Spring 2026", "S6 Part 1",
               "Awakening: Plugging the Mind into the Soul - Conclusion Part I", []),
    CTASession(date(2026, 6, 23), "Spring 2026", "S6 Part 2",
               "Awakening: Plugging the Mind into the Soul - Conclusion Part II", []),
    # ── Fall 2026 ─────────────────────────────────────────────────────────────
    CTASession(date(2026, 9, 8),  "Fall 2026", "Second Semester Orientation",
               "Second Semester Orientation", []),
    CTASession(date(2026, 9, 22), "Fall 2026", "S7 Part 1",
               "Moods and Modes: How the Material World Affects Us Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 9, 29), "Fall 2026", "S7 Part 2",
               "Moods and Modes: How the Material World Affects Us Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 10, 6),  "Fall 2026", "S8 Part 1",
               "Faith and Knowledge: The Epistemology of Experience Part I", []),
    CTASession(date(2026, 10, 13), "Fall 2026", "S8 Part 2",
               "Faith and Knowledge: The Epistemology of Experience Part II", []),
    CTASession(date(2026, 10, 20), "Fall 2026", "S9 Part 1",
               "The Super-String Theory: Exploring the Origins of the Self Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 10, 27), "Fall 2026", "S9 Part 2",
               "The Super-String Theory: Exploring the Origins of the Self Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 11, 3),  "Fall 2026", "S10 Part 1",
               "Bhakti: The Yoga of Devotion Part I",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 11, 10), "Fall 2026", "S10 Part 2",
               "Bhakti: The Yoga of Devotion Part II",
               ["Hari", "Rasanath", "Tzipi", "Vipin"]),
    CTASession(date(2026, 11, 17), "Fall 2026", "S11 Part 1",
               "Unfettered: Being the Change You Wish to See Part I", []),
    CTASession(date(2026, 12, 1),  "Fall 2026", "S11 Part 2",
               "Unfettered: Being the Change You Wish to See Part II", []),
    CTASession(date(2026, 12, 8),  "Fall 2026", "S12 Part 1",
               "Unfettered: Being the Change You Wish to See - Conclusion Part I", []),
    CTASession(date(2026, 12, 15), "Fall 2026", "S12 Part 2",
               "Unfettered: Being the Change You Wish to See - Conclusion Part II", []),
]

_CALENDAR_BY_DATE: Dict[date, CTASession] = {s.date: s for s in CTA_CALENDAR}


def lookup_session(d: date) -> CTASession:
    """Return the CTASession for a given date. Raises KeyError if not found."""
    if d not in _CALENDAR_BY_DATE:
        raise KeyError(f"No CTA session found for {d}. Check cta_calendar.py.")
    return _CALENDAR_BY_DATE[d]


def scheduled_dates() -> List[date]:
    """Return all CTA session dates in chronological order."""
    return sorted(_CALENDAR_BY_DATE.keys())
