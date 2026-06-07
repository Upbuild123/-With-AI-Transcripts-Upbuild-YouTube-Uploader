import os
from datetime import date
from typing import Tuple, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from programs.dates import fmt_mon_period_dd_yyyy

DOCS_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

COL_FULL_GROUP = 3
COL_FACILITATORS = 4


def _get_service():
    private_key = os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n")
    creds = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=DOCS_SCOPES,
    )
    return build("docs", "v1", credentials=creds)


def _cell_text(cell: dict) -> str:
    parts = []
    for block in cell.get("content", []):
        for elem in block.get("paragraph", {}).get("elements", []):
            parts.append(elem.get("textRun", {}).get("content", ""))
    return "".join(parts)


def _find_cell_range(doc: dict, date_str: str, col_index: int) -> Tuple[int, int]:
    """Return (startIndex, endIndex) of the target cell for the row whose first cell contains date_str."""
    for element in doc.get("body", {}).get("content", []):
        if "table" not in element:
            continue
        for row in element["table"]["tableRows"]:
            cells = row["tableCells"]
            if date_str in _cell_text(cells[0]):
                cell = cells[col_index]
                return cell["startIndex"], cell["endIndex"]
    raise ValueError(f"Row with date '{date_str}' not found in document table.")


def _get_target_cell(doc: dict, date_str: str, col_index: int) -> dict:
    """Return the cell dict for the matching row and column."""
    for element in doc.get("body", {}).get("content", []):
        if "table" not in element:
            continue
        for row in element["table"]["tableRows"]:
            cells = row["tableCells"]
            if date_str in _cell_text(cells[0]):
                return cells[col_index]
    raise ValueError(f"Row with date '{date_str}' not found.")


def update_cta_doc(doc_id: str, session_date: date, youtube_url: str, recording_type: str) -> None:
    """
    Write a YouTube hyperlink into the CTA course calendar Google Doc.
    recording_type == "Full Group" -> column 3, overwrite.
    Any other value (facilitator name) -> column 4, append.
    """
    service = _get_service()
    doc = service.documents().get(documentId=doc_id).execute()
    date_str = fmt_mon_period_dd_yyyy(session_date)
    is_full_group = recording_type == "Full Group"
    col_index = COL_FULL_GROUP if is_full_group else COL_FACILITATORS

    cell_start, cell_end = _find_cell_range(doc, date_str, col_index)
    content_start = cell_start + 1
    content_end = cell_end - 1

    link_text = "Full Group" if is_full_group else recording_type

    requests = []
    if is_full_group:
        if content_end > content_start:
            requests.append({
                "deleteContentRange": {
                    "range": {"startIndex": content_start, "endIndex": content_end}
                }
            })
        insert_index = content_start
    else:
        target_cell = _get_target_cell(doc, date_str, col_index)
        existing = _cell_text(target_cell).strip()
        if existing:
            link_text = f"\n{recording_type}"
        insert_index = content_end

    requests.append({
        "insertText": {"location": {"index": insert_index}, "text": link_text}
    })
    requests.append({
        "updateTextStyle": {
            "range": {
                "startIndex": insert_index,
                "endIndex": insert_index + len(link_text),
            },
            "textStyle": {"link": {"url": youtube_url}},
            "fields": "link",
        }
    })

    service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
