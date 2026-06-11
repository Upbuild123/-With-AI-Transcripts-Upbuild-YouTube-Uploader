# RWWA AI-Generated Titles & Summary

**Date:** 2026-06-07  
**Scope:** RWWA program only (Remembering Who We Are)  
**Status:** Approved

---

## Overview

Before uploading a RWWA session to YouTube, the app extracts audio from the video, transcribes it using OpenAI Whisper, and sends the transcript to Claude to generate 5 suggested titles and a 3–6 sentence session summary. The user reviews and edits these in the UI before uploading.

---

## User Flow

1. User selects the RWWA program, session date, and video source (local file or Drive link)
2. A **"Generate Titles & Summary"** button appears (RWWA only)
3. User clicks the button — app shows a progress indicator while:
   - Extracting audio from the `.mp4` via ffmpeg (mono mp3, 16kHz, `-q:a 5`)
   - Sending audio to OpenAI Whisper API → returns transcript
   - Sending transcript to Claude → returns 5 title suggestions + 3–6 sentence summary
4. Results render inline:
   - 5 editable title options (radio to select, text input to edit any of them, plus a free-text field to write a custom title)
   - Editable summary text area
5. User reviews/edits, then clicks **"Upload to YouTube"**
6. Selected/edited title and AI summary are used in the upload (summary overrides `program.description` for RWWA)

---

## Architecture & Components

### New files

**`services/transcription.py`**  
- `extract_audio(video_path: str) -> str` — runs ffmpeg to extract mono mp3 at 16kHz with `-q:a 5`, returns temp file path
- `transcribe(audio_path: str) -> str` — sends audio to OpenAI Whisper API, returns transcript string

**`services/ai_content.py`**  
- `generate_titles_and_summary(transcript: str) -> dict` — sends transcript to Claude, returns `{"titles": [str x5], "summary": str}`
- Prompt asks for 5 distinct title suggestions and a 3–6 sentence summary; format is free-form (no rigid examples for now, with room to add title style examples later)

### Modified files

**`ui/forms.py`**  
- RWWA form renderer updated to show "Generate Titles & Summary" button after video source is provided
- On completion, renders: 5 radio+edit title fields, free-text custom title field, editable summary text area
- Returns selected/edited title and summary in `form_values`

**`pipeline.py`**  
- `run_pipeline()` gains an optional `description: Optional[str] = None` parameter
- When provided, uses it instead of `program.description` for the YouTube upload

**`.env` / `.env.example`**  
- Add `OPENAI_API_KEY`
- Add `ANTHROPIC_API_KEY`

---

## Error Handling

| Scenario | Behavior |
|---|---|
| ffmpeg not installed | Clear error message instructing user to install ffmpeg |
| Video has no audio track | ffmpeg fails gracefully, clear error shown |
| Whisper API fails | Error shown, user can retry; upload not blocked |
| Claude API fails | Error shown, user can retry; upload not blocked |
| User clicks Generate twice | Button disabled during processing; results replaced on completion |

---

## Constraints & Scope

- This feature is **RWWA-only**, gated by `program.key == "rwwa"`. All other programs are unaffected.
- Audio extraction produces mono mp3 at 16kHz with `-q:a 5` — expected output size for a 90-min session is 10–15 MB, well under Whisper API's 25 MB limit. No chunking needed.
- Title examples/style guidance are out of scope for this iteration but the prompt structure should make them easy to add later.

---

## Testing

- Unit tests for `transcription.py`: mock ffmpeg subprocess call, mock Whisper API response
- Unit tests for `ai_content.py`: mock Claude API, verify prompt structure and that output parsing returns correct shape
- Existing tests for all other programs remain unaffected
