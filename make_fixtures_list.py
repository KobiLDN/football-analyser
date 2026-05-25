"""
Scan index.html for fixtures and write fixtures.json — a minimal list
of (home, away, day, time, competition) ready to upload to DeepSeek
alongside research.template.md.

Default behaviour: every upcoming unplayed fixture in the next 7 days,
across every league, capped at 20.

Flags:
  --league <id>      only this league: pl, laliga, seriea, bundesliga,
                     ligue1, ucl, uel, uecl, worldcup
  --days <N>         only fixtures kicking off in the next N days
                     (default 7; 0 = today only; -1 = no date filter)
  --stubs-only       only fixtures whose summary is 'Pending deep research.'
  --include-played   include fixtures that have a `result` set
  --max <N>          cap the list at N entries (default 20)
  --output <path>    output file (default fixtures.json)

Examples:
  # Upcoming PL fixtures in the next 7 days (default)
  python make_fixtures_list.py --league pl

  # All World Cup stubs still needing research
  python make_fixtures_list.py --league worldcup --stubs-only --days -1 --max 100

  # Everything in the next 3 days
  python make_fixtures_list.py --days 3 --max 50
"""

import argparse
import datetime
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(REPO_ROOT, "index.html")

LEAGUE_NAMES = [
    ("pl",         "Premier League"),
    ("laliga",     "La Liga"),
    ("seriea",     "Serie A"),
    ("bundesliga", "Bundesliga"),
    ("ligue1",     "Ligue 1"),
    ("ucl",        "Champions League"),
    ("uel",        "Europa League"),
    ("uecl",       "Conference League"),
    ("worldcup",   "World Cup 2026"),
]

MONTHS = {
    "January": 1,  "February": 2,  "March": 3,  "April": 4,
    "May": 5,      "June": 6,      "July": 7,   "August": 8,
    "September": 9,"October": 10,  "November": 11, "December": 12,
}


def parse_day(day_str, year=None):
    """Parse 'Friday 15 May' → datetime.date. Returns None on failure."""
    parts = (day_str or "").strip().split()
    if len(parts) < 3:
        return None
    try:
        d = int(parts[1])
        m = MONTHS[parts[2]]
        y = year or datetime.date.today().year
        return datetime.date(y, m, d)
    except (ValueError, KeyError):
        return None


def scan_index(html):
    """Yield {league_id, league_name, home, away, day, time, result, summary}
    for every fixture object literal in the LEAGUES array. Walks the
    file once, tracking which league block we're inside."""
    id_positions = []
    for lid, lname in LEAGUE_NAMES:
        m = re.search(rf"id:\s*'{lid}'", html)
        if m:
            id_positions.append((m.start(), lid, lname))
    id_positions.sort()

    # Compute each league's window
    windows = []
    for i, (pos, lid, lname) in enumerate(id_positions):
        end = id_positions[i + 1][0] if i + 1 < len(id_positions) else len(html)
        windows.append((lid, lname, pos, end))

    for lid, lname, start, end in windows:
        block = html[start:end]
        # Find each fixture in this league: walk by 'home:' anchor
        for m in re.finditer(
            r"day:\s*'([^']+)'[\s\S]{0,400}?"
            r"home:\s*'([^']+)',\s*away:\s*'([^']+)',\s*time:\s*'([^']+)',"
            r"\s*\n\s*result:\s*([^,]+),"
            r"[\s\S]{0,4000}?summary:\s*'((?:[^'\\]|\\.)*?)'",
            block,
        ):
            yield {
                "league_id":   lid,
                "league_name": lname,
                "day":         m.group(1),
                "home":        m.group(2),
                "away":        m.group(3),
                "time":        m.group(4),
                "result":      None if m.group(5).strip() == "null" else m.group(5).strip().strip("'"),
                "summary":     m.group(6),
            }


def main():
    ap = argparse.ArgumentParser(description="Build fixtures.json for DeepSeek upload")
    ap.add_argument("--league",         default=None,
                    help="filter by league id (pl, laliga, ucl, worldcup, ...)")
    ap.add_argument("--days",           type=int, default=7,
                    help="only fixtures within N days from today (-1 = no filter)")
    ap.add_argument("--stubs-only",     action="store_true",
                    help="only fixtures with 'Pending deep research.' summary")
    ap.add_argument("--include-played", action="store_true",
                    help="include fixtures that already have a result")
    ap.add_argument("--max",            type=int, default=20, dest="max_n",
                    help="cap at N fixtures (default 20)")
    ap.add_argument("--output",         default=os.path.join(REPO_ROOT, "fixtures.json"),
                    help="output file (default fixtures.json)")
    args = ap.parse_args()

    if not os.path.exists(HTML_FILE):
        print(f"X index.html not found at {HTML_FILE}")
        sys.exit(1)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    all_fixtures = list(scan_index(html))
    if not all_fixtures:
        print("X No fixtures found in index.html (regex may need updating)")
        sys.exit(1)

    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=args.days) if args.days >= 0 else None

    out = []
    for f in all_fixtures:
        if args.league and f["league_id"] != args.league:
            continue
        if not args.include_played and f["result"] is not None:
            continue
        if args.stubs_only and f["summary"] != "Pending deep research.":
            continue
        d = parse_day(f["day"])
        if d is None:
            continue
        if cutoff is not None and not (today <= d <= cutoff):
            continue
        out.append({
            "home":        f["home"],
            "away":        f["away"],
            "day":         f["day"],
            "time":        f["time"],
            "competition": f["league_name"],
        })

    # Sort by date then time for predictable output
    def key(x):
        d = parse_day(x["day"]) or datetime.date(9999, 1, 1)
        return (d.toordinal(), x["time"])
    out.sort(key=key)

    if len(out) > args.max_n:
        print(f"  trimming {len(out)} candidates down to --max {args.max_n}")
        out = out[: args.max_n]

    if not out:
        print(f"No fixtures matched.")
        if args.stubs_only:
            print(f"  (--stubs-only is on — no pending fixtures match the filter)")
        sys.exit(0)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"OK Wrote {len(out)} fixture(s) to {args.output}:")
    for x in out:
        print(f"  - {x['day']:<22} {x['time']}  {x['home']} vs {x['away']}  [{x['competition']}]")

    print()
    print(f"Next steps:")
    print(f"  1. Upload {os.path.basename(args.output)} and research.template.md to DeepSeek")
    print(f"  2. Ask: 'Research every fixture in fixtures.json using the schema in")
    print(f"     research.template.md. Return a single JSON array of fixture objects.'")
    print(f"  3. Paste the array into research.json")
    print(f"  4. Double-click apply_research.bat")


if __name__ == "__main__":
    main()
