"""
Game-day refresh: reset only fixtures kicking off in the next N days
back to stubs, then trigger the agent to re-research them.

Default --days 1 = today only. --days 2 = today + tomorrow, etc.
Useful on a Saturday morning to incorporate the latest team news /
injury updates without re-researching the entire week.

Run order:
  1. find fixtures whose `day` field is within the window
  2. for each unplayed one, reset its `summary` to 'Pending deep research.'
  3. invoke agent.run() — same hardened pipeline as run_agent.bat

Run: python refresh_today.py [--days N]
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

HTML_FILE = "index.html"
STUB = "summary: 'Pending deep research.'"
SUMMARY_RE = re.compile(r"summary:\s*'((?:[^'\\]|\\.)*?)'")

MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
    'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12,
}


def parse_day_field(day_str, year=None):
    """Parse 'Friday 15 May' -> datetime.date. Returns None on failure."""
    if not day_str:
        return None
    parts = day_str.strip().split()
    if len(parts) < 3:
        return None
    try:
        d = int(parts[1])
        m = MONTHS[parts[2]]
        y = year or datetime.date.today().year
        return datetime.date(y, m, d)
    except (ValueError, KeyError):
        return None


def find_fixtures_in_window(html, days):
    """Return list of (start_idx, end_idx, day_str, home, away, summary_match)
    for fixtures whose day falls within [today, today + days - 1]."""
    today = datetime.date.today()
    end_day = today + datetime.timedelta(days=days - 1)

    hits = []
    # iterate every fixture block by walking 'home:' anchors
    for m in re.finditer(r"home:\s*'([^']+)'", html):
        # look ahead a reasonable window for this fixture's fields
        block_end = m.end() + 6000
        block = html[m.start():block_end]
        day_m   = re.search(r"day:\s*'([^']+)'",       block)
        away_m  = re.search(r"away:\s*'([^']+)'",      block)
        res_m   = re.search(r"result:\s*([^,]+),",     block)
        sum_m   = SUMMARY_RE.search(block)
        if not (day_m and away_m and res_m and sum_m):
            continue
        # Skip played fixtures (result has a scoreline)
        if res_m.group(1).strip() != "null":
            continue
        d = parse_day_field(day_m.group(1))
        if d is None or not (today <= d <= end_day):
            continue
        home = m.group(1)
        away = away_m.group(1)
        summary_abs_start = m.start() + sum_m.start()
        summary_abs_end   = m.start() + sum_m.end()
        hits.append({
            'home': home, 'away': away, 'day': day_m.group(1), 'date': d,
            'summary_start': summary_abs_start,
            'summary_end':   summary_abs_end,
            'current_summary': sum_m.group(1),
        })
    return hits


def reset_window(days):
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    hits = find_fixtures_in_window(html, days)
    if not hits:
        print(f"No unplayed fixtures in the next {days} day(s) — nothing to reset.")
        return 0

    print(f"Found {len(hits)} unplayed fixture(s) in window:")
    for h in hits:
        print(f"  {h['date']}  {h['home']} vs {h['away']}")

    # Reset from end to start so earlier offsets stay valid
    hits.sort(key=lambda h: h['summary_start'], reverse=True)
    reset_count = 0
    for h in hits:
        if h['current_summary'] == 'Pending deep research.':
            continue  # already a stub
        html = html[:h['summary_start']] + STUB + html[h['summary_end']:]
        reset_count += 1

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Reset {reset_count} fixtures to stub state.")
    return reset_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=1,
                    help='How many days ahead to refresh (1 = today only).')
    ap.add_argument('--no-research', action='store_true',
                    help='Reset only — skip the agent run.')
    args = ap.parse_args()

    print(f"Game-day refresh: today + {args.days - 1} day(s) ahead\n")
    reset_window(args.days)

    if args.no_research:
        print("Skipping research. Run auto_research.py manually to research stubs.")
        return

    print("\nRunning auto_research.py on any stubs (newly reset + pre-existing)...")
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_research.py")
    subprocess.run([sys.executable, script, "--days", str(args.days)], check=True)


if __name__ == '__main__':
    main()
