import os
import re
import tempfile
from datetime import date
import streamlit as st
from typing import Dict, Any

from programs.cta_calendar import scheduled_dates, lookup_session
from programs.dates import today_eastern
from programs.bhakti_sastri_verses import next_bhakti_sastri_verses
from programs.counters import (
    next_committed_bhakti_session,
    next_morning_rounds_session,
    next_library_live_episode,
    next_rwwa_part,
)
from programs.titles import (
    build_cta_title,
    build_bhakti_sastri_title,
    build_committed_bhakti_title,
    build_morning_rounds_title,
    build_library_live_title,
    build_rwwa_title,
)
from services.youtube import load_youtube_service, get_playlist_titles
from config import PROGRAM_BY_KEY


def _show_previous_title(playlist_id: str) -> None:
    try:
        titles = _cached_playlist_titles(playlist_id)
        if titles:
            st.caption(f"Previous upload: {titles[0]}")
    except Exception:
        pass


def _editable_title(generated: str) -> str:
    return st.text_input("YouTube title (edit if needed)", value=generated)


@st.cache_data(ttl=300)
def _cached_playlist_titles(playlist_id: str):
    """Cache playlist titles for 5 minutes to avoid hitting the API on every re-render."""
    yt = load_youtube_service()
    return get_playlist_titles(yt, playlist_id)


def _cta_privacy_status() -> str:
    privacy_label = st.radio(
        "Visibility",
        options=["Unlisted", "Private"],
        index=0,
        key="cta_privacy",
        horizontal=True,
    )
    return "private" if privacy_label == "Private" else "unlisted"


def render_cta_form(session_date: date) -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["cta"].playlist_id)
    dates = scheduled_dates()
    date_options = [d for d in dates if d <= today_eastern()]

    if not date_options:
        st.warning("No past CTA sessions found in the calendar — using previous YouTube title as a starting point.")
        try:
            yt_titles = _cached_playlist_titles(PROGRAM_BY_KEY["cta"].playlist_id)
            prev_title = yt_titles[0] if yt_titles else ""
        except Exception:
            prev_title = ""
        title = st.text_input("YouTube title", value=prev_title)
        if not title:
            return {}
        return {
            "title": title,
            "session_date": session_date,
            "recording_type": None,
            "privacy_status": _cta_privacy_status(),
        }

    selected_date = st.selectbox(
        "Session date",
        options=date_options,
        format_func=lambda d: f"{d.strftime('%b')} {d.day}, {d.year}",
        index=len(date_options) - 1,
    )
    try:
        session = lookup_session(selected_date)
    except KeyError:
        st.error("Could not find session for selected date.")
        return {}

    st.info(f"**{session.season} — {session.session_label}:** {session.class_title}")

    recording_options = ["Full Group"] + session.facilitators
    recording_type = st.selectbox("Recording type", recording_options)

    title = _editable_title(build_cta_title(session.season, session.session_label, recording_type, selected_date))
    return {
        "session_date": selected_date,
        "session_label": session.session_label,
        "season": session.season,
        "recording_type": recording_type,
        "title": title,
        "privacy_status": _cta_privacy_status(),
    }


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
                    st.session_state["rwwa_title_radio"] = 0
                    # Reset editable inputs so new generated titles appear in the fields
                    for i, t in enumerate(result["titles"]):
                        st.session_state[f"rwwa_title_{i}"] = t
                    st.session_state["rwwa_custom_title"] = ""
                    st.session_state["rwwa_summary"] = result["summary"]

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
        st.markdown("**Suggested titles** — select one, or edit any field below:")

        # Single radio to pick which title to use
        selected_idx = st.radio(
            "Select a title",
            options=list(range(len(titles))),
            format_func=lambda i: titles[i],
            index=st.session_state[SELECTED_TITLE_KEY],
            key="rwwa_title_radio",
            label_visibility="collapsed",
        )
        st.session_state[SELECTED_TITLE_KEY] = selected_idx

        # Editable text input for each title
        edited_titles = []
        for i, t in enumerate(titles):
            edited = st.text_input(
                f"Edit option {i + 1}",
                value=t,
                key=f"rwwa_title_{i}",
                label_visibility="visible",
            )
            edited_titles.append(edited)

        final_title = edited_titles[selected_idx] if edited_titles else ""

        custom = st.text_input(
            "Or type a custom title",
            key="rwwa_custom_title",
            placeholder="Leave blank to use the selected option above",
        )
        if custom.strip():
            final_title = custom.strip()
    else:
        final_title = st.text_input("YouTube title (edit if needed)", value="")

    if not final_title:
        return {}

    try:
        rwwa_titles = _cached_playlist_titles(PROGRAM_BY_KEY["rwwa"].playlist_id)
    except Exception:
        rwwa_titles = []
    part_num = next_rwwa_part(rwwa_titles, final_title)
    final_title = st.text_input(
        "YouTube title (with RWWA prefix, part #, and date)",
        value=build_rwwa_title(final_title, part_num, session_date),
        key="rwwa_final_title",
    )

    if not final_title:
        return {}

    # --- Summary ---
    summary = st.session_state[GEN_SUMMARY_KEY]
    final_summary = st.text_area("Session summary (used as YouTube description)",
                                 value=summary, height=150, key="rwwa_summary")

    return {
        "title": final_title,
        "description": final_summary if final_summary.strip() else None,
    }


