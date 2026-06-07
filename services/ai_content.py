import os
import re
from typing import Dict, List

import anthropic


_PROMPT_TEMPLATE = """\
Below is a transcript from a session of "Remembering Who We Are" (RWWA), a weekly community \
gathering at Upbuild focused on spiritual reflection and reconnecting with a deeper sense of self.

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


def generate_titles_and_summary(transcript: str) -> Dict[str, object]:
    """Call Claude with transcript. Returns dict with 'titles' (list of 5 str) and 'summary' (str)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
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
            # Strip leading "1. " numbering
            title = re.sub(r"^\d+\.\s*", "", stripped)
            if title:
                titles.append(title)
        elif in_summary and stripped:
            summary_lines.append(stripped)

    return {
        "titles": titles[:5],
        "summary": " ".join(summary_lines),
    }
