import os
import tempfile
from dataclasses import dataclass
from datetime import date
from typing import Optional, Callable

from config import PROGRAM_BY_KEY, CTA_DOC_ID
from services.youtube import load_youtube_service, upload_video
from services.drive import drive_link_to_file_id, download_drive_file
from services.docs import update_cta_doc


@dataclass
class UploadResult:
    youtube_url: str
    drive_url: Optional[str] = None


def run_pipeline(
    program_key: str,
    title: str,
    source_type: str,
    source,
    source_filename: str,
    session_date: date,
    recording_type: Optional[str] = None,
    on_progress: Optional[Callable] = None,
) -> UploadResult:
    def progress(msg: str):
        if on_progress:
            on_progress(msg)

    program = PROGRAM_BY_KEY[program_key]
    tmp_path = None
    drive_url = None

    try:
        progress("Preparing file...")
        if source_type == "local":
            tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            tmp.write(source)
            tmp.close()
            tmp_path = tmp.name
        else:
            file_id = drive_link_to_file_id(source)
            progress("Downloading from Google Drive...")
            tmp_path = download_drive_file(file_id)

        progress("Uploading to YouTube (this may take a while for large files)...")
        yt_service = load_youtube_service()
        youtube_url = upload_video(
            service=yt_service,
            file_path=tmp_path,
            title=title,
            description=program.description,
            playlist_id=program.playlist_id,
            on_progress=lambda pct: progress(f"Uploading to YouTube... {int(pct * 100)}%"),
        )

        if program_key == "cta":
            progress("Updating CTA course calendar...")
            try:
                update_cta_doc(CTA_DOC_ID, session_date, youtube_url, recording_type)
            except Exception as doc_err:
                progress(f"Google Doc update failed: {doc_err}. Please update manually.")

        return UploadResult(youtube_url=youtube_url, drive_url=drive_url)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
