"""Council and Committee meetings from the City's Council Hub Online API."""
import re
from datetime import date

import requests

CONFIG_URL = "https://web1.capetown.gov.za/web1/councilhubonline/assets/config/appsettings.json"
PAGE_URL = "https://web1.capetown.gov.za/web1/councilhubonline/councilandCommitteemeetings"
USER_AGENT = "coct-calendar/0.1 (public-interest event calendar; contact via GitHub repo)"

NAME = "council"


def _months(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m > 12:
            y, m = y + 1, 1


def _api_credentials(session):
    # The key is published in the City's own front-end config; read it fresh each
    # run so a rotation by the City does not break the build.
    cfg = session.get(CONFIG_URL, timeout=30)
    cfg.raise_for_status()
    data = cfg.json()
    return data["apiBaseUrl"], data["CouncillorsApiKey"]


def _to_event(m):
    title = re.sub(r"\s*-?\s*\[Cancelled\]\s*$", "", m["title"], flags=re.I).strip()
    venue = (m.get("meetingVenue") or {}).get("title") or ""
    return {
        "uid": f"coct-council-{m['meetingId']}",
        "title": title,
        "date": m["meetingDate"][:10],
        "start": (m.get("startTime") or "")[:5] or None,
        "end": (m.get("endTime") or "")[:5] or None,
        "location": venue,
        "cancelled": (m.get("status") or "").lower() == "cancelled",
        "details": m.get("description") or "",
        "meeting_type": m.get("meetingType") or "",
        "modified": m.get("modifiedDate") or m.get("createdDate") or "",
        "url": PAGE_URL,
    }


def fetch(start: date, end: date):
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    base, key = _api_credentials(session)
    events = {}
    for year, month in _months(start, end):
        r = session.get(
            f"{base}Meetings/ecs/date",
            params={"year": year, "month": month, "day": "", "publishedToWWW": "true"},
            headers={"X-Api-Key": key},
            timeout=30,
        )
        if r.status_code == 404:  # the API answers 404 for months with no published meetings
            continue
        r.raise_for_status()
        for m in r.json().get("data") or []:
            ev = _to_event(m)
            events[ev["uid"]] = ev
    return sorted(events.values(), key=lambda e: (e["date"], e["start"] or "", e["title"]))
