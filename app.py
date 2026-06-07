import base64
import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Upbuild Video Uploader", layout="centered")

logo_path = os.path.join(os.path.dirname(__file__), "assets", "upbuild_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{b64}" style="height:60px; margin-bottom:24px;">',
        unsafe_allow_html=True,
    )

st.title("Upbuild Video Uploader")

from config import PROGRAMS, PROGRAM_BY_KEY
from programs.dates import most_recent_weekday, today_eastern
from ui.forms import FORM_RENDERERS
from pipeline import run_pipeline
from services.email import send_error_alert

program_label = st.selectbox("Program", [p.label for p in PROGRAMS])
program = next(p for p in PROGRAMS if p.label == program_label)

default_date = most_recent_weekday(program.scheduled_day)
session_date = st.date_input(
    "Session date",
    value=default_date,
    max_value=today_eastern(),
)

source_type = st.radio("Video source", ["Upload local file", "Google Drive link"])

uploaded_file = None
drive_link = None

if source_type == "Upload local file":
    uploaded_file = st.file_uploader("Choose mp4 file", type=["mp4"])
else:
    drive_link = st.text_input("Google Drive link")

# Derive source for RWWA form (needed before the upload button)
_src_type = "local" if source_type == "Upload local file" else "drive"
_src = None
if _src_type == "local" and uploaded_file is not None:
    _src = uploaded_file.read()
    uploaded_file.seek(0)  # Reset so the upload button can read it again
elif _src_type == "drive" and drive_link:
    _src = drive_link

st.divider()

if program.key == "rwwa":
    form_values = FORM_RENDERERS[program.key](session_date, video_source=_src, video_source_type=_src_type)
else:
    form_values = FORM_RENDERERS[program.key](session_date)
title = form_values.get("title", "")

if title:
    st.markdown(f"**Preview title:** `{title}`")

can_upload = bool(title) and (uploaded_file is not None or bool(drive_link))
if st.button("Upload to YouTube", disabled=not can_upload, type="primary"):
    progress_placeholder = st.empty()

    def on_progress(msg: str):
        progress_placeholder.info(msg)

    try:
        if source_type == "Upload local file":
            file_bytes = uploaded_file.read()
            source = file_bytes
            source_filename = uploaded_file.name
            src_type = "local"
        else:
            source = drive_link
            source_filename = f"{title}.mp4"
            src_type = "drive"

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

        progress_placeholder.empty()
        st.success("Upload complete!")
        st.markdown(f"**YouTube URL:** [{result.youtube_url}]({result.youtube_url})")
        if result.drive_url:
            st.markdown(f"**Drive URL:** [{result.drive_url}]({result.drive_url})")

    except Exception as exc:
        progress_placeholder.empty()
        st.error(f"Upload failed: {exc}")
        send_error_alert(
            program=program_label,
            attempted_title=title,
            error=exc,
        )
