# Morning Rounds AI-Generated Topic Suggestions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add AI-generated topic suggestions (5 options) for Morning Rounds, reusing the RWWA transcription pipeline, with one suggestion optionally continuing the previous session's "Part N" series based on Claude's judgment of the transcript.

**Architecture:** Reuse `services/transcription.py` unchanged. Add `generate_topic_suggestions(transcript, previous_topic=None)` to `services/ai_content.py`, following the same numbered-list parsing pattern as `generate_titles_and_summary`. Update `render_morning_rounds_form` in `ui/forms.py` to accept `video_source`/`video_source_type`, add a "Generate Topic Suggestions" button, extract the full previous topic (including any "Part N" suffix) via a new regex, and render 5 editable topic options wrapped in the existing structured title format. Extend `app.py` to pass video source info to Morning Rounds.

**Tech Stack:** Python, Streamlit, Anthropic Claude API (`claude-opus-4-8`), pytest.

---

## Background: previous_topic regex

Existing `prev_topic` regex (used to prefill the topic input, unchanged):
```python
re.match(r"^Morning Rounds - \d+ - (.+?) - Part \d+", mr_titles[0])
```
For a title like `"Morning Rounds - 42 - Prema Vivarta - Part 9 - Jun 9, 2026"`, this captures `"Prema Vivarta"` (non-greedy, stops before " - Part N").

For `generate_topic_suggestions`, Claude needs the FULL previous topic **including** "Part N" (e.g., `"Prema Vivarta - Part 9"`) so it can judge continuation and suggest "Part 10". This requires a **separate** regex that captures everything between the session number and the trailing date:

```python
re.match(r"^Morning Rounds - \d+ - (.+) - \w+ \d{1,2}, \d{4}$", mr_titles[0])
```

For `"Morning Rounds - 42 - Prema Vivarta - Part 9 - Jun 9, 2026"`, this captures `"Prema Vivarta - Part 9"` (greedy `.+` consumes up to the last `" - <Month> <Day>, <Year>"`).

This new regex is used ONLY to build `previous_topic_full` passed to `generate_topic_suggestions`. The existing `prev_topic` regex remains unchanged and continues to prefill the topic input field.

---

## Task 1: Add `generate_topic_suggestions` to `services/ai_content.py`

**Files:**
- Modify: `services/ai_content.py`
- Test: `tests/test_ai_content.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_ai_content.py`:

```python
from services.ai_content import generate_topic_suggestions


def test_generate_topic_suggestions_with_previous_topic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    captured_prompt = {}

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. Prema Vivarta - Part 10\n"
            "2. The Nature of Surrender\n"
            "3. Cultivating Humility\n"
            "4. Service Without Attachment\n"
            "5. Faith in Difficult Times\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            captured_prompt["text"] = kwargs["messages"][0]["content"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    topics = generate_topic_suggestions("some transcript text", previous_topic="Prema Vivarta - Part 9")

    assert len(topics) == 5
    assert topics[0] == "Prema Vivarta - Part 10"
    assert "Prema Vivarta - Part 9" in captured_prompt["text"]
    assert "continu" in captured_prompt["text"].lower()


def test_generate_topic_suggestions_without_previous_topic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    captured_prompt = {}

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. The Nature of Surrender\n"
            "2. Cultivating Humility\n"
            "3. Service Without Attachment\n"
            "4. Faith in Difficult Times\n"
            "5. The Power of Association\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            captured_prompt["text"] = kwargs["messages"][0]["content"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    topics = generate_topic_suggestions("some transcript text")

    assert len(topics) == 5
    assert "Part" not in captured_prompt["text"].split("Transcript:")[0] or "previous" not in captured_prompt["text"].lower()
    assert "continu" not in captured_prompt["text"].lower()


def test_generate_topic_suggestions_raises_on_too_few(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. The Nature of Surrender\n"
            "2. Cultivating Humility\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    import pytest
    with pytest.raises(ValueError):
        generate_topic_suggestions("some transcript text")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ai_content.py -v -k topic_suggestions`
Expected: FAIL with `ImportError: cannot import name 'generate_topic_suggestions'`

- [ ] **Step 3: Implement `generate_topic_suggestions` and `_parse_topic_list`**

In `services/ai_content.py`, add after the existing `_PROMPT_TEMPLATE` (keep existing imports/template/functions unchanged):

