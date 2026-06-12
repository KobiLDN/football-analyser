"""
auto_research.py — automated fixture research via OpenRouter.

Replaces the manual DeepSeek copy-paste loop with a single command:
  python auto_research.py   (or double-click auto_research.bat)

Pipeline:
  1. Runs make_fixtures_list.py to find stubs + build the research prompt
  2. Sends the prompt to OpenRouter (deepseek:online — live web search)
  3. Parses the returned JSON array
  4. Writes research.json
  5. Calls apply_research.py to commit dev → main → live

Flags:
  --league <id>    filter by league: pl, laliga, seriea, bundesliga,
                   ligue1, ucl, uel, uecl, worldcup
  --days <N>       fixtures kicking off within N days (default 7; -1 = all)
  --max <N>        cap at N fixtures per run (default 20)
  --offset <N>     skip first N — use for batching when >20 stubs exist
  --model <id>     OpenRouter model (default: deepseek/deepseek-r1-0528:online)
  --no-apply       write research.json but stop before pushing live
  --dry-run        print the prompt, skip the API call

Requires:
  OPENROUTER_API_KEY — set as an environment variable, or add a line
  OPENROUTER_API_KEY=sk-or-... to a .env file in this folder.
"""

import argparse
import json
import os
import re
import subprocess
import sys

import requests

REPO_ROOT      = os.path.dirname(os.path.abspath(__file__))
HTML_FILE      = os.path.join(REPO_ROOT, "index.html")
OUT_FILE       = os.path.join(REPO_ROOT, "research.json")
PROMPT_FILE    = os.path.join(REPO_ROOT, "fixtures_research_needed_prompt.txt")
RAW_DUMP_FILE  = os.path.join(REPO_ROOT, "openrouter_raw.txt")

DEFAULT_MODEL  = "deepseek/deepseek-r1-0528:online"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# ─── env / config ─────────────────────────────────────────────────────────────

def load_env_file():
    """Load key=value pairs from .env in the repo root into os.environ."""
    env_path = os.path.join(REPO_ROOT, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


# ─── fixture list + prompt ────────────────────────────────────────────────────

def build_fixture_list(fixture_args):
    """Run make_fixtures_list.py, return the fixtures it found (from fixtures.json)."""
    fixtures_path = os.path.join(REPO_ROOT, "fixtures.json")
    # Remove stale fixtures.json first so we can tell if make_fixtures_list
    # actually found anything (it doesn't write the file when there's no match).
    if os.path.exists(fixtures_path):
        os.remove(fixtures_path)

    cmd = [sys.executable, os.path.join(REPO_ROOT, "make_fixtures_list.py"), *fixture_args]
    rc = subprocess.run(cmd, cwd=REPO_ROOT)
    if rc.returncode != 0:
        print("X make_fixtures_list.py failed — aborting.")
        sys.exit(1)

    if not os.path.exists(fixtures_path):
        return []
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)


def read_prompt():
    if not os.path.exists(PROMPT_FILE):
        print(f"X {PROMPT_FILE} not found — make_fixtures_list.py should have created it.")
        sys.exit(1)
    with open(PROMPT_FILE, encoding="utf-8") as f:
        return f.read()


# ─── OpenRouter call ──────────────────────────────────────────────────────────

def call_openrouter(prompt, model, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://kobildn.github.io/football-analyser/",
        "X-Title":       "Football Analyser",
    }
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a football analyst with access to live web search. "
                    "Return only a valid JSON array — no markdown, no code fences, no prose."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    print(f"-> Calling {model} ...")
    resp = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    # Surface usage if available
    usage = data.get("usage", {})
    if usage:
        print(f"   tokens — prompt: {usage.get('prompt_tokens','?')}  "
              f"completion: {usage.get('completion_tokens','?')}")
    return data["choices"][0]["message"]["content"].strip()


# ─── response parsing ─────────────────────────────────────────────────────────

