import re
import hashlib
from datetime import datetime, timezone


def make_doc_id(text: str) -> str:
    """Generate a safe Firestore document ID from any string."""
    return hashlib.md5(text.encode()).hexdigest()


def is_recent(date_str: str, days: int = 30) -> bool:
    """Check if a date string is within the last N days."""
    if not date_str:
        return True  # keep if no date
    try:
        from dateutil import parser
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - dt).days <= days
    except Exception:
        return True


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_user_topics(users: list) -> dict:
    """
    Returns: { uid: [topics] }
    """
    result = {}
    for user in users:
        uid = user.get("uid") or user.get("_docId")
        if not uid:
            continue
        topics = user.get("topics", [])
        if topics:
            result[uid] = [t.lower() for t in topics]
    return result
