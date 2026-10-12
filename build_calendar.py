"""Scrape every source, keep last-good data on failure, and write docs/calendar.ics."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from coct_calendar.ics import build_calendar
from coct_calendar.sources import SOURCES

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "calendar.ics"
MIN_RATIO = 0.3  # a source returning under 30% of its previous count is treated as broken


def healthy(new, old):
    if not new:
        return False
    return not old or len(new) >= MIN_RATIO * len(old)


def main():
    keywords = json.loads((ROOT / "config" / "keywords.json").read_text(encoding="utf-8"))
    today = date.today()
    start, end = today - timedelta(days=30), today + timedelta(days=180)
    DATA.mkdir(exist_ok=True)

    failures, events = [], []
    for src in SOURCES:
        cache = DATA / f"{src.NAME}.json"
        old = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else []
        try:
            new = src.fetch(start, end)
        except Exception as exc:  # one broken source must not stop the others
            print(f"[{src.NAME}] FAILED: {exc!r}", file=sys.stderr)
            failures.append(src.NAME)
            events += old
            continue
        if healthy(new, old):
            cache.write_text(json.dumps(new, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"[{src.NAME}] {len(new)} events")
            events += new
        else:
            print(f"[{src.NAME}] SUSPICIOUS: got {len(new)}, previously {len(old)}; keeping last good data", file=sys.stderr)
            failures.append(src.NAME)
            events += old

    if events:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_bytes(build_calendar(events, keywords))
        print(f"wrote {OUT} ({len(events)} events)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
