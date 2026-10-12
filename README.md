# CoCT Event Scraper

A subscribable calendar of City of Cape Town council and committee meetings, tagged by topic
(`[HOUSING]`, `[PLANNING]`, `[BUDGET]`, `[COUNCIL]`), for organisations tracking housing, short-term
rental and rent policy.

A daily GitHub Actions job runs `build_calendar.py`, which writes `docs/calendar.ics`.
GitHub Pages serves that file.

## Subscribe
Google Calendar: *Other calendars → + → From URL* and paste `https://<user>.github.io/<repo>/calendar.ics`.
Google refreshes subscribed feeds every 12–24 hours.

## Run locally
```
pip install -r requirements.txt pytest
python build_calendar.py
pytest
```

## Publish (one-off)
1. Push to a public GitHub repo.
2. Settings → Pages → deploy from branch `main`, folder `/docs`.
3. Actions → *Build calendar* → Run workflow (to test).

## How it works
- `coct_calendar/sources/` has one module per City source. Add a module and list it in `sources/__init__.py`.
  `council.py` reads the Council Hub Online API. It reads the API key from the City site's own
  front-end config on each run, so nothing is stored in this repo.
- `config/keywords.json` maps tags to keywords. Matching events get the tag in the title. Nothing is filtered out.
- `data/<source>.json` is the last known good scrape. If a source fails or returns suspiciously few
  events, the build keeps the old data, still publishes, and exits non-zero. The Actions run fails and
  GitHub emails the repo owner.
- Cancelled meetings are kept with `STATUS:CANCELLED`, so calendar apps hide them. The City pre-loads
  the year with placeholder slots and cancels the unused ones.

## Next
- Public participation deadlines: `https://www.capetown.gov.za/city-connect/have-your-say/issues-open-for-public-comment/`
- Subcouncil and Municipal Planning Tribunal meetings (same API: `Meetings/subcouncil/date`, `Meetings/mpts/date`)
- Ask the City for an official API key or `.ics` feed