def parse_json_response(raw):
    """Strip markdown fences / thinking tags and return a list of fixture dicts."""
    # DeepSeek R1 wraps reasoning in <think>…</think>
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    # Strip markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw.strip())
    # Find the outermost JSON array or object
    m = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw)
    if m:
        raw = m.group(0)
    data = json.loads(raw.strip())
    return data if isinstance(data, list) else [data]


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    load_env_file()

    ap = argparse.ArgumentParser(description="Auto-research fixtures via OpenRouter")
    ap.add_argument("--league",   default=None,
                    help="filter by league id (pl, laliga, worldcup, ...)")
    ap.add_argument("--days",     type=int, default=7,
                    help="fixtures within N days (default 7; -1 = no filter)")
    ap.add_argument("--max",      type=int, default=20, dest="max_n",
                    help="cap at N fixtures (default 20)")
    ap.add_argument("--offset",   type=int, default=0,
                    help="skip first N fixtures (for batching)")
    ap.add_argument("--model",    default=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
                    help=f"OpenRouter model ID (default: {DEFAULT_MODEL})")
    ap.add_argument("--no-apply", action="store_true",
                    help="write research.json but don't push live")
    ap.add_argument("--dry-run",  action="store_true",
                    help="show prompt, skip API call")
    args = ap.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key and not args.dry_run:
        print("X OPENROUTER_API_KEY is not set.")
        print("  Either export it in your shell, or add it to a .env file:")
        print("    OPENROUTER_API_KEY=sk-or-...")
        sys.exit(1)

    # Build args for make_fixtures_list.py
    fixture_args = [
        "--stubs-only",
        "--days",  str(args.days),
        "--max",   str(args.max_n),
    ]
    if args.league:
        fixture_args += ["--league", args.league]
    if args.offset:
        fixture_args += ["--offset", str(args.offset)]

    print("-> Building fixture list...")
    fixtures = build_fixture_list(fixture_args)
    if not fixtures:
        print("No stub fixtures matched — nothing to research.")
        return

    print(f"\n-> {len(fixtures)} fixture(s) queued:")
    for fx in fixtures:
        print(f"   {fx['day']:<24} {fx['time']}  "
              f"{fx['home']} vs {fx['away']}  [{fx['competition']}]")

    prompt = read_prompt()

    if args.dry_run:
        print(f"\n--- PROMPT ({len(prompt)} chars) ---")
        print(prompt[:3000])
        if len(prompt) > 3000:
            print(f"... [{len(prompt) - 3000} more chars]")
        return

    # Call the API
    try:
        raw = call_openrouter(prompt, args.model, api_key)
    except requests.HTTPError as e:
        print(f"X OpenRouter HTTP error: {e}")
        print(f"  Response: {e.response.text[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"X OpenRouter call failed: {e}")
        sys.exit(1)

    print(f"-> Response received ({len(raw)} chars)")

    # Parse
    try:
        data = parse_json_response(raw)
    except Exception as e:
        print(f"X Failed to parse JSON: {e}")
        with open(RAW_DUMP_FILE, "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"  Raw response saved to {os.path.basename(RAW_DUMP_FILE)} — inspect and fix manually.")
        sys.exit(1)

    print(f"-> Parsed {len(data)} fixture(s) from response")

    if not data:
        print("WARNING: model returned an empty array — no fixtures to apply.")
        with open(RAW_DUMP_FILE, "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"  Raw response saved to {os.path.basename(RAW_DUMP_FILE)} for inspection.")
        return

    for d in data:
        home = d.get("home", "?")
        away = d.get("away", "?")
        hw   = d.get("homeWin", "?")
        dr   = d.get("draw", "?")
        aw   = d.get("awayWin", "?")
        v    = d.get("verdict", "?")
        print(f"   {home} vs {away}  H{hw}/D{dr}/A{aw}  {v}")

    # Write research.json
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n-> Wrote {os.path.basename(OUT_FILE)}")

    if args.no_apply:
        print("(--no-apply: stopping here. Run apply_research.bat to push live.)")
        return

    # Apply + push live
    print("-> Running apply_research.py ...")
    rc = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "apply_research.py")],
        cwd=REPO_ROOT,
    )
    if rc.returncode != 0:
        print("X apply_research.py failed — research.json is intact, fix and re-run apply_research.bat.")
        sys.exit(1)


if __name__ == "__main__":
    main()
