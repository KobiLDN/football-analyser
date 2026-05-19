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

Fixtures are now fetched automatically via the API through the `.github/workflows/fetch-fixtures.yml` GitHub Action. Do not add fixtures manually.

Once fixtures are fetched, you can run AI tools to add deep research:

```
Research the upcoming gameweek fixtures listed in index.html. For each fixture:
- Search for team news, injuries, form
- Check H2H and motivation context
- Update the factors and teamNews objects
- Commit and push
```

## Fixture verification

A GitHub Action (`.github/workflows/verify-fixtures.yml`) runs daily and on push, comparing the `LEAGUES` array against ground truth from [football-data.org](https://www.football-data.org/). It flags wrong dates, wrong matchups, and missing fixtures so they can be corrected before kick-off.

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

Run `run_agent.bat` to research all `Pending deep research.` stubs in `index.html`. Run `reset_stubs.bat` first if you want to re-research already-populated fixtures.

The pipeline is hardened against common LLM failure modes: a scored relevance filter prioritises articles mentioning *both* fixture teams (preventing wrong-opponent contamination), the prompt forbids inventing scorelines or guessing personnel, and a post-validation step retries any analysis that doesn't mention both teams.

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
