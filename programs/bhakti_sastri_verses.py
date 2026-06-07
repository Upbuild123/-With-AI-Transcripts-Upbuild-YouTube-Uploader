from typing import List, Optional

# Ordered verse sets for chapters 8–18
VERSE_SETS: List[str] = [
    # Chapter 8
    "BG 8.1-7",
    "BG 8.8-16",
    "BG 8.17-28",
    # Chapter 9
    "BG 9.1-3",
    "BG 9.4-10",
    "BG 9.11-15",
    "BG 9.16-22",
    "BG 9.23-34",
    # Chapter 10
    "BG 10.1-7",
    "BG 10.8-18",
    "BG 10.19-42",
    # Chapter 11
    "BG 11.9-31",
    "BG 11.32-46",
    # Chapter 12
    "BG 12.1-7",
    "BG 12.8-12",
    "BG 12.13-20",
    # Chapter 13
    "BG 13.1-5",
    "BG 13.5-7",
    "BG 13.8-12",
    "BG 13.13-19",
    "BG 13.20-26",
    "BG 13.27-35",
    # Chapter 14
    "BG 14.1-9",
    "BG 14.10-18",
    "BG 14.19-25",
    "BG 14.26-27",
    # Chapter 15
    "BG 15.1-6",
    "BG 15.7-15",
    "BG 15.16-20",
    # Chapter 16
    "BG 16.1-9",
    "BG 16.10-17",
    "BG 16.19-24",
    # Chapter 17
    "BG 17.1-6",
    "BG 17.7-22",
    "BG 17.23-28",
    # Chapter 18
    "BG 18.1-12",
    "BG 18.13-35",
    "BG 18.36-48",
    "BG 18.49-62",
    "BG 18.63-77",
]


def next_bhakti_sastri_verses(titles: List[str]) -> Optional[str]:
    """Return the next verse set based on the most recently uploaded title."""
    for title in titles:
        for i, verse_set in enumerate(VERSE_SETS):
            if verse_set in title:
                next_i = i + 1
                return VERSE_SETS[next_i] if next_i < len(VERSE_SETS) else None
    return VERSE_SETS[0] if VERSE_SETS else None
