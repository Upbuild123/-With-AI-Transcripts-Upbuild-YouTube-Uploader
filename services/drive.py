import os
import re
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service():
    private_key = os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n")
    creds = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=DRIVE_SCOPES,
    )
    return build("drive", "v3", credentials=creds)


def drive_link_to_file_id(link: str) -> str:
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", link)
    if m:
        return m.group(1)
    raise ValueError(f"Could not extract file ID from Drive link: {link}")


def download_drive_file(file_id: str) -> str:
    """Download a Drive file to a temp mp4 file. Returns local path."""
    service = _get_service()
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    downloader = MediaIoBaseDownload(tmp, request, chunksize=10 * 1024 * 1024)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    tmp.close()
    return tmp.name


def upload_to_drive(local_path: str, filename: str) -> str:
    """Upload a local file to the Upbuild Drive folder. Returns webViewLink."""
    service = _get_service()
    folder_id = os.environ["GOOGLE_DRIVE_UPLOADER_FOLDER_ID"]
    meta = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, resumable=True)
    file = service.files().create(
        body=meta, media_body=media, fields="id", supportsAllDrives=True
    ).execute()
    result = service.files().get(
        fileId=file["id"], fields="webViewLink", supportsAllDrives=True
    ).execute()
    return result["webViewLink"]
