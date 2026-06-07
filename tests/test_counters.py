from programs.counters import (
    next_committed_bhakti_session,
    next_morning_rounds_session,
    next_library_live_episode,
    next_rwwa_part,
)

COMMITTED_TITLES = [
    "Session 1 - Committed Bhakti (2026.01.09) Introduction",
    "Session 2 - Committed Bhakti (2026.01.16) Sadhana Basics",
    "Session 13 - Committed Bhakti (2026.06.05) Identity and Purpose",
]

MORNING_TITLES = [
    "Morning Rounds - 1 - Japa Basics - Jan 6, 2026",
    "Morning Rounds - 41 - Focus and Attention - Jun 2, 2026",
]

LIBRARY_TITLES = [
    "1 - Finding Your Dharma (2026.01.15)",
    "6 - The Nature of Consciousness (2026.05.28)",
]

RWWA_TITLES = [
    "RWWA - The Art of Listening - Part 1 - Jan 7, 2026",
    "RWWA - Servant Leadership - Part 1 - Feb 4, 2026",
    "RWWA - The Art of Listening - Part 2 - Jan 14, 2026",
]

def test_next_committed_bhakti():
    assert next_committed_bhakti_session(COMMITTED_TITLES) == 14

def test_next_morning_rounds():
    assert next_morning_rounds_session(MORNING_TITLES) == 42

def test_next_library_live():
    assert next_library_live_episode(LIBRARY_TITLES) == 7

def test_next_rwwa_part_existing_title():
    assert next_rwwa_part(RWWA_TITLES, "The Art of Listening") == 3

def test_next_rwwa_part_new_title():
    assert next_rwwa_part(RWWA_TITLES, "Brand New Topic") == 1

def test_next_rwwa_part_case_sensitive():
    assert next_rwwa_part(RWWA_TITLES, "the art of listening") == 1
