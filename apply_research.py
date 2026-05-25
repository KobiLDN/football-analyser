"""
Apply DeepSeek-researched fixture analysis from research.json into index.html.

Workflow:
  1. Ask DeepSeek (with web search) to research a fixture using the prompt
     in research.template.json. It returns a JSON object matching the
     fixture schema.
  2. Paste that JSON into ./research.json
  3. Double-click apply_research.bat (or run `python apply_research.py`)
  4. This script:
       - Validates the JSON
       - Finds the matching fixture in index.html (by home + away + day)
       - Replaces just that fixture's block
       - git add / commit / push to the current branch (usually dev)

  After that, merge dev -> main yourself the usual way when you're ready
  to ship to live.

By default the script:
  1. git pull --rebase origin dev   (catch any bot commits)
  2. edits index.html in place
  3. commits + pushes to dev
  4. checks out main, merges dev, pushes main (live)
  5. switches back to dev
  6. renames research.json -> research.json.applied so it won't get
     accidentally re-applied next run

Flags:
  --no-push       Edit index.html only; skip the commit + push step
  --dev-only      Stop after pushing dev (don't merge to main / live)
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
          headToHead:    {{ score: {f['headToHead']['score']}, detail: '{esc(f['headToHead']['detail'])}' }},
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
    required_factors = ["formBalance", "momentum", "headToHead", "goalTendency", "leagueContext"]
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


def main():
    no_push = "--no-push" in sys.argv
    dev_only = "--dev-only" in sys.argv
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(JSON_FILE):
        print(f"X {JSON_FILE} not found.")
        print(f"  Paste DeepSeek's JSON into research.json, then re-run.")
        sys.exit(1)

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"X research.json is not valid JSON: {e}")
            sys.exit(1)

    err = validate(data)
    if err:
        print(f"X Validation failed: {err}")
        sys.exit(1)

    print(f"Applying: {data['home']} vs {data['away']} ({data['day']})")
    print(f"  probs:  H {data['homeWin']}% / D {data['draw']}% / A {data['awayWin']}%  -  {data['verdict']}")
    print(f"  news:   {len(data['teamNews']['home'])} home + {len(data['teamNews']['away'])} away items")

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

    start, end = find_fixture_block(html, data["home"], data["away"], data["day"])
    if start is None:
        print(f"X Fixture not found in index.html.")
        print(f"  Looking for: day='{data['day']}', home='{data['home']}', away='{data['away']}'")
        print(f"  Check the spelling matches the existing fixture exactly.")
        sys.exit(1)

    new_block = build_block(data)

    if dry_run:
        print(f"\n--- DRY RUN: would replace the following block ---")
        print(html[start:end])
        print(f"\n--- with: ---")
        print(new_block)
        return

    html2 = html[:start] + new_block + html[end:]
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html2)

    print(f"OK Replaced fixture block in index.html")

    if no_push:
        print("(--no-push given; not committing)")
        return

    rc, current_branch, _ = git("branch", "--show-current")
    if not current_branch:
        print(f"X Could not detect current branch; aborting push.")
        sys.exit(1)

    print(f"-> Committing on '{current_branch}'...")
    git("add", "index.html")
    msg = f"data: research-backfill {data['home']} vs {data['away']} ({data['day']})"
    rc, out, err = git("commit", "-m", msg)
    if rc != 0:
        if "nothing to commit" in (out + err).lower():
            print("(no changes to commit — file already matches the research)")
            return
        print(f"X Commit failed: {err or out}")
        sys.exit(1)

    print(f"-> Pushing to origin/{current_branch}...")
    rc, out, err = git("push", "origin", current_branch)
    if rc != 0:
        print(f"X Push failed: {err or out}")
        sys.exit(1)
    print(f"OK Pushed to dev.")

    # Stop here if user only wanted dev (staging-only mode)
    if dev_only:
        print(f"(--dev-only given; not promoting to main / live)")
        _archive_research_json()
        return

    # If we're not on dev, skip the dev→main promotion (already on main, etc.)
    if current_branch != "dev":
        print(f"(current branch is '{current_branch}', not dev — skipping main merge)")
        _archive_research_json()
        return

    # Promote to main / live
    print(f"-> Promoting to main (live)...")
    rc, out, err = git("checkout", "main")
    if rc != 0:
        print(f"X Could not checkout main: {err or out}")
        sys.exit(1)

    rc, out, err = git("pull", "--ff-only", "origin", "main")
    if rc != 0:
        # Try non-FF pull-rebase in case main has diverged
        rc, out, err = git("pull", "--rebase", "origin", "main")
        if rc != 0:
            print(f"X Could not pull main: {err or out}")
            git("checkout", "dev")
            sys.exit(1)

    msg = f"Merge dev: research-backfill {data['home']} vs {data['away']}"
    rc, out, err = git("merge", "dev", "--no-ff", "-m", msg)
    if rc != 0:
        print(f"X Merge conflict on main. Resolve manually then push:")
        print(f"  git push origin main; git checkout dev")
        sys.exit(1)

    rc, out, err = git("push", "origin", "main")
    if rc != 0:
        print(f"X Push main failed: {err or out}")
        git("checkout", "dev")
        sys.exit(1)
    print(f"OK Pushed to main. Live in ~1 min.")

    # Back to dev for the next session
    git("checkout", "dev")
    _archive_research_json()


def _archive_research_json():
    """Rename research.json so it can't accidentally be re-applied."""
    if not os.path.exists(JSON_FILE):
        return
    archive = JSON_FILE + ".applied"
    # If a previous .applied exists, overwrite
    if os.path.exists(archive):
        os.remove(archive)
    os.rename(JSON_FILE, archive)
    print(f"-> Archived research.json -> research.json.applied")


if __name__ == "__main__":
    main()
