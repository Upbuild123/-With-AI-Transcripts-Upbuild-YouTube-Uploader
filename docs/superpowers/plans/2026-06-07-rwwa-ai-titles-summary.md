# RWWA AI-Generated Titles & Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** For the RWWA program, extract audio from the uploaded video, transcribe it with OpenAI Whisper, and use Claude to generate 5 editable title suggestions and an editable session summary before uploading to YouTube.

**Architecture:** A pre-upload "Generate" step is added to the RWWA form only. Two new service modules handle transcription (`services/transcription.py`) and AI content generation (`services/ai_content.py`). The RWWA form renderer is updated to show the generate button and editable results. `pipeline.py` gains an optional `description` parameter so the AI summary can override the default program description.

**Tech Stack:** Python, Streamlit, ffmpeg (subprocess), OpenAI Python SDK (Whisper API), Anthropic Python SDK (Claude), pytest with unittest.mock

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `services/transcription.py` | Create | Audio extraction via ffmpeg + Whisper API transcription |
| `services/ai_content.py` | Create | Claude call to generate titles and summary from transcript |
| `ui/forms.py` | Modify | RWWA form: add generate button, editable title options, editable summary |
| `pipeline.py` | Modify | Accept optional `description` param, pass it to `upload_video` |
| `.env` / `.env.example` | Modify | Add `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` |
| `requirements.txt` | Modify | Add `openai` and `anthropic` packages |
| `tests/test_transcription.py` | Create | Unit tests for transcription service |
| `tests/test_ai_content.py` | Create | Unit tests for AI content service |

---

## Task 1: Add environment variables and dependencies

**Files:**
- Modify: `.env.example`
- Modify: `requirements.txt`

- [ ] **Step 1: Add API keys to `.env.example`**

Append to `.env.example`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Also add the same two keys to your local `.env` file with real values.

- [ ] **Step 2: Add packages to `requirements.txt`**

Append to `requirements.txt`:
```
openai>=1.0
anthropic>=0.25
```

- [ ] **Step 3: Install new dependencies**

```bash
pip install openai anthropic
```

Expected: both install without error.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .env.example
git commit -m "chore: add openai and anthropic dependencies"
```

---

## Task 2: Create `services/transcription.py`

**Files:**
- Create: `services/transcription.py`
- Create: `tests/test_transcription.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_transcription.py`:

```python
import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from services.transcription import extract_audio, transcribe


