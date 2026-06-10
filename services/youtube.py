import base64
import io
import os
import pickle
from typing import Optional, Callable
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_creds_from_secret() -> object:
    try:
        import streamlit as st
        raw = st.secrets["YOUTUBE_TOKEN_B64"]
        return pickle.loads(base64.b64decode(raw))
    except Exception:
        return None


def load_youtube_service():
    token_file = os.environ.get("YOUTUBE_TOKEN_FILE", "token.json")
    if not os.path.isabs(token_file):
        token_file = os.path.join(_PROJECT_ROOT, token_file)

    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    else:
        creds = _load_creds_from_secret()
        if creds is None:
            raise FileNotFoundError(
                f"YouTube token not found at {token_file}. Run: python auth_setup.py"
            )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        if os.path.exists(token_file):
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def get_playlist_titles(service, playlist_id: str):
    """Fetch all video titles from a playlist (handles pagination)."""
    titles = []
    page_token = None
    while True:
        resp = service.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token,
        ).execute()
        for item in resp.get("items", []):
            title = item["snippet"]["title"]
            if title in ("Deleted video", "Private video"):
                continue
            titles.append(title)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return titles


def upload_video(
    service,
    file_path: str,
    title: str,
    description: str,
    playlist_id: str,
    on_progress: Optional[Callable] = None,
    privacy_status: str = "unlisted",
) -> str:
    """Upload mp4 to YouTube (default unlisted) and add to playlist. Returns YouTube URL."""
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "27",
        },
        "status": {"privacyStatus": privacy_status},
    }
    media = MediaFileUpload(file_path, chunksize=10 * 1024 * 1024, resumable=True)
    request = service.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status and on_progress:
            on_progress(status.progress())

    video_id = response["id"]
    service.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        },
    ).execute()
    return f"https://www.youtube.com/watch?v={video_id}"