```python
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
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text
    return _parse_topic_list(raw)


def _parse_topic_list(raw: str) -> List[str]:
    topics: List[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.", stripped):
            topic = re.sub(r"^\d+\.\s*", "", stripped)
            if topic:
                topics.append(topic)

    if len(topics) < 5:
        raise ValueError(
            f"Expected 5 topic suggestions from Claude, got {len(topics)}. "
            "The response may be malformed."
        )

    return topics[:5]
```

Update the `typing` import at the top of the file to include `Optional`:

```python
from typing import Dict, List, Optional
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ai_content.py -v`
Expected: PASS (all tests, including the existing RWWA ones)

- [ ] **Step 5: Commit**

```bash
git add services/ai_content.py tests/test_ai_content.py
git commit -m "feat: add AI topic suggestions for Morning Rounds"
```

---

## Task 2: Update `render_morning_rounds_form` in `ui/forms.py`

**Files:**
- Modify: `ui/forms.py:240-261`
- Test: `tests/test_forms.py` (or wherever existing forms tests live — check for an existing Morning Rounds test file/function first)

- [ ] **Step 1: Check for existing Morning Rounds form tests**

Run: `grep -rn "render_morning_rounds_form" tests/`

If a test exists that calls `render_morning_rounds_form(session_date)` with the old signature, note it — Step 3 keeps `video_source`/`video_source_type` as optional kwargs with defaults (`None` / `"local"`), so the old call signature continues to work and that test should still pass unchanged.

- [ ] **Step 2: Write a failing test for the new full-topic regex**

