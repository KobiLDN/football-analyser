# Kanban

Football Analyser task board. Move cards left → right as work progresses.

---

## 🔲 Backlog

### Pipeline
- **Pre-commit schema validation** — run `node -e "loadLeagues(html)"` before commits to catch schema breakage (would have caught the v2.33 fetch-fixtures regression)
- **Scripts README** — one-line description per file: `agent.py`, `auto_research.py`, `apply_research.py`, `fetch-fixtures.js`, etc.
- **Discord / email webhook on workflow failures** — get pinged when `auto-mark`, `auto-fetch`, or `verify-fixtures` fails instead of discovering it by opening Actions
- **Schema migration helper** — automate retrofitting old fixtures when a new field is added (prevents v2.33-style cross-script breakage)

### Site UX
- **Search / filter by team name** — sidebar input → filter fixture list as you type ("Real Madrid" → only Real Madrid fixtures)
- **Compact list view toggle** — one-line-per-fixture spreadsheet view alongside current expanded cards
- **URL anchoring per fixture** — `?fixture=liverpool-brentford-may-24` for shareable / bookmarkable predictions
- **Sort by probability / edge** — option to surface top picks first
- **Sticky verdict pill** — pin outcome badge when scrolling long analysis panels
- **Backtest mode** — toggle to show all past fixtures with predicted vs actual outcomes for a season-long view
- **CSV export** — download this weekend's picks as a spreadsheet

### Data / Analysis
- **Probability calibration tracker** — when model says 60% home win, how often does home actually win? Plot calibration curve and surface confidence bias
- **xG numbers in the analysis panel** — Understat xG is fetched but only used for form dots; show "Liverpool 2.14 / 1.61 xG" in the panel too
- **Multi-bookmaker odds** — support a few books and pick the best price instead of a single `fairOdds` field
- **Transfermarkt injury scrape** — add to prompt as step 3 of the probability pipeline (steps 1 + 2 done)
- **Tournament scorer data in team news** — add one line to research prompt: include goal/assist tally for key players mentioned in team news (e.g. "Mbappé — likely to start, 3 goals this tournament")
- **⏳ WAITING: fifaindex.com squad data** — user to drop all 48 WC team pages (MHTML files) into a local folder. Parser ready to extract team OVR/ATK/MID/DEF + starting XI player names/positions/OVR and inject into `team_intel.py`. Individual team page URL format: `https://fifaindex.com/teams/1335-france`

### World Cup
- **Knockout placeholder resolution** — verify `W99` / `L101` / `2A` placeholders auto-resolve mid-tournament as openfootball updates; may need a manual nudge if it lags
- **Refresh FIFA rankings in `team_intel.py`** — rankings are hardcoded as of the 2026 WC seeding; update before each major tournament (next: Euros 2028 cycle)

---

## 🔄 In Progress

*(nothing active right now)*

---

## ✅ Done

### This session (v2.63 — 2026-06-18)
- **Score update schedule** — added 2am and 8am BST runs to `mark-results.yml` to catch World Cup overnight kick-offs (00:00–05:00 BST). Was missing a full night's worth of results
- **International team intel** — `team_intel.py`: FIFA rankings + World Cup history + continental tournament history (UEFA Euro, Copa América, AFCON, AFC Asian Cup, Gold Cup, OFC Nations Cup) for all 48 WC 2026 teams. Auto-injected into research prompts for international fixtures
- **SearXNG removed** — stripped from `agent.py` (fetch_news, fetch_article_text, call_lmstudio, run()). `refresh_today.py` now calls `auto_research.py` (OpenRouter) via subprocess instead of the old local LM Studio agent. `bench.py` updated to require news cache rather than fetching via SearXNG
- **Daily auto-research cron** — `auto-research.yml` now runs at 11am BST daily. Mid-tournament placeholder fixtures (W99 → real team) get researched same day instead of waiting until Monday
- **Midnight refresh workflow** — `refresh-tonight.yml` resets today/tomorrow's fixtures to stubs at midnight BST and re-researches via OpenRouter. Catches late injuries, lineup leaks, and suspension confirmations before kickoff
- **KANBAN.md** — task board created with Backlog / In Progress / Done columns

### Recent (v2.56–v2.62)
- **v2.62–v2.57** — Auto-marked World Cup group stage results
- **v2.56** — Fully automated fixture research via OpenRouter (deepseek:online) + GitHub Actions. Zero manual steps
- **v2.54** — Hit Rate stat-card per league (HIT/MISS tracking, Low picks excluded)
- **v2.53** — Self-contained DeepSeek prompt file (`fixtures_research_needed_prompt.txt`)
- **v2.52** — End-to-end DeepSeek research pipeline (72 WC fixtures across 4 batches)
- **v2.51** — World Cup 2026 integration: 104 fixtures, openfootball source, fetch + mark workflow
- **v2.47** — Per-fixture HIT / MISS badges + outcome tags (Home Win / Draw / Away Win)
- **v2.46** — Google search link per fixture (live score / match report)
- **v2.42** — Sidebar signal filter chips (Strong / Likely / Low) + past fixtures window (2d / Week / All)
- **v2.36** — Game-day refresh (`refresh_today.py`) — targeted stub reset + re-research in ~3 min
- **v2.35** — Research pipeline hardening: relevance scoring, alias resolver, wrong-fixture validation retry
- **v2.34** — Form dots (last 5 W/D/L) from Understat stored as `homeForm` / `awayForm`
- **v2.33** — Mobile responsive overhaul; verdict reworked to Home Win / Draw / Away Win + confidence tier
- **v2.32** — Understat xG enrichment in agent pipeline
- **v2.27** — Local AI research pipeline (`agent.py`) with LM Studio + SearXNG (now replaced by OpenRouter)
- **v2.5** — Auto-fetch fixtures workflow (football-data.org, every Monday)
- **v2.4** — Auto-mark results workflow (daily, football-data.org)
- **v2.0** — Eight competitions, book odds/edge, fixture verification workflow, All Fixtures view