def test_extract_audio_calls_ffmpeg():
    with patch("services.transcription.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("services.transcription.tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/audio_abc.mp3"
            mock_tmp.return_value.__enter__ = lambda s: mock_file
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            result = extract_audio("/path/to/video.mp4")

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "ffmpeg" in args
    assert "-ac" in args
    assert "1" in args          # mono
    assert "-ar" in args
    assert "16000" in args      # 16kHz
    assert "-q:a" in args
    assert "5" in args


def test_extract_audio_raises_on_ffmpeg_failure():
    with patch("services.transcription.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr=b"error")
        with pytest.raises(RuntimeError, match="ffmpeg"):
            extract_audio("/path/to/video.mp4")


def test_transcribe_returns_text():
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = MagicMock(text="Hello world")

    with patch("services.transcription.openai.OpenAI", return_value=mock_client):
        with patch("builtins.open", MagicMock()):
            result = transcribe("/tmp/audio.mp3")

    assert result == "Hello world"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_transcription.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'services.transcription'`

- [ ] **Step 3: Implement `services/transcription.py`**

```python
import os
import subprocess
import tempfile

import openai


def extract_audio(video_path: str) -> str:
    """Extract mono mp3 audio from video file. Returns path to temp mp3 file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    audio_path = tmp.name

    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1",       # mono
            "-ar", "16000",   # 16kHz
            "-q:a", "5",      # lossy compression
            audio_path,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        os.unlink(audio_path)
        raise RuntimeError(
            f"ffmpeg failed. Make sure ffmpeg is installed (brew install ffmpeg).\n"
            f"Error: {result.stderr.decode(errors='replace')}"
        )

    return audio_path


def transcribe(audio_path: str) -> str:
    """Send audio file to OpenAI Whisper API. Returns transcript text."""
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return response.text
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_transcription.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add services/transcription.py tests/test_transcription.py
git commit -m "feat: add transcription service (ffmpeg + Whisper API)"
```

---

## Task 3: Create `services/ai_content.py`

**Files:**
- Create: `services/ai_content.py`
- Create: `tests/test_ai_content.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ai_content.py`:

```python
from unittest.mock import patch, MagicMock

from services.ai_content import generate_titles_and_summary


SAMPLE_TRANSCRIPT = "Today we discussed the nature of the self and how to quiet the mind."

SAMPLE_RESPONSE = """TITLES:
1. The Quiet Mind: Exploring the Inner Self
2. Who Are We Really? A Conversation on Consciousness
3. Stilling the Mind, Knowing the Self
4. Beyond the Ego: Remembering Who We Are
5. The Inner Life: Presence, Stillness, and Identity

SUMMARY:
In this session, we explored the nature of the self and the practice of quieting the mind. The conversation touched on how our busy lives often pull us away from a deeper awareness of who we are. Participants reflected on how stillness creates space to reconnect with something more essential. The group considered practical ways to bring this awareness into daily life."""


def test_generate_returns_five_titles():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client):
        result = generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    assert len(result["titles"]) == 5
    assert result["titles"][0] == "The Quiet Mind: Exploring the Inner Self"


def test_generate_returns_summary():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client):
        result = generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    assert "summary" in result
    assert len(result["summary"]) > 20


def test_generate_sends_transcript_in_prompt():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client):
        generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    call_kwargs = mock_client.messages.create.call_args[1]
    prompt_text = call_kwargs["messages"][0]["content"]
    assert SAMPLE_TRANSCRIPT in prompt_text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_ai_content.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'services.ai_content'`

- [ ] **Step 3: Implement `services/ai_content.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_ai_content.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add services/ai_content.py tests/test_ai_content.py
git commit -m "feat: add AI content service (Claude titles + summary)"
```

---

## Task 4: Update `pipeline.py` to accept optional description

**Files:**
- Modify: `pipeline.py`

- [ ] **Step 1: Add `description` parameter to `run_pipeline`**

In `pipeline.py`, update the function signature and the `upload_video` call:

```python
def run_pipeline(
    program_key: str,
    title: str,
    source_type: str,
    source,
    source_filename: str,
    session_date: date,
    recording_type: Optional[str] = None,
    description: Optional[str] = None,
    on_progress: Optional[Callable] = None,
) -> UploadResult:
```

Then find this line (around line 52):
```python
        youtube_url = upload_video(
            service=yt_service,
            file_path=tmp_path,
            title=title,
            description=program.description,
            playlist_id=program.playlist_id,
            on_progress=lambda pct: progress(f"Uploading to YouTube... {int(pct * 100)}%"),
        )
```

Change `description=program.description` to:
```python
            description=description if description is not None else program.description,
```

- [ ] **Step 2: Run existing tests to verify nothing is broken**

```bash
pytest tests/ -v
```

Expected: all existing tests PASS (the new parameter is optional so nothing breaks).

- [ ] **Step 3: Commit**

```bash
git add pipeline.py
git commit -m "feat: pipeline accepts optional description override"
```

---

## Task 5: Update `ui/forms.py` — RWWA AI generate flow

**Files:**
- Modify: `ui/forms.py`

This task replaces the existing `render_rwwa_form` function entirely. The new version adds session state for generated content, a Generate button, and editable title/summary fields.

- [ ] **Step 1: Replace `render_rwwa_form` in `ui/forms.py`**

Add this import at the top of the file (after existing imports):
```python
from datetime import date
```
(It may already be imported — check and skip if so.)

Replace the entire `render_rwwa_form` function (lines 90–114) with:

```python
def render_rwwa_form(session_date: date, video_source=None, video_source_type: str = "local") -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["rwwa"].playlist_id)

    # --- AI generation state keys ---
    GEN_TITLES_KEY = "rwwa_gen_titles"
    GEN_SUMMARY_KEY = "rwwa_gen_summary"
    SELECTED_TITLE_KEY = "rwwa_selected_title_idx"

    if GEN_TITLES_KEY not in st.session_state:
        st.session_state[GEN_TITLES_KEY] = []
    if GEN_SUMMARY_KEY not in st.session_state:
        st.session_state[GEN_SUMMARY_KEY] = ""
    if SELECTED_TITLE_KEY not in st.session_state:
        st.session_state[SELECTED_TITLE_KEY] = 0

    has_video = video_source is not None

    # --- Generate button ---
    if has_video:
        if st.button("Generate Titles & Summary", key="rwwa_generate"):
            import tempfile, os
            from services.transcription import extract_audio, transcribe
            from services.ai_content import generate_titles_and_summary

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

                with st.spinner("Generating titles and summary..."):
                    result = generate_titles_and_summary(transcript)
                    st.session_state[GEN_TITLES_KEY] = result["titles"]
                    st.session_state[GEN_SUMMARY_KEY] = result["summary"]
                    st.session_state[SELECTED_TITLE_KEY] = 0

            except Exception as e:
                st.error(f"Generation failed: {e}")
            finally:
                if tmp_video_path and os.path.exists(tmp_video_path):
                    os.unlink(tmp_video_path)
                if audio_path and os.path.exists(audio_path):
                    os.unlink(audio_path)

    # --- Title selection and editing ---
    titles = st.session_state[GEN_TITLES_KEY]
    final_title = ""

    if titles:
        st.markdown("**Suggested titles** — select one to use, or edit any field:")
        edited_titles = []
        for i, t in enumerate(titles):
            col1, col2 = st.columns([1, 8])
            with col1:
                selected = st.radio("", [i], index=0 if st.session_state[SELECTED_TITLE_KEY] == i else -1,
                                    key=f"rwwa_radio_{i}", label_visibility="collapsed")
                if selected == i:
                    st.session_state[SELECTED_TITLE_KEY] = i
            with col2:
                edited = st.text_input(f"Title option {i+1}", value=t, key=f"rwwa_title_{i}",
                                       label_visibility="collapsed")
                edited_titles.append(edited)

        idx = st.session_state[SELECTED_TITLE_KEY]
        final_title = edited_titles[idx] if edited_titles else ""
        st.text_input("Or type a custom title", key="rwwa_custom_title",
                      placeholder="Leave blank to use selection above")
        custom = st.session_state.get("rwwa_custom_title", "")
        if custom.strip():
            final_title = custom.strip()
    else:
        final_title = st.text_input("YouTube title (edit if needed)", value="")

    if not final_title:
        return {}

    # --- Summary ---
    summary = st.session_state[GEN_SUMMARY_KEY]
    final_summary = st.text_area("Session summary (used as YouTube description)",
                                 value=summary, height=150, key="rwwa_summary")

    if final_title:
        st.markdown(f"**Preview title:** `{final_title}`")

    return {
        "title": final_title,
        "description": final_summary if final_summary.strip() else None,
    }
```

- [ ] **Step 2: Update `app.py` to pass video source into the RWWA form**

The RWWA form now needs access to the video source to enable the Generate button. In `app.py`, the form is called as:

```python
form_values = FORM_RENDERERS[program.key](session_date)
```

Change this block so that RWWA gets the video source:

```python
if program.key == "rwwa":
    src = uploaded_file.read() if uploaded_file is not None else drive_link
    src_type = "local" if uploaded_file is not None else "drive"
    form_values = FORM_RENDERERS[program.key](session_date, video_source=src, video_source_type=src_type)
else:
    form_values = FORM_RENDERERS[program.key](session_date)
```

Also update the `run_pipeline` call in `app.py` to pass `description`:

```python
        result = run_pipeline(
            program_key=program.key,
            title=title,
            source_type=src_type,
            source=source,
            source_filename=source_filename,
            session_date=session_date,
            recording_type=form_values.get("recording_type"),
            description=form_values.get("description"),
            on_progress=on_progress,
        )
```

Note: the existing `src_type` variable in `app.py` is set inside the `if st.button(...)` block. For RWWA, `src` and `src_type` are needed before the button too. Restructure `app.py` so `src` and `src_type` are set after `source_type` is chosen:

```python
source_type = st.radio("Video source", ["Upload local file", "Google Drive link"])

uploaded_file = None
drive_link = None

if source_type == "Upload local file":
    uploaded_file = st.file_uploader("Choose mp4 file", type=["mp4"])
else:
    drive_link = st.text_input("Google Drive link")

# Derive source for use in RWWA form (before upload button)
_src_type = "local" if source_type == "Upload local file" else "drive"
_src = None
if _src_type == "local" and uploaded_file is not None:
    _src = uploaded_file.read()
    # Reset file position for later read
    uploaded_file.seek(0)
elif _src_type == "drive" and drive_link:
    _src = drive_link

st.divider()

if program.key == "rwwa":
    form_values = FORM_RENDERERS[program.key](session_date, video_source=_src, video_source_type=_src_type)
else:
    form_values = FORM_RENDERERS[program.key](session_date)
```

Then inside the upload button handler, keep existing logic but pass `description`:

```python
        result = run_pipeline(
            program_key=program.key,
            title=title,
            source_type=src_type,
            source=source,
            source_filename=source_filename,
            session_date=session_date,
            recording_type=form_values.get("recording_type"),
            description=form_values.get("description"),
            on_progress=on_progress,
        )
```

- [ ] **Step 3: Run all existing tests**

```bash
pytest tests/ -v
```

Expected: all tests PASS (form changes are UI-only; existing program logic is untouched).

- [ ] **Step 4: Commit**

```bash
git add ui/forms.py app.py
git commit -m "feat: RWWA form with AI title/summary generation"
```

---

## Task 6: Manual smoke test

- [ ] **Step 1: Start the app**

```bash
streamlit run app.py
```

- [ ] **Step 2: Test the generate flow**
  - Select "Remembering Who We Are"
  - Upload a short `.mp4` test clip (even 30 seconds is fine)
  - Click "Generate Titles & Summary"
  - Verify spinner shows "Extracting audio..." → "Transcribing audio..." → "Generating titles and summary..."
  - Verify 5 title options appear with radio buttons and editable text inputs
  - Verify editable summary text area appears
  - Verify selecting a radio and editing a title updates the preview
  - Verify typing in the custom title field overrides the selection

- [ ] **Step 3: Test error cases**
  - Try clicking Generate without a video selected — button should not be visible
  - With OPENAI_API_KEY unset, verify a clear error message appears

- [ ] **Step 4: Verify other programs are unaffected**
  - Switch to "Call to Awaken" — confirm normal form renders, no generate button

- [ ] **Step 5: Final commit if any fixes were needed**

```bash
git add -p
git commit -m "fix: smoke test corrections"
```

---

## Task 7: Run full test suite

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Final commit**

```bash
git add .
git commit -m "chore: all tests passing for RWWA AI titles/summary feature"
```