The full-topic extraction regex is the riskiest new piece of logic (it's easy to get the date pattern wrong). Add a focused unit test for it directly, in `tests/test_forms.py`:

```python
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
```

- [ ] **Step 3: Run test to verify it passes (regex sanity check)**

Run: `pytest tests/test_forms.py -v -k previous_topic_full`
Expected: PASS (this validates the regex before wiring it into the form)

- [ ] **Step 4: Replace `render_morning_rounds_form`**

Replace the function at `ui/forms.py:240-261` (currently):

```python
def render_morning_rounds_form(session_date: date) -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["morning_rounds"].playlist_id)
    mr_titles = []
    with st.spinner("Fetching session number from YouTube..."):
        try:
            mr_titles = _cached_playlist_titles(PROGRAM_BY_KEY["morning_rounds"].playlist_id)
            session_num = next_morning_rounds_session(mr_titles)
        except Exception:
            session_num = 1

    prev_topic = ""
    if mr_titles:
        m = re.match(r"^Morning Rounds - \d+ - (.+?) - Part \d+", mr_titles[0])
        if m:
            prev_topic = m.group(1)

    session_num = st.number_input("Session number", min_value=1, value=session_num, step=1)
    topic = st.text_input("Topic", value=prev_topic)
    if not topic:
        return {}
    title = _editable_title(build_morning_rounds_title(int(session_num), topic, session_date))
    return {"title": title, "session_num": int(session_num), "topic": topic}
```

with:

```python
def render_morning_rounds_form(session_date: date, video_source=None, video_source_type: str = "local") -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["morning_rounds"].playlist_id)
    mr_titles = []
    with st.spinner("Fetching session number from YouTube..."):
        try:
            mr_titles = _cached_playlist_titles(PROGRAM_BY_KEY["morning_rounds"].playlist_id)
            session_num = next_morning_rounds_session(mr_titles)
        except Exception:
            session_num = 1

    prev_topic = ""
    previous_topic_full = None
    if mr_titles:
        m = re.match(r"^Morning Rounds - \d+ - (.+?) - Part \d+", mr_titles[0])
        if m:
            prev_topic = m.group(1)
        m_full = re.match(r"^Morning Rounds - \d+ - (.+) - \w+ \d{1,2}, \d{4}$", mr_titles[0])
        if m_full:
            previous_topic_full = m_full.group(1)

    session_num = st.number_input("Session number", min_value=1, value=session_num, step=1)

    # --- AI generation state keys ---
    GEN_TOPICS_KEY = "mr_gen_topics"
    SELECTED_TOPIC_KEY = "mr_selected_topic_idx"

    if GEN_TOPICS_KEY not in st.session_state:
        st.session_state[GEN_TOPICS_KEY] = []
    if SELECTED_TOPIC_KEY not in st.session_state:
        st.session_state[SELECTED_TOPIC_KEY] = 0

    has_video = video_source is not None

    # --- Generate button ---
    if has_video:
        if st.button("Generate Topic Suggestions", key="mr_generate"):
            from services.transcription import extract_audio, transcribe
            from services.ai_content import generate_topic_suggestions

            tmp_video_path = None
            audio_path = None
            try:
                with st.spinner("Extracting audio..."):
                    if video_source_type == "local":
                        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                        tmp.write(video_source)
                        tmp.close()
                        tmp_video_path = tmp.name
                    else:
                        from services.drive import drive_link_to_file_id, download_drive_file
                        file_id = drive_link_to_file_id(video_source)
                        tmp_video_path = download_drive_file(file_id)
                    audio_path = extract_audio(tmp_video_path)

                with st.spinner("Transcribing audio (this may take a minute)..."):
                    transcript = transcribe(audio_path)

                with st.spinner("Generating topic suggestions..."):
                    topics = generate_topic_suggestions(transcript, previous_topic=previous_topic_full)
                    st.session_state[GEN_TOPICS_KEY] = topics
                    st.session_state[SELECTED_TOPIC_KEY] = 0
                    st.session_state["mr_topic_radio"] = 0
                    # Reset editable inputs so new generated topics appear in the fields
                    for i, t in enumerate(topics):
                        st.session_state[f"mr_topic_{i}"] = t
                    st.session_state["mr_custom_topic"] = ""

            except Exception as e:
                st.error(f"Generation failed: {e}")
            finally:
                if tmp_video_path and os.path.exists(tmp_video_path):
                    os.unlink(tmp_video_path)
                if audio_path and os.path.exists(audio_path):
                    os.unlink(audio_path)

    # --- Topic selection and editing ---
    topics = st.session_state[GEN_TOPICS_KEY]
    final_topic = ""

    if topics:
        st.markdown("**Suggested topics** — select one, or edit any field below:")

        selected_idx = st.radio(
            "Select a topic",
            options=list(range(len(topics))),
            format_func=lambda i: build_morning_rounds_title(int(session_num), topics[i], session_date),
            index=st.session_state[SELECTED_TOPIC_KEY],
            key="mr_topic_radio",
            label_visibility="collapsed",
        )
        st.session_state[SELECTED_TOPIC_KEY] = selected_idx

        edited_topics = []
        for i, t in enumerate(topics):
            edited = st.text_input(
                f"Edit option {i + 1}",
                value=t,
                key=f"mr_topic_{i}",
                label_visibility="visible",
            )
            edited_topics.append(edited)

        final_topic = edited_topics[selected_idx] if edited_topics else ""

        custom = st.text_input(
            "Or type a custom topic",
            key="mr_custom_topic",
            placeholder="Leave blank to use the selected option above",
        )
        if custom.strip():
            final_topic = custom.strip()
    else:
        final_topic = st.text_input("Topic", value=prev_topic)

    if not final_topic:
        return {}
    title = _editable_title(build_morning_rounds_title(int(session_num), final_topic, session_date))
    return {"title": title, "session_num": int(session_num), "topic": final_topic}
```

- [ ] **Step 5: Run full test suite**

Run: `pytest -v`
Expected: PASS (all tests, including any pre-existing Morning Rounds form test, since the new params have defaults)

- [ ] **Step 6: Commit**

```bash
git add ui/forms.py tests/test_forms.py
git commit -m "feat: add AI topic generation UI to Morning Rounds form"
```

---

## Task 3: Wire video source into Morning Rounds in `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Locate the form-rendering branch**

Run: `grep -n 'program.key == "rwwa"' app.py`

- [ ] **Step 2: Update the condition**

Change:

```python
if program.key == "rwwa":
    form_values = FORM_RENDERERS[program.key](session_date, video_source=_src, video_source_type=_src_type)
else:
    form_values = FORM_RENDERERS[program.key](session_date)
```

to:

```python
if program.key in ("rwwa", "morning_rounds"):
    form_values = FORM_RENDERERS[program.key](session_date, video_source=_src, video_source_type=_src_type)
else:
    form_values = FORM_RENDERERS[program.key](session_date)
```

- [ ] **Step 3: Run full test suite**

Run: `pytest -v`
Expected: PASS (all tests)

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: pass video source to Morning Rounds form for AI topic generation"
```

---

## Task 4: Manual smoke test

- [ ] **Step 1: Start the Streamlit app**

Run: `streamlit run app.py --server.headless true --server.port 8502`

- [ ] **Step 2: Verify Morning Rounds renders correctly**

Using Playwright (or browser), navigate to the app, select "Morning Rounds", select a session date, and select a video source. Verify:
- "Generate Topic Suggestions" button appears
- Session number input still works independently
- Other programs (e.g., Call to Awaken, RWWA) still render correctly with no regressions

- [ ] **Step 3: Stop the app**

Kill the Streamlit process started in Step 1.
