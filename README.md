# Football Analyser

A football match analysis tool with AI-powered home/draw/away win probabilities and deep-research per fixture across European leagues and competitions.

## Live site

https://kobildn.github.io/football-analyser/

## What it covers

Nine competitions: Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, Europa League, Conference League, and World Cup 2026.

Each fixture is annotated with:

- Recent form and league position
- Confirmed team news (injuries, suspensions, key players)
- Tactical context and motivation
- Head-to-head history
- Home / draw / away win probabilities and confidence verdict (Low / Likely / Strong)
- Last-5 form dots per team (W/D/L) sourced from Understat xG data
- Fair odds estimate, plus book odds and edge calculation when available

## Updating each gameweek

Fixtures are fetched automatically via the API through the `.github/workflows/fetch-fixtures.yml` GitHub Action — do not add fixtures manually. Deep research is then populated automatically by the `auto-research.yml` workflow (see [Automated research pipeline](#automated-research-pipeline) below), or locally via `refresh_today.bat` for game-day updates.

## Fixture verification

A GitHub Action (`.github/workflows/verify-fixtures.yml`) runs daily and on push, comparing the `LEAGUES` array against ground truth from [football-data.org](https://www.football-data.org/). **It now auto-corrects** date/time mismatches by patching `index.html` directly and committing the fix — only genuinely missing fixtures (wrong matchups, no API result) still require manual review.

Requires `FOOTBALL_DATA_API_KEY` to be set as a repo secret.

## Marking results

A second GitHub Action (`.github/workflows/mark-results.yml`) runs at **5pm BST on Thursday–Sunday**, **11pm BST daily**, **2am BST daily** (catches 22:00–23:00 kick-offs finishing after midnight), and **8am BST daily** (catches World Cup overnight kick-offs 00:00–05:00 BST), queries football-data.org for finished matches, and writes scorelines into the `result` field in the `LEAGUES` array — then auto-commits as `github-actions[bot]`. The toggle in the sidebar's Display section lets you flip between "upcoming only" and "include past fixtures" so you can see final scores (and draw tags) once they're populated.

Manual fallback: edit the fixture object directly to set `result:` if the workflow misses one.

## Auto-fetching fixtures

A third GitHub Action (`.github/workflows/fetch-fixtures.yml`) runs every Monday at 08:00 UTC and inserts stub fixtures for the coming week. Stubs have placeholder analysis (all factors set to 50, verdict "Low") — deep research is added automatically by the `auto-research.yml` workflow shortly after. **Re-fetch preserves** any existing `teamNews`, `context`, and `bookOdds` on fixtures the script re-writes. Trigger it on demand via **Actions → Auto-fetch fixtures → Run workflow** (supports an optional `days_ahead` input, default 8).

## Automated research pipeline

`.github/workflows/auto-research.yml` runs **daily at 11am BST** and also triggers automatically after `fetch-fixtures.yml` and `fetch-worldcup.yml` complete. It:

1. Runs `auto_research.py` which finds all stub fixtures and builds a research prompt
2. Calls **OpenRouter** (`deepseek/deepseek-r1-0528:online`) — live web search for team news, injuries, form, head-to-head
3. Parses the returned JSON array and writes `research.json`
4. Applies the research to `index.html` and commits direct to main

Requires `OPENROUTER_API_KEY` set as a GitHub Actions secret.

**Manual use:** double-click `auto_research.bat` to research stubs locally. Same flags as `make_fixtures.bat`:

```
auto_research.bat                           # all leagues, next 7 days
auto_research.bat --league worldcup         # World Cup only
auto_research.bat --days -1 --max 25        # all stubs, first batch of 25
auto_research.bat --days -1 --max 25 --offset 25   # second batch
auto_research.bat --no-apply                # write research.json only, don't push
```

**Game-day refresh:** `refresh_today.bat [days]` resets fixtures kicking off within N days back to stubs and re-researches them via OpenRouter (~3–5 min). Default window is 2 days (today + tomorrow). The nightly `refresh-tonight.yml` workflow does this automatically at midnight BST.

## Nightly fixture refresh

`.github/workflows/refresh-tonight.yml` runs every night at **midnight BST**. It resets fixtures kicking off today or tomorrow back to stubs, then re-researches them via OpenRouter — so late injury announcements, lineup leaks, or suspension confirmations are reflected before kickoff. Can also be triggered manually via **Actions → Midnight refresh → Run workflow** with an optional `days` input.

## International fixture intel

`team_intel.py` holds FIFA rankings and continental tournament history (World Cup, UEFA Euro, Copa América, AFCON, AFC Asian Cup, Gold Cup, OFC Nations Cup) for all 48 World Cup 2026 teams. This data is automatically injected into the research prompt for any international fixture, giving the model a calibrated baseline to work from instead of relying on web search alone.

## Model benchmarking

`bench.py` compares LLMs on identical cached news input and scores them on objective metrics: JSON validity, probabilities summing to 100, wrong-fixture contamination check, fictional-scoreline detection, schema completeness, and speed. Run `bench.bat` to sweep all configured models — results append to `bench_results.md`.

## Local development

Just open `index.html` in a browser. No build step, no dependencies.

## Multi-AI workflow (important)

If you use multiple AI tools (Cursor/Codex, Claude, ChatGPT, etc.), follow this on every session:

1. Read docs in this order before editing:
   - `AGENTS.md`
   - `CHANGELOG.md`
   - `FEATURES.md`
2. Pull latest changes first:
   - `git checkout main`
   - `git pull --rebase`
3. Make your changes.
4. Update `CHANGELOG.md` by **prepending** one new table row right under the header (**newest first**), with:
   - Date and time in **`YYYY-MM-DD HH:MM BST`**
   - AI name/tool
   - What changed and why (include primary file paths in backticks)
5. Update `FEATURES.md`:
   - Add shipped user-visible changes to **Done**
   - Add new ideas to **Backlog**
6. Commit with a clear AI-prefixed message, e.g.:
   - `ai-codex: improve odds-label readability`
   - `ai-claude: add fixture verification notes`

This keeps handoffs clean and prevents duplicate or conflicting edits.
