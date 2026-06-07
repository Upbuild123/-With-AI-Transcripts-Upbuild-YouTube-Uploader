from datetime import date
from programs.titles import (
    build_cta_title,
    build_rwwa_title,
    build_bhakti_sastri_title,
    build_committed_bhakti_title,
    build_morning_rounds_title,
    build_library_live_title,
)

D = date(2026, 6, 9)

def test_cta_full_group():
    assert build_cta_title("Spring 2026", "S5 Part 2", "Full Group", D) == \
        "The Call To Awaken - Spring 2026 - S5 Part 2 - Full Group - Jun. 9, 2026"

def test_cta_facilitator():
    assert build_cta_title("Fall 2026", "S7 Part 1", "Hari", date(2026, 9, 22)) == \
        "The Call To Awaken - Fall 2026 - S7 Part 1 - Hari - Sep. 22, 2026"

def test_rwwa():
    assert build_rwwa_title("The Art of Listening", 3, D) == \
        "RWWA - The Art of Listening - Part 3 - Jun. 9, 2026"

def test_bhakti_sastri_no_part():
    assert build_bhakti_sastri_title("2.1-2.5", None, D) == \
        "Bhakti Sastri - Bhagavad Gita - 2.1-2.5 - June 9, 2026"

def test_bhakti_sastri_with_part():
    assert build_bhakti_sastri_title("2.1-2.5", 2, D) == \
        "Bhakti Sastri - Bhagavad Gita - 2.1-2.5 - Part 2 - June 9, 2026"

def test_committed_bhakti():
    assert build_committed_bhakti_title(14, "Identity and Purpose", date(2026, 6, 5)) == \
        "Session 14 - Committed Bhakti (2026.06.05) Identity and Purpose"

def test_morning_rounds():
    assert build_morning_rounds_title(42, "Japa Practice", D) == \
        "Morning Rounds - 42 - Japa Practice - Jun 9, 2026"

def test_library_live():
    assert build_library_live_title(7, "Finding Your Dharma", date(2026, 6, 5)) == \
        "7 - Finding Your Dharma (2026.06.05)"
