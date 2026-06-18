"""
Scan index.html for fixtures and write fixtures.json — a minimal list
of (home, away, day, time, competition) ready to upload to DeepSeek
alongside research.template.md.

Default behaviour: every upcoming unplayed fixture in the next 7 days,
across every league, capped at 20, skipping knockout placeholders.

Flags:
  --league <id>            only this league: pl, laliga, seriea, bundesliga,
                           ligue1, ucl, uel, uecl, worldcup
  --days <N>               only fixtures kicking off in the next N days
                           (default 7; 0 = today only; -1 = no date filter)
  --stubs-only             only fixtures whose summary is 'Pending deep research.'
  --include-played         include fixtures that have a `result` set
  --include-placeholders   include W99 / 2A / L101 names (off by default —
                           DeepSeek can't research them)
  --offset <N>             skip the first N matching fixtures (for batching)
  --max <N>                cap the list at N entries (default 20)
  --output <path>          output file (default fixtures.json)

Recommended batching workflow when DeepSeek truncates a large request:

  # First batch — uses --stubs-only so already-researched ones are excluded
  python make_fixtures_list.py --league worldcup --stubs-only --days -1 --max 25
  # ... upload to DeepSeek, paste into research.json, apply_research.bat ...
  # Then for the next batch, run the same command again — fixtures you just
  # applied are no longer stubs, so they're skipped automatically.

  # OR use --offset if you don't want --stubs-only to filter for you:
  python make_fixtures_list.py --league worldcup --days -1 --max 25 --offset 25
  python make_fixtures_list.py --league worldcup --days -1 --max 25 --offset 50
"""

import argparse
import datetime
import json
import os
import re
import sys

from team_intel import build_intel_block, is_international

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
    ap.add_argument("--include-placeholders", action="store_true",
                    help="include knockout placeholders like W99 / 2A / L101 "
                         "(skipped by default — DeepSeek can't research these)")
    ap.add_argument("--offset",         type=int, default=0,
                    help="skip the first N matching fixtures (for batching)")
    ap.add_argument("--max",            type=int, default=20, dest="max_n",
                    help="cap at N fixtures (default 20)")
    ap.add_argument("--output",         default=os.path.join(REPO_ROOT, "fixtures.json"),
                    help="output file (default fixtures.json)")
    args = ap.parse_args()


    # Knockout-bracket placeholder names openfootball / similar use until
    # the actual teams are known: W99, L102, 2A, 3B, 1C, R16W2 etc.
    placeholder_re = re.compile(r"^[A-Z]?\d+[A-Z]?$|^R\d+[A-Z]\d*$")
    def is_placeholder(team):
        return bool(placeholder_re.match(team))

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
    skipped_placeholders = 0
    for f in all_fixtures:
        if args.league and f["league_id"] != args.league:
            continue
        if not args.include_played and f["result"] is not None:
            continue
        if args.stubs_only and f["summary"] != "Pending deep research.":
            continue
        if not args.include_placeholders and (
            is_placeholder(f["home"]) or is_placeholder(f["away"])
        ):
            skipped_placeholders += 1
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

    # Apply --offset (skip first N) after sort, so batching is predictable
    if args.offset > 0:
        if args.offset >= len(out):
            print(f"--offset {args.offset} skips past all {len(out)} matches.")
            sys.exit(0)
        print(f"  --offset {args.offset}: skipping first {args.offset} of {len(out)} matches")
        out = out[args.offset:]

    if skipped_placeholders:
        print(f"  skipped {skipped_placeholders} knockout placeholder fixture(s) "
              f"(W99/2A/L101 etc.) — use --include-placeholders to keep them")

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

    # Build a ready-to-paste DeepSeek prompt with the fixtures embedded.
    # User just copies the file and pastes into DeepSeek — no upload, no
    # manual customisation, the schema + team-name list + fixtures are all
    # baked in.
    prompt_path = os.path.join(REPO_ROOT, "fixtures_research_needed_prompt.txt")
    write_prompt_txt(prompt_path, out, html)
    print()
    print(f"OK Wrote ready-to-paste prompt to {os.path.basename(prompt_path)}")

    print()
    print(f"Next steps:")
    print(f"  1. Open fixtures_research_needed_prompt.txt, copy all")
    print(f"     -> paste into DeepSeek (web search ON)")
    print(f"  2. Save the JSON DeepSeek returns into this repo folder")
    print(f"     (DeepSeek's default filename 'deepseek_json_*.json' is auto-detected)")
    print(f"  3. Double-click apply_research.bat -- done.")


