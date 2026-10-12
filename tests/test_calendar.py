import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from build_calendar import healthy
from coct_calendar.ics import build_calendar
from coct_calendar.sources.council import _to_event
from coct_calendar.tagging import tags_for

KEYWORDS = {"HOUSING": ["human settlements"], "PLANNING": ["planning"]}

RAW = {
    "meetingId": 1, "title": "Human Settlements PC - [Cancelled]", "meetingDate": "2026-10-01T00:00:00",
    "startTime": "10:00:00", "endTime": "14:00:00", "status": "Cancelled", "meetingType": "Ordinary",
    "meetingVenue": {"title": "Room A"}, "modifiedDate": "2025-12-24T14:25:08.18",
}


def test_cancelled_marker_moves_to_status():
    e = _to_event(RAW)
    assert e["title"] == "Human Settlements PC" and e["cancelled"] and e["start"] == "10:00"


def test_tags_and_ics():
    e = _to_event(RAW)
    assert tags_for(e, KEYWORDS) == ["HOUSING"]
    ics = build_calendar([e], KEYWORDS).decode()
    assert "SUMMARY:[HOUSING] Human Settlements PC" in ics
    assert "STATUS:CANCELLED" in ics and "UID:coct-council-1@coct-calendar" in ics


def test_build_is_deterministic():
    e = _to_event(RAW)
    assert build_calendar([e], KEYWORDS) == build_calendar([e], KEYWORDS)


def test_health_guard():
    assert not healthy([], [1, 2, 3])
    assert not healthy([1], [1] * 10)
    assert healthy([1] * 5, [1] * 10)
    assert healthy([1], [])
