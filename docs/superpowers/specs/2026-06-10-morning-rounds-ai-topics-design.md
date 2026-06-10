# Morning Rounds AI-Generated Topic Suggestions

**Date:** 2026-06-10
**Scope:** Morning Rounds program only
**Status:** Approved

---

## Overview

Before uploading a Morning Rounds session to YouTube, the app extracts audio from the video, transcribes it using OpenAI Whisper, and sends the transcript (plus the previous session's topic, if available) to Claude to generate 5 topic suggestions. One suggestion may be a continuation of the previous topic's series (e.g., "Prema Vivarta Part 10") if Claude judges the session continues that series; otherwise all suggestions are independent. Suggestions are wrapped into the existing structured title format and presented for the user to review/edit before upload.

This reuses the audio extraction and transcription infrastructure built for RWWA (`services/transcription.py`), and follows the same UI pattern (Generate button, editable radio options).

---

## User Flow

1. User selects Morning Rounds, session date, and video source (local file or Drive link)
2. App fetches recent YouTube playlist titles to compute `session_num` (existing behavior) and extract `previous_topic` via regex on the most recent title (existing regex, already present)
3. A **"Generate Topic Suggestions"** button appears (Morning Rounds only, visible once a video is selected)
4. User clicks the button — app shows progress while:
   - Extracting audio via ffmpeg (reuses `services/transcription.extract_audio`)
   - Transcribing via Whisper (reuses `services/transcription.transcribe`)
   - Sending transcript + `previous_topic` to Claude via new `generate_topic_suggestions(transcript, previous_topic)`
5. Results render inline:
   - 5 editable topic options (radio to select, text input to edit each), each previewed wrapped in `Morning Rounds - {session_num} - {topic} - {date}`
   - A free-text field to enter a custom topic
   - `session_num` input remains independently editable (unchanged from current behavior)
6. User reviews/edits, then clicks "Upload to YouTube" (unchanged pipeline — no description override for Morning Rounds)

---

## Architecture & Components

### Modified files

**`services/ai_content.py`**
- Add `generate_topic_suggestions(transcript: str, previous_topic: Optional[str] = None) -> List[str]`
- New prompt template:
  - Explains Morning Rounds format and that output should be short topic phrases (not full titles)
  - Includes the transcript
  - If `previous_topic` is provided, includes it and instructs Claude to:
    - Determine if this session continues the same series as `previous_topic`
    - If yes, include one suggestion that continues the series (e.g., increment "Part N" to "Part N+1")
    - If the transcript indicates a new series/topic is starting, do not force a continuation — all 5 suggestions reflect Claude's independent judgment
  - Asks for exactly 5 numbered topic suggestions, one per line
- Reuses the same parsing approach as `_parse_response` (numbered line extraction) via a shared helper or a second parser function `_parse_topic_list`
- Enforces the "exactly 5" contract: raises `ValueError` if fewer than 5 are parsed (same pattern as `generate_titles_and_summary`)

**`ui/forms.py`**
- `render_morning_rounds_form` updated:
  - Accept `video_source=None, video_source_type: str = "local"` params (same signature addition as RWWA)
  - Extract `previous_topic` from `mr_titles[0]` using the existing regex (`^Morning Rounds - \d+ - (.+?) - Part \d+`); if no match or no titles, `previous_topic = None`
  - Add "Generate Topic Suggestions" button, visible only when `video_source is not None`
  - On click: extract audio → transcribe → `generate_topic_suggestions(transcript, previous_topic)` → store 5 topics in session state (reset session state for topic input fields on each generate, same fix pattern as RWWA)
  - Render 5 radio+edit topic fields (single `st.radio` + per-option `st.text_input`, same pattern as RWWA) plus a custom topic text input
  - Each option's preview shows the full wrapped title via `build_morning_rounds_title(session_num, topic, session_date)`
  - `session_num` number input remains, independent of generation
  - Return `{"title": <wrapped title>, "session_num": int(session_num), "topic": <selected/edited topic>}` (same shape as before — no `description` key, since Morning Rounds doesn't use it)

**`app.py`**
- Extend the existing `if program.key == "rwwa":` branch to `if program.key in ("rwwa", "morning_rounds"):` so Morning Rounds also receives `video_source` and `video_source_type`

### Unchanged

- `pipeline.py` — no changes; Morning Rounds doesn't pass a `description` override
- `services/transcription.py` — reused as-is

---

## Error Handling

| Scenario | Behavior |
|---|---|
| No previous title / regex doesn't match | `previous_topic = None`; prompt omits continuation instruction |
| ffmpeg/Whisper/Claude failures | `st.error()` shown; button remains clickable for retry; manual topic entry still possible |
| Fewer than 5 topics parsed from Claude | `ValueError` raised (same contract as RWWA) |
| User clicks Generate twice | Topic input session-state fields reset to new suggestions (same fix as RWWA) |
| `session_num` | Always independently editable, unaffected by AI generation |

---

## Constraints & Scope

- Morning-Rounds-only; gated by `program.key == "morning_rounds"`. RWWA and other programs unaffected.
- No description/summary generation for Morning Rounds (out of scope).
- Reuses existing transcription service without modification.

---

## Testing

- Unit tests in `tests/test_ai_content.py` for `generate_topic_suggestions`:
  - With `previous_topic` provided: verify it appears in the prompt sent to Claude
  - Without `previous_topic`: verify prompt omits continuation instructions
  - Verify exactly 5 topics returned in both cases
  - Verify `ValueError` raised if fewer than 5 topics parsed
- Existing Morning Rounds and RWWA tests remain unaffected (run full suite)
