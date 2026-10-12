from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from .tagging import tags_for

TZ = ZoneInfo("Africa/Johannesburg")


def _parse_modified(value):
    try:
        return datetime.fromisoformat(value).replace(tzinfo=TZ)
    except ValueError:
        return datetime(2000, 1, 1, tzinfo=TZ)


def build_calendar(events, keywords, name="Cape Town political events"):
    cal = Calendar()
    cal.add("prodid", "-//coct-calendar//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", name)
    cal.add("x-wr-timezone", "Africa/Johannesburg")
    cal.add("x-published-ttl", "PT12H")
    cal.add("refresh-interval", timedelta(hours=12))

    for e in events:
        tags = tags_for(e, keywords)
        ev = Event()
        ev.add("uid", f"{e['uid']}@coct-calendar")
        prefix = "".join(f"[{t}] " for t in tags)
        ev.add("summary", f"{prefix}{e['title']}")

        d = date.fromisoformat(e["date"])
        if e["start"]:
            sh, sm = map(int, e["start"].split(":"))
            start = datetime(d.year, d.month, d.day, sh, sm, tzinfo=TZ)
            if e["end"]:
                eh, em = map(int, e["end"].split(":"))
                end = datetime(d.year, d.month, d.day, eh, em, tzinfo=TZ)
            else:
                end = start + timedelta(hours=2)
            ev.add("dtstart", start)
            ev.add("dtend", max(end, start + timedelta(minutes=30)))
        else:
            ev.add("dtstart", d)
            ev.add("dtend", d + timedelta(days=1))

        if e["location"]:
            ev.add("location", e["location"])
        lines = []
        if e["cancelled"]:
            lines.append("CANCELLED")
        if tags:
            lines.append("Topics: " + ", ".join(tags))
        if e["meeting_type"]:
            lines.append(f"Type: {e['meeting_type']}")
        if e["details"]:
            lines.append(e["details"])
        lines.append(f"Agendas, reports and minutes: {e['url']}")
        ev.add("description", "\n".join(lines))
        ev.add("url", e["url"])
        ev.add("status", "CANCELLED" if e["cancelled"] else "CONFIRMED")
        modified = _parse_modified(e["modified"])
        ev.add("dtstamp", modified)
        ev.add("last-modified", modified)
        cal.add_component(ev)
    return cal.to_ical()
