import base64
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from typing import Dict, Any


def _b64u_decode(data: str) -> str:
    """Decode base64url string (Google uses urlsafe base64)."""
    if not data:
        return ""
    # Add padding if missing
    padding = len(data) % 4
    if padding:
        data += "=" * (4 - padding)
    try:
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception:
        # defensive fallback
        try:
            return base64.b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""


def _get_plain_text_from_payload(payload: Dict[str, Any]) -> str:
    """
    Recursively extract plain text from a Gmail payload.
    Handles:
      - text/plain (direct)
      - text/html (convert to text via BeautifulSoup)
      - multipart with parts/subparts
    """
    if not payload:
        return ""

    mime_type = payload.get("mimeType", "").lower()
    body = payload.get("body", {}) or {}
    data = body.get("data")

    # Direct text/plain
    if mime_type == "text/plain" and data:
        return _b64u_decode(data)

    # HTML -> convert to plain text
    if mime_type == "text/html" and data:
        html = _b64u_decode(data)
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator="\n", strip=True)

    # If there are parts, try them in order
    parts = payload.get("parts") or []
    for part in parts:
        text = _get_plain_text_from_payload(part)
        if text:
            return text

    # No text found here
    return ""


def parse_message(raw_message: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse a Gmail 'full' message resource into a simple dict:
      { 'id', 'from', 'subject', 'date', 'body' }

    raw_message is the dict returned by:
      service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    """
    payload = raw_message.get("payload", {}) or {}
    headers_list = payload.get("headers", []) or []

    headers = {h.get("name", ""): h.get("value", "") for h in headers_list}
    sender = headers.get("From", "")
    subject = headers.get("Subject", "")
    date_hdr = headers.get("Date", "")

    # Parse date to ISO if possible
    try:
        date_iso = parsedate_to_datetime(date_hdr).isoformat()
    except Exception:
        # fallback to raw header or empty
        date_iso = date_hdr or ""

    # Try extracting body from payload; fallback to top-level snippet
    body_text = _get_plain_text_from_payload(payload)
    if not body_text:
        # the API returns a short 'snippet' that is safe to use as fallback
        body_text = raw_message.get("snippet", "") or ""

    return {
        "id": raw_message.get("id", ""),
        "from": sender,
        "subject": subject,
        "date": date_iso,
        "body": body_text.strip(),
    }
