import re
from typing import List


def next_committed_bhakti_session(titles: List[str]) -> int:
    pattern = re.compile(r"^Session (\d+) - Committed Bhakti")
    nums = [int(m.group(1)) for t in titles if (m := pattern.match(t))]
    return max(nums) + 1 if nums else 1


def next_morning_rounds_session(titles: List[str]) -> int:
    pattern = re.compile(r"^Morning Rounds - (\d+) - ")
    nums = [int(m.group(1)) for t in titles if (m := pattern.match(t))]
    return max(nums) + 1 if nums else 1


def next_library_live_episode(titles: List[str]) -> int:
    pattern = re.compile(r"^(\d+) - ")
    nums = [int(m.group(1)) for t in titles if (m := pattern.match(t))]
    return max(nums) + 1 if nums else 1


def next_rwwa_part(titles: List[str], topic_title: str) -> int:
    pattern = re.compile(r"^RWWA - " + re.escape(topic_title) + r" - Part (\d+)")
    parts = [int(m.group(1)) for t in titles if (m := pattern.match(t))]
    return max(parts) + 1 if parts else 1
