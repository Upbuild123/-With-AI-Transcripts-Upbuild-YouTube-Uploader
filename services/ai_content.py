import os
import re
from typing import Dict, List, Optional

import anthropic


_PROMPT_TEMPLATE = """\
Below is a transcript from a session of "Remembering Who We Are" (RWWA), a weekly community \
gathering at Upbuild focused on spiritual reflection and reconnecting with a deeper sense of self.

Note: the first several minutes of most sessions are a standard introduction where a \
facilitator reminds everyone of the program's purpose (helping people move from the ego to \
the true self and cultivate a spiritual orientation to the world) and the three pillars of \
the culture asked of all participants (full-hearted participation, respect, and \
determination). This introduction is the same general content every week (even if the exact \
wording varies) and is NOT specific to this session. Do not let this recurring introduction \
influence the title suggestions, and do not include it in the summary — focus only on the \
specific topics, themes, and content discussed in the rest of the session.

Transcript:
{transcript}

Please provide:

TITLES:
Generate 5 distinct YouTube title suggestions for this session. Each title should be \
thoughtful, evocative, and reflect the main themes discussed. Number them 1-5, one per line, \
with no extra punctuation before the title text.

SUMMARY:
Write a 3-6 sentence summary of this session suitable for use as a YouTube video description. \
The summary should capture the key themes and invite viewers to watch.\
"""


_TOPIC_PROMPT_TEMPLATE = """\
Below is a transcript from a session of "Morning Rounds", a recurring talk series at Upbuild. \
Morning Rounds sessions are often organized into multi-part series on a single topic (e.g., \
"Prema Vivarta - Part 9"), but a session may also begin a new series.

Transcript:
{transcript}
{previous_topic_section}
Please suggest 5 short topic phrases (not full titles) that capture the main subject(s) \
discussed in this session. These will be inserted into a structured title in the form \
"Morning Rounds - {{session_num}} - {{topic}} - {{date}}", so keep each suggestion concise \
(a few words, optionally including a "Part N" suffix for a series).

Number them 1-5, one per line, with no extra punctuation before the topic text.\
"""

_TOPIC_PROMPT_PREVIOUS_TOPIC_SECTION = """
The previous session's topic was: "{previous_topic}"

Based on the transcript, determine whether this session continues the same series as the \
previous topic. If it clearly continues that series, include one of the 5 suggestions that \
continues the series by incrementing its "Part N" number (e.g., if the previous topic was \
"Prema Vivarta - Part 9", suggest "Prema Vivarta - Part 10"). If the transcript indicates a \
new series or topic is starting, do not force a continuation suggestion — base all 5 \
suggestions on your independent judgment of this session's content.
"""


def generate_topic_suggestions(transcript: str, previous_topic: Optional[str] = None) -> List[str]:
    """Call Claude with transcript (and optional previous topic). Returns list of 5 topic strings."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    if previous_topic:
        previous_topic_section = _TOPIC_PROMPT_PREVIOUS_TOPIC_SECTION.format(previous_topic=previous_topic)
    else:
        previous_topic_section = ""

    prompt = _TOPIC_PROMPT_TEMPLATE.format(transcript=transcript, previous_topic_section=previous_topic_section)

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(block.text for block in response.content if hasattr(block, "text"))
    return _parse_topic_list(raw)


def _parse_topic_list(raw: str) -> List[str]:
    topics: List[str] = []
    for line in raw.splitlines():
        stripped = line.strip().strip("*").strip()
        if re.match(r"^\d+[\.\):]?\s+", stripped):
            topic = re.sub(r"^\d+[\.\):]?\s+", "", stripped).strip("*").strip()
            if topic:
                topics.append(topic)

    if len(topics) < 5:
        raise ValueError(
            f"Expected 5 topic suggestions from Claude, got {len(topics)}. "
            f"Raw response was: {raw!r}"
        )

    return topics[:5]


def generate_titles_and_summary(transcript: str) -> Dict[str, object]:
    """Call Claude with transcript. Returns dict with 'titles' (list of 5 str) and 'summary' (str)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": _PROMPT_TEMPLATE.format(transcript=transcript)}
        ],
    )
    raw = response.content[0].text
    return _parse_response(raw)


def _parse_response(raw: str) -> Dict[str, object]:
    titles: List[str] = []
    summary_lines: List[str] = []
    in_titles = False
    in_summary = False

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("TITLES"):
            in_titles = True
            in_summary = False
            continue
        if stripped.upper().startswith("SUMMARY"):
            in_summary = True
            in_titles = False
            continue
        if in_titles and stripped:
            # Only collect numbered title lines (e.g. "1. Some Title")
            if re.match(r"^\d+\.", stripped):
                title = re.sub(r"^\d+\.\s*", "", stripped)
                if title:
                    titles.append(title)
        elif in_summary and stripped:
            summary_lines.append(stripped)

    if len(titles) < 5:
        raise ValueError(
            f"Expected 5 title suggestions from Claude, got {len(titles)}. "
            "The response may be malformed."
        )

    return {
        "titles": titles[:5],
        "summary": " ".join(summary_lines),
    }
