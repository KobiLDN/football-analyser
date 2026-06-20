"""
Apply researched fixture analysis from research.json into index.html.

Workflow:
  1. OpenRouter (or manual paste) produces research.json
  2. Double-click apply_research.bat (or run `python apply_research.py`)
  3. This script:
       - Validates the JSON
       - Finds the matching fixture in index.html (by home + away + day)
       - Replaces just that fixture's block
       - git add / commit / push to main (live)
       - renames research.json -> research.json.applied

Flags:
  --no-push       Edit index.html only; skip the commit + push step
  --dry-run       Show what would change, don't write anything
"""

import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(REPO_ROOT, "index.html")
JSON_FILE = os.path.join(REPO_ROOT, "research.json")


def esc(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def fmt_team_news(items):
    if not items:
        return "[]"
    lines = [
        f"              {{ tag: '{esc(i['tag'])}', text: '{esc(i['text'])}' }}"
        for i in items
    ]
    return "[\n" + ",\n".join(lines) + "\n            ]"


def build_block(d):
    f = d["factors"]
    home_news = fmt_team_news(d["teamNews"]["home"])
    away_news = fmt_team_news(d["teamNews"]["away"])
    result_str = "null" if d.get("result") is None else f"'{esc(d['result'])}'"
    home_form_line = f"\n        homeForm: '{esc(d['homeForm'])}',"  if d.get("homeForm") else ""
    away_form_line = f"\n        awayForm: '{esc(d['awayForm'])}',"  if d.get("awayForm") else ""

    return f"""{{
        day: '{esc(d['day'])}',
        home: '{esc(d['home'])}', away: '{esc(d['away'])}', time: '{d['time']}',
        result: {result_str}, homeWin: {d['homeWin']}, draw: {d['draw']}, awayWin: {d['awayWin']}, verdict: '{esc(d['verdict'])}', fairOdds: '{esc(d['fairOdds'])}',{home_form_line}{away_form_line}
        factors: {{
          formBalance:   {{ score: {f['formBalance']['score']}, detail: '{esc(f['formBalance']['detail'])}' }},
          momentum:      {{ score: {f['momentum']['score']}, detail: '{esc(f['momentum']['detail'])}' }},
          goalTendency:  {{ score: {f['goalTendency']['score']}, detail: '{esc(f['goalTendency']['detail'])}' }},
          leagueContext: {{ score: {f['leagueContext']['score']}, detail: '{esc(f['leagueContext']['detail'])}' }}
        }},
        teamNews: {{
          home: {home_news},
          away: {away_news}
        }},
        context: '{esc(d['context'])}',
        summary: '{esc(d['summary'])}'
      }}"""


def validate(d):
    required = ["home", "away", "day", "time", "homeWin", "draw", "awayWin",
                "verdict", "fairOdds", "factors", "teamNews", "context", "summary"]
    for k in required:
        if k not in d:
            return f"Missing field: '{k}'"
    s = d["homeWin"] + d["draw"] + d["awayWin"]
    if s != 100:
        return f"homeWin + draw + awayWin must equal 100 (got {s})"
    if d["verdict"] not in ("Low", "Likely", "Strong"):
        return f"verdict must be Low | Likely | Strong (got '{d['verdict']}')"
    required_factors = ["formBalance", "momentum", "goalTendency", "leagueContext"]
    for k in required_factors:
        if k not in d["factors"]:
            return f"Missing factor: '{k}'"
        f = d["factors"][k]
        if "score" not in f or "detail" not in f:
            return f"Factor '{k}' missing score or detail"
    if "home" not in d["teamNews"] or "away" not in d["teamNews"]:
        return "teamNews must have 'home' and 'away' arrays"
    for side in ("home", "away"):
        for i, item in enumerate(d["teamNews"][side]):
            if "tag" not in item or "text" not in item:
                return f"teamNews.{side}[{i}] missing tag or text"
            if item["tag"] not in ("out", "doubt", "key"):
                return f"teamNews.{side}[{i}].tag must be out | doubt | key (got '{item['tag']}')"
    return None


def find_fixture_block(html, home, away, day):
    """Return (start_idx, end_idx) of the fixture object literal matching
    all three of home + away + day. Returns (None, None) if not found."""
    pat = re.compile(
        rf"day:\s*'{re.escape(day)}'[\s\S]{{0,400}}?home:\s*'{re.escape(home)}',\s*away:\s*'{re.escape(away)}'"
    )
    m = pat.search(html)
    if not m:
        return None, None
    start = html.rfind('{', 0, m.start())
    depth = 0
    end = start
    for i in range(start, len(html)):
        if html[i] == '{':
            depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return start, end


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def _autodetect_input():
    """If research.json doesn't exist or a newer deepseek_json_*.json file
    sits alongside it, return the path to use. DeepSeek's web app names
    downloads like 'deepseek_json_20260525_8a6400.json', so once you drop
    one in the repo folder the script picks it up automatically — no
    rename needed."""
    import glob
    candidates = sorted(
        glob.glob(os.path.join(REPO_ROOT, "deepseek_json_*.json")),
        key=os.path.getmtime,
        reverse=True,
    )
    if not candidates:
        return JSON_FILE if os.path.exists(JSON_FILE) else None
    newest_ds = candidates[0]
    # Prefer the deepseek file if research.json doesn't exist, or if the
    # deepseek file is newer than research.json (you just downloaded it).
    if not os.path.exists(JSON_FILE):
        return newest_ds
    if os.path.getmtime(newest_ds) > os.path.getmtime(JSON_FILE):
        return newest_ds
    return JSON_FILE


def main():
    no_push = "--no-push" in sys.argv
    dry_run = "--dry-run" in sys.argv

    input_path = _autodetect_input()
    if input_path is None:
        print(f"X No input found.")
        print(f"  Either paste DeepSeek's JSON into research.json,")
        print(f"  or drop a deepseek_json_*.json file in the repo folder.")
        sys.exit(1)
    if input_path != JSON_FILE:
        print(f"-> Using {os.path.basename(input_path)} (newer than research.json)")

    with open(input_path, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError as e:
            print(f"X {os.path.basename(input_path)} is not valid JSON: {e}")
            sys.exit(1)

    # Accept either a single fixture object OR an array of them
    fixtures = raw if isinstance(raw, list) else [raw]
    if not fixtures:
        print(f"X research.json is an empty array.")
        sys.exit(1)

    # Validate everything BEFORE touching the file (atomic). If any
    # fixture fails validation, we abort with no side effects.
    for i, d in enumerate(fixtures):
        err = validate(d)
        if err:
            label = f"fixtures[{i}]" if isinstance(raw, list) else "fixture"
            print(f"X Validation failed for {label}: {err}")
            sys.exit(1)

    print(f"Applying {len(fixtures)} fixture{'s' if len(fixtures) != 1 else ''}:")
    for d in fixtures:
        print(f"  - {d['home']} vs {d['away']} ({d['day']})  "
              f"H {d['homeWin']}/D {d['draw']}/A {d['awayWin']} {d['verdict']}  "
              f"news {len(d['teamNews']['home'])}+{len(d['teamNews']['away'])}")

    # Sync with origin first so we don't push a stale index.html on top
    # of bot commits (auto-mark, daily WC fetch, verify auto-correct).
    if not no_push and not dry_run:
        rc, current_branch, _ = git("branch", "--show-current")
        print(f"-> Syncing local '{current_branch}' with origin...")
        rc, out, err = git("pull", "--rebase", "origin", current_branch)
        if rc != 0:
            print(f"X Pull --rebase failed: {err or out}")
            print(f"  Resolve manually and re-run.")
            sys.exit(1)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Pre-flight: confirm every fixture exists in index.html before any
    # edits. If any are missing, abort.
    missing = []
    for d in fixtures:
        start, end = find_fixture_block(html, d["home"], d["away"], d["day"])
        if start is None:
            missing.append(d)
    if missing:
        print(f"X {len(missing)} fixture(s) not found in index.html:")
        for d in missing:
            print(f"  - day='{d['day']}', home='{d['home']}', away='{d['away']}'")
        print(f"  Check the spelling matches the existing fixtures exactly.")
        sys.exit(1)

    if dry_run:
        for d in fixtures:
            start, end = find_fixture_block(html, d["home"], d["away"], d["day"])
            print(f"\n--- DRY RUN: would replace {d['home']} vs {d['away']} ---")
            print(html[start:end])
            print(f"\n--- with: ---")
            print(build_block(d))
        return

    # Replace each fixture in-place. Re-find on each iteration because
    # the offsets shift after the previous replacement.
    for d in fixtures:
        start, end = find_fixture_block(html, d["home"], d["away"], d["day"])
        html = html[:start] + build_block(d) + html[end:]

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK Replaced {len(fixtures)} fixture block(s) in index.html")

    if no_push:
        print("(--no-push given; not committing)")
        return

    rc, current_branch, _ = git("branch", "--show-current")
    if not current_branch:
        print(f"X Could not detect current branch; aborting push.")
        sys.exit(1)

    print(f"-> Committing on '{current_branch}'...")
    git("add", "index.html")
    if len(fixtures) == 1:
        d0 = fixtures[0]
        msg = f"data: research-backfill {d0['home']} vs {d0['away']} ({d0['day']})"
    else:
        first = fixtures[0]
        msg = (f"data: research-backfill {len(fixtures)} fixtures "
               f"({first['home']} vs {first['away']}, +{len(fixtures)-1} more)")
    rc, out, err = git("commit", "-m", msg)
    if rc != 0:
        if "nothing to commit" in (out + err).lower():
            print("(no changes to commit — file already matches the research)")
            # Still archive: the data has already been applied to the
            # repo, so we don't want to keep re-processing this file.
            _archive_research_json(input_path)
            return
        print(f"X Commit failed: {err or out}")
        sys.exit(1)

    print(f"-> Pushing to origin/{current_branch}...")
    rc, out, err = git("push", "origin", current_branch)
    if rc != 0:
        print(f"X Push failed: {err or out}")
        sys.exit(1)
    print(f"OK Pushed to main. Live in ~1 min.")
    _archive_research_json(input_path)


def _archive_research_json(path):
    """Rename whichever input file we just applied so it can't be
    accidentally re-applied. For deepseek_json_*.json files, rename to
    *.applied alongside the original; for research.json, same idea."""
    if not path or not os.path.exists(path):
        return
    archive = path + ".applied"
    if os.path.exists(archive):
        os.remove(archive)
    os.rename(path, archive)
    print(f"-> Archived {os.path.basename(path)} -> {os.path.basename(archive)}")


if __name__ == "__main__":
    main()
