# Football Analyser

A football match analysis tool with AI-powered home/draw/away win probabilities and deep-research per fixture across European leagues and competitions.

## Live site

https://kobildn.github.io/football-analyser/

## What it covers

Eight competitions: Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, Europa League, Conference League.

Each fixture is annotated with:

- Recent form and league position
- Confirmed team news (injuries, suspensions, key players)
- Tactical context and motivation
- Head-to-head history
- Home / draw / away win probabilities and confidence verdict (Low / Likely / Strong)
- Last-5 form dots per team (W/D/L) sourced from Understat xG data
- Fair odds estimate, plus book odds and edge calculation when available

## Updating each gameweek

Fixtures are fetched automatically via the API through the `.github/workflows/fetch-fixtures.yml` GitHub Action — do not add fixtures manually. Deep research is then populated by `agent.py` (see [Local AI research pipeline](#local-ai-research-pipeline) below) or by `refresh_today.bat` for game-day updates.

## Fixture verification

A GitHub Action (`.github/workflows/verify-fixtures.yml`) runs daily and on push, comparing the `LEAGUES` array against ground truth from [football-data.org](https://www.football-data.org/). **It now auto-corrects** date/time mismatches by patching `index.html` directly and committing the fix — only genuinely missing fixtures (wrong matchups, no API result) still require manual review.

Requires `FOOTBALL_DATA_API_KEY` to be set as a repo secret.

## Marking results

A second GitHub Action (`.github/workflows/mark-results.yml`) runs at **5pm BST on Thursday–Sunday** and at **11pm BST every day**, queries football-data.org for finished matches, and writes scorelines into the `result` field in the `LEAGUES` array — then auto-commits as `github-actions[bot]`. The toggle in the sidebar's Display section lets you flip between "upcoming only" and "include past fixtures" so you can see final scores (and draw tags) once they're populated.

Manual fallback: edit the fixture object directly to set `result:` if the workflow misses one.

## Auto-fetching fixtures

A third GitHub Action (`.github/workflows/fetch-fixtures.yml`) runs every Monday at 08:00 UTC and inserts stub fixtures for the coming week. Stubs have placeholder analysis (all factors set to 50, verdict "Low") — deep research is added manually afterwards. **Re-fetch preserves** any existing `teamNews`, `context`, and `bookOdds` on fixtures the script re-writes. Trigger it on demand via **Actions → Auto-fetch fixtures → Run workflow** (supports an optional `days_ahead` input, default 8).

## Local AI research pipeline

`agent.py` populates stub fixtures with deep research locally — no external API costs. It uses:

- **LM Studio** serving a local LLM (winner: `qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2`)
- **SearXNG** as a self-hosted meta-search for live news
- **Understat** via the `understatapi` Python package for xG and form data

Three entry points:

- **`run_agent.bat`** — researches every `Pending deep research.` stub in `index.html`. Use after a Monday fetch when there are a lot of new stubs.
- **`reset_stubs.bat`** — resets all unplayed fixtures back to stubs (useful before a full re-research with an updated model or prompt).
- **`refresh_today.bat [days]`** — targeted reset of fixtures kicking off within N days (default 1 = today), then auto-runs the agent. Use on matchday morning to incorporate the latest team news and injury updates without re-researching the entire week (~3–5 min vs ~15+ min full).

The pipeline is hardened against common LLM failure modes: a scored relevance filter prioritises articles mentioning *both* fixture teams (preventing wrong-opponent contamination), the prompt forbids inventing scorelines or guessing personnel, and a post-validation step retries any analysis that doesn't mention both teams. Team-name aliases (in `agent.py` `UNDERSTAT_ALIASES`) handle long club names like *Brighton & Hove Albion* → *Brighton*.

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