def write_prompt_txt(path, fixtures, html):
    """Write a self-contained DeepSeek prompt with fixtures + schema +
    canonical team names already embedded. User just copies + pastes."""

    # Build per-league canonical team list from the current index.html
    id_positions = []
    for lid, lname in LEAGUE_NAMES:
        m = re.search(rf"id:\s*'{lid}'", html)
        if m:
            id_positions.append((m.start(), lid, lname))
    id_positions.sort()
    windows = []
    for i, (pos, lid, lname) in enumerate(id_positions):
        end = id_positions[i + 1][0] if i + 1 < len(id_positions) else len(html)
        windows.append((lname, html[pos:end]))

    # Wider placeholder filter for the team list — also catches slashed
    # group cross-references like '3A/B/C/D/F' that openfootball uses
    # for ranked-third-place playoff slots.
    placeholder_re = re.compile(
        r"^[A-Z]?\d+[A-Z]?$"           # W99, L101, 2A, 3B
        r"|^R\d+[A-Z]\d*$"             # R16W2 etc.
        r"|^\d+[A-Z](/[A-Z])+$"        # 3A/B/C/D/F
    )
    team_list_lines = []
    for lname, block in windows:
        teams = set()
        for m in re.finditer(r"home:\s*'([^']+)',\s*away:\s*'([^']+)'", block):
            teams.add(m.group(1))
            teams.add(m.group(2))
        real = {t for t in teams if not placeholder_re.match(t)}
        if real:
            team_list_lines.append(f"### {lname}")
            team_list_lines.append(", ".join(sorted(real)))
            team_list_lines.append("")

    fixtures_block_lines = []
    for i, f in enumerate(fixtures, 1):
        fixtures_block_lines.append(
            f"{i:>3}. {f['home']} vs {f['away']} — "
            f"{f['day']}, {f['time']}, {f['competition']}"
        )
        if is_international(f['competition']):
            intel = build_intel_block(f['home'], f['away'])
            if intel:
                for line in intel.strip().splitlines():
                    fixtures_block_lines.append(f"     {line}")

    prompt = f"""Research the football fixtures listed below. Use web search (must be ON)
for each one: current team news, injuries, last 5 results form, head-to-head,
and pundit consensus.

FIXTURES TO RESEARCH ({len(fixtures)} total — use the EXACT home/away/day
values as listed):

{chr(10).join(fixtures_block_lines)}

Return ONLY a single JSON array (no markdown, no code fence, no prose around it).
Each fixture object must have this exact shape:

{{
  "home":     "<EXACT team name — see canonical list at the bottom>",
  "away":     "<EXACT team name — see canonical list at the bottom>",
  "day":      "<exact day from the list above, e.g. 'Saturday 30 May'>",
  "time":     "<HH:MM UK time, as listed above>",
  "result":   null,
  "homeWin":  <integer 0-100>,
  "draw":     <integer 0-100>,
  "awayWin":  <integer 0-100>,
  "verdict":  "<Low|Likely|Strong>",
  "fairOdds": "<decimal odds range for the leading outcome, e.g. '2.10-2.30'>",
  "homeForm": "<5 W/D/L space-separated, oldest first, e.g. 'W W L D L'>",
  "awayForm": "<same format>",
  "factors": {{
    "formBalance":   {{ "score": <0-100>, "detail": "<one sentence>" }},
    "momentum":      {{ "score": <0-100>, "detail": "<one sentence>" }},
    "headToHead":    {{ "score": <0-100>, "detail": "<one sentence>" }},
    "goalTendency":  {{ "score": <0-100>, "detail": "<one sentence>" }},
    "leagueContext": {{ "score": <0-100>, "detail": "<one sentence>" }}
  }},
  "teamNews": {{
    "home": [{{ "tag": "<out|doubt|key>", "text": "<Player — short reason>" }}],
    "away": [{{ "tag": "<out|doubt|key>", "text": "<Player — short reason>" }}]
  }},
  "context":  "<2-4 sentence tactical / motivational paragraph with real player names>",
  "summary":  "<2-3 sentence summary, real specifics not generic football tropes>"
}}

RULES:
- homeWin + draw + awayWin MUST sum to exactly 100.
- verdict: Strong if leading outcome ≥65%, Likely if 50-64%, Low if <50%.
- If news is thin or contradictory, set verdict to Low and probabilities
  close to 33/34/33. Do not pad with generic phrases.
- 'tag' field MUST be exactly one of: out | doubt | key
- 'out' = ruled out, 'doubt' = uncertain, 'key' = important player to watch.
- For 'key' players in international tournaments, include their tournament goal/assist tally where known (e.g. "Mbappé — 3 goals this World Cup", "Saka — 2 goals, 1 assist this tournament").
- Form string is OLDEST → NEWEST (5 results, single space between each W/D/L).
- Use real player names from your web search — no placeholders.

If your response would be too long, return as many complete fixtures as you can
in one array. I'll ask you to continue with the rest after.

---

# Canonical team names

Use these strings EXACTLY in the home / away fields. Variants like
'Paris Saint-Germain' (instead of 'PSG') or 'Manchester United' (instead
of 'Man United') will cause the apply step to fail.

{chr(10).join(team_list_lines)}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(prompt)


if __name__ == "__main__":
    main()
