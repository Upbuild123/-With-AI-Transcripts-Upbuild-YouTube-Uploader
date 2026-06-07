from datetime import date
from programs.cta_calendar import lookup_session, CTASession

def test_lookup_spring_session():
    s = lookup_session(date(2026, 6, 9))
    assert s.season == "Spring 2026"
    assert s.session_label == "S5 Part 2"
    assert s.class_title == "Awakening: Plugging the Mind into the Soul Part II"
    assert s.facilitators == []

def test_lookup_fall_session_with_facilitators():
    s = lookup_session(date(2026, 9, 22))
    assert s.season == "Fall 2026"
    assert s.session_label == "S7 Part 1"
    assert "Hari" in s.facilitators
    assert "Rasanath" in s.facilitators
    assert "Tzipi" in s.facilitators
    assert "Vipin" in s.facilitators

def test_lookup_orientation():
    s = lookup_session(date(2026, 9, 8))
    assert s.season == "Fall 2026"
    assert s.session_label == "Second Semester Orientation"
    assert s.facilitators == []

def test_lookup_unknown_date_raises():
    import pytest
    with pytest.raises(KeyError):
        lookup_session(date(2026, 7, 1))