def render_bhakti_sastri_form(session_date: date) -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["bhakti_sastri"].playlist_id)
    try:
        bs_titles = _cached_playlist_titles(PROGRAM_BY_KEY["bhakti_sastri"].playlist_id)
        suggested_verses = next_bhakti_sastri_verses(bs_titles) or ""
    except Exception:
        suggested_verses = ""
    verses = st.text_input("Verses", value=suggested_verses)
    part_str = st.text_input("Part number (leave blank if not needed)")
    part_num = int(part_str) if part_str.strip().isdigit() else None
    if not verses:
        return {}
    title = _editable_title(build_bhakti_sastri_title(verses, part_num, session_date))
    return {"title": title, "verses": verses, "part_num": part_num}


def render_committed_bhakti_form(session_date: date) -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["committed_bhakti"].playlist_id)
    with st.spinner("Fetching session number from YouTube..."):
        try:
            titles = _cached_playlist_titles(PROGRAM_BY_KEY["committed_bhakti"].playlist_id)
            session_num = next_committed_bhakti_session(titles)
        except Exception:
            session_num = 1

    session_num = st.number_input("Session number", min_value=1, value=session_num, step=1)
    topics = st.text_input("Topics")
    if not topics:
        return {}
    title = _editable_title(build_committed_bhakti_title(int(session_num), topics, session_date))
    return {"title": title, "session_num": int(session_num), "topics": topics}


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


def render_library_live_form(session_date: date) -> Dict[str, Any]:
    _show_previous_title(PROGRAM_BY_KEY["library_live"].playlist_id)
    titles = []
    with st.spinner("Fetching episode number from YouTube..."):
        try:
            titles = _cached_playlist_titles(PROGRAM_BY_KEY["library_live"].playlist_id)
            episode_num = next_library_live_episode(titles)
        except Exception as e:
            st.warning(f"Could not fetch episode number from YouTube: {e}")
            episode_num = 1

    prev_ep_title = ""
    if titles:
        m = re.match(r"^\d+ - (.+?) \(\d{4}\.\d{2}\.\d{2}\)$", titles[0])
        if m:
            prev_ep_title = m.group(1)

    episode_num = st.number_input("Episode number", min_value=1, value=episode_num, step=1)
    ep_title = st.text_input("Episode title", value=prev_ep_title)
    if not ep_title:
        return {}
    title = _editable_title(build_library_live_title(int(episode_num), ep_title, session_date))
    return {"title": title, "episode_num": int(episode_num), "ep_title": ep_title}


FORM_RENDERERS = {
    "cta": render_cta_form,
    "rwwa": render_rwwa_form,
    "bhakti_sastri": render_bhakti_sastri_form,
    "committed_bhakti": render_committed_bhakti_form,
    "morning_rounds": render_morning_rounds_form,
    "library_live": render_library_live_form,
}
