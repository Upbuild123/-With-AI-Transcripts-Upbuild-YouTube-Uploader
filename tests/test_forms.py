import re


def test_morning_rounds_previous_topic_full_regex_extracts_part_number():
    title = "Morning Rounds - 42 - Prema Vivarta - Part 9 - Jun 9, 2026"
    m = re.match(r"^Morning Rounds - \d+ - (.+) - \w+ \d{1,2}, \d{4}$", title)
    assert m is not None
    assert m.group(1) == "Prema Vivarta - Part 9"


def test_morning_rounds_previous_topic_full_regex_no_match_returns_none():
    title = "Some Unrelated Title"
    m = re.match(r"^Morning Rounds - \d+ - (.+) - \w+ \d{1,2}, \d{4}$", title)
    assert m is None
