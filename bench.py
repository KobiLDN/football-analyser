"""
Model benchmark harness for the Football Analyser research pipeline.

Compares LLMs on the SAME cached news input so the test is fair.
Scores objective metrics (JSON validity, sum=100, wrong-fixture
contamination, fictional scoreline, schema completeness, speed).

Usage:
  1. Make sure LM Studio is running with ONE model loaded.
  2. python bench.py --model "google/gemma-4-e4b"
     (run once per model, swapping the model in LM Studio between runs)
  3. Or: python bench.py --all   (pauses and prompts you to swap models)

News is fetched ONCE and cached to bench_news_cache.json so every
model sees identical input. Delete that file to refresh the news.

Results are appended to bench_results.md as a scorecard table.
"""

import argparse
import json
import os
import re
import time

import requests

from agent import fetch_news, build_prompt, parse_json, team_tokens

LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
NEWS_CACHE   = "bench_news_cache.json"
RESULTS_FILE = "bench_results.md"

# Exact LM Studio API model IDs. Correct these to match your LM Studio
# (API tab → "model" field). GPT-OSS id is a guess — fix if wrong.
MODELS = [
    "google/gemma-4-e4b",
    "qwen/qwen3.5-9b",
    "qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2",
    "openai/gpt-oss-20b",
    "deepseek/deepseek-r1-0528-qwen3-8b",
]

# Representative test set — covers the hard cases found in the deep dive.
# (home, away, competition)
TEST_FIXTURES = [
    ("Liverpool",              "Brentford",  "Premier League"),  # clean
    ("Nottingham",             "Bournemouth","Premier League"),  # contamination-prone
    ("Brighton & Hove Albion", "Man United", "Premier League"),  # alias + ambiguous club
    ("Burnley",                "Wolverhampton","Premier League"),# sparse news
    ("Chelsea",                "Tottenham",  "Premier League"),  # heavy injury news
]


def get_cached_news():
    """Fetch news once per fixture and cache it so all models see the
    same input. Returns {"home|away": [articles]}."""
    if os.path.exists(NEWS_CACHE):
        with open(NEWS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("No news cache — fetching once for all test fixtures...")
    cache = {}
    for home, away, _ in TEST_FIXTURES:
        key = f"{home}|{away}"
        print(f"  fetching {home} vs {away}...")
        cache[key] = fetch_news(home, away)
    with open(NEWS_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"Cached to {NEWS_CACHE}\n")
    return cache


def call_model(model, prompt, timeout=240):
    resp = requests.post(LMSTUDIO_URL, json={
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a football analyst. Return only valid JSON — no markdown, no code fences."},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 10000,
    }, timeout=timeout)
    resp.raise_for_status()
    msg = resp.json()["choices"][0]["message"]
    return msg.get("content", "").strip() or msg.get("reasoning_content", "").strip()


FICTION_RE = re.compile(r"\b\d\s*[-–]\s*\d\b")


def score_fixture(model, home, away, competition, articles):
    """Run one model on one fixture, return a metrics dict."""
    prompt = build_prompt(home, away, competition, articles)
    metrics = {
        "fixture": f"{home} vs {away}",
        "parsed_first_try": False,
        "attempts": 0,
        "sum100": False,
        "both_team_ok": False,
        "no_fiction": False,
        "schema_complete": False,
        "seconds": 0.0,
        "context_excerpt": "",
        "error": "",
    }

    analysis = None
    t0 = time.time()
    for attempt in (1, 2):
        metrics["attempts"] = attempt
        try:
            analysis = parse_json(call_model(model, prompt))
            if attempt == 1:
                metrics["parsed_first_try"] = True
            break
        except Exception as e:
            metrics["error"] = str(e)[:120]
            analysis = None
    metrics["seconds"] = round(time.time() - t0, 1)

    if analysis is None:
        return metrics

    # sum to 100
    try:
        s = analysis["homeWin"] + analysis["draw"] + analysis["awayWin"]
        metrics["sum100"] = (s == 100)
    except Exception:
        pass

    # both-team mention (wrong-fixture contamination check)
    blob = (str(analysis.get("context", "")) + " " +
            str(analysis.get("summary", ""))).lower()
    h_ok = any(t in blob for t in team_tokens(home))
    a_ok = any(t in blob for t in team_tokens(away))
    metrics["both_team_ok"] = h_ok and a_ok

    # fictional scoreline in summary (these fixtures are all unplayed)
    metrics["no_fiction"] = not bool(FICTION_RE.search(
        str(analysis.get("summary", ""))))

    # schema completeness
    try:
        f = analysis["factors"]
        keys = ["formBalance", "momentum", "headToHead",
                "goalTendency", "leagueContext"]
        metrics["schema_complete"] = all(
            isinstance(f.get(k), dict) and "score" in f[k] and "detail" in f[k]
            for k in keys)
    except Exception:
        pass

    metrics["context_excerpt"] = str(analysis.get("context", ""))[:180]
    return metrics


def bench_model(model, news):
    print(f"\n=== Benchmarking: {model} ===")
    rows = []
    for home, away, comp in TEST_FIXTURES:
        articles = news.get(f"{home}|{away}", [])
        print(f"  [{home} vs {away}] running...", end=" ", flush=True)
        m = score_fixture(model, home, away, comp, articles)
        print(f"{m['seconds']}s  "
              f"json={'Y' if m['parsed_first_try'] else 'N'} "
              f"sum100={'Y' if m['sum100'] else 'N'} "
              f"both={'Y' if m['both_team_ok'] else 'N'} "
              f"fict={'OK' if m['no_fiction'] else 'BAD'}")
        rows.append(m)
    return rows


def write_results(model, rows):
    n = len(rows)
    def pct(key):
        return f"{sum(1 for r in rows if r[key])}/{n}"
    avg_time = round(sum(r["seconds"] for r in rows) / n, 1)

    line = (f"| {model} | {pct('parsed_first_try')} | {pct('sum100')} | "
            f"{pct('both_team_ok')} | {pct('no_fiction')} | "
            f"{pct('schema_complete')} | {avg_time}s |")

    header = (
        "# Model Benchmark Results\n\n"
        f"Test set: {len(TEST_FIXTURES)} fixtures, identical cached news.\n\n"
        "| Model | JSON 1st try | Sum=100 | Both teams | No fiction | "
        "Schema | Avg time |\n"
        "|---|---|---|---|---|---|---|\n"
    )

    existing = ""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            existing = f.read()
    if not existing:
        existing = header

    # Append the model row before the spot-check section (or at end)
    if "## Context spot-checks" in existing:
        existing = existing.replace("## Context spot-checks",
                                    line + "\n\n## Context spot-checks")
    else:
        existing = existing.rstrip() + "\n" + line + "\n\n## Context spot-checks\n"

    # Add spot-check excerpts
    existing += f"\n**{model}**\n\n"
    for r in rows:
        existing += f"- *{r['fixture']}*: {r['context_excerpt']}...\n"

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(existing)
    print(f"\nResults written to {RESULTS_FILE}")
    print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="single model id to benchmark")
    ap.add_argument("--all", action="store_true",
                    help="loop all MODELS, pausing to swap in LM Studio")
    args = ap.parse_args()

    news = get_cached_news()

    if args.all:
        for model in MODELS:
            input(f"\n>>> Load '{model}' in LM Studio, then press Enter...")
            rows = bench_model(model, news)
            write_results(model, rows)
        print("\nAll models benchmarked.")
    else:
        model = args.model or MODELS[0]
        rows = bench_model(model, news)
        write_results(model, rows)


if __name__ == "__main__":
    main()
