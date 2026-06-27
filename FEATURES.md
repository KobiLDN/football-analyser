# Features

Running list of ideas, things in progress, and things shipped. Pick from the Backlog when there's time, move to Done with the version it shipped in.

## Collaboration process

- Read `AGENTS.md` first, then `CHANGELOG.md`, before making edits.
- Before editing, run: `git checkout main` then `git pull --rebase`.
- After editing, prepend one row to `CHANGELOG.md` directly under the table header (**`YYYY-MM-DD HH:MM BST`**, AI Name, Changed) — **newest first**.
- If user-visible behavior changed, add a **Done** entry below with version/date context.
- Keep each AI session focused on one intent where possible (smaller diffs, easier merges).

## Backlog

### Pipeline polish

- **Pre-commit hook** — run `node -e "loadLeagues(html)"` before any commit to catch schema breakage (would have prevented the v2.33-era `fetch-fixtures` regression that wiped data).
- **`scripts/README.md`** — one-line description per script (`agent.py`, `fetch-fixtures.js`, `apply_research.py`, etc.).

### Site UX

- **Search / filter by team name** — sidebar input → filter the fixture list as you type ("Real Madrid" → only Real Madrid matches).
- **Compact list view toggle** — switch between expanded cards (current) and a one-line-per-fixture spreadsheet-style view for quick scanning.
- **URL anchoring per fixture** — `?fixture=liverpool-brentford-may-24` so a specific prediction can be shared/bookmarked.
- **Sort by leading probability / edge** — top picks first option in the fixture list.

### Data / analysis

- **Home win / draw / away win probability** — step (3) remaining: add Transfermarkt injury scrape per team to prompt. Steps (1) restructure to homeWin/draw/awayWin and (2) Understat xG enrichment are both done.
- **Probability calibration tracker** — when model says "60% home win", how often does home actually win across the season? Plot calibration curve, surface confidence-bias.
- **xG numbers in the analysis panel** — we already fetch them via Understat (currently only used to derive form dots). Show "Liverpool 2.14 / 1.61 xG" alongside form.
- **Backtest mode** — toggle to show all past fixtures with predicted vs actual outcomes for a season-long view.
- **CSV export** — download this weekend's picks as a spreadsheet.
- **Multi-bookmaker odds** — currently a single `bookOdds` field; support a few books and pick the best price.

### Reliability / monitoring

- **Discord / email webhook on workflow failures** — get pinged when `auto-mark`, `auto-fetch`, or `verify-fixtures` fails. Currently only know by manually opening Actions.
- **Schema migration helper** — when we add a new fixture field (e.g. v2.33's `homeWin` rework), automate retrofitting old fixtures and updating serializers. Prevents the kind of cross-script breakage we hit at v2.33.

### World Cup specific

- **Name resolution for knockout placeholders** — openfootball uses `W99` / `L101` / `2A` placeholders until the bracket fills. Verify they auto-resolve mid-tournament; may need a manual nudge if openfootball lags. (`fetch-worldcup.yml` daily cron is already set up.)
- **International fixture research quality** — national teams have no Understat xG / form data. Partially addressed: `team_intel.py` now injects FIFA rankings + tournament history into prompts. Remaining: Transfermarkt international-team form scrape for live pre-tournament form.

### Sticky misc

- **Sticky verdict pill** — pin the outcome badge when scrolling long fixture analysis panels.

## Done

- **v2.97** — Marked 2 World Cup results.
- **v2.96** — Marked 4 World Cup results.
- **v2.95** — Marked 2 World Cup results.
- **v2.94** — Auto-fetched 4 World Cup 2026 fixture stubs.
- **v2.93** — Marked 4 World Cup results.
- **v2.92** — Marked 2 World Cup results.
- **v2.91** — FIFA rank redesigned: shown below each team name in aligned columns (`Czech Republic vs Mexico / FIFA rank #35  FIFA rank #15`). Light mode set as default. Branch renamed to `dev` for cleaner Cloudflare staging URL ([dev.football-analyser.pages.dev](https://dev.football-analyser.pages.dev)).
- **v2.90** — Auto-fetched 4 World Cup 2026 fixture stubs.
- **v2.89** — FIFA rankings shown beside team names on World Cup fixtures (`France #2 vs Morocco #13`). `WC_RANKS` JS lookup for all 48 teams; `wcRankBadge()` helper; `.wc-rank` CSS class (muted, small). Domestic fixtures unaffected. Cloudflare Pages staging set up for branch preview deployments.
- **v2.88** — Marked 4 World Cup results.
- **v2.87** — Marked 2 World Cup results.
- **v2.86** — Marked 2 World Cup results.
- **v2.85** — Marked 1 World Cup result.
- **v2.84** — Marked 1 World Cup result.
- **v2.83** — Marked 3 World Cup results.
- **v2.82** — Marked 1 World Cup result.
- **v2.81** — Auto-fetched 3 World Cup 2026 fixture stubs.
- **v2.80** — Marked 2 World Cup results.
- **v2.79** — Marked 1 World Cup result.
- **v2.78** — Marked 1 World Cup result.
- **v2.75** — Marked 2 World Cup results.
- **v2.74** — Marked 1 World Cup result.
- **v2.73** — Marked 1 World Cup result.
- **v2.72** — Marked 3 World Cup results.
- **v2.71** — WC form dots for all 48 teams (verified WC results + pre-tournament qualifiers/friendlies). Unknown `?` dots now grey instead of red. Hit rate now includes Low-confidence picks. Head to Head factor removed from pipeline. Likely threshold raised to 55%. Strong/Likely split shown in hit rate stat card. Factor score modal for mobile. fetch-worldcup.yml runs every 3 hours.
- **v2.70** — Marked 1 World Cup result.
- **v2.69** — Marked 1 World Cup result.
- **v2.68** — Marked 1 World Cup result.
- **v2.67** — Marked 1 World Cup result.
- **v2.66** — Marked 1 World Cup result.
- **v2.65** — Marked 4 World Cup results.
- **v2.63** — Score updates now 4× daily (2am + 8am BST added for World Cup overnight kick-offs). `team_intel.py`: FIFA rankings + WC history + continental tournament history (UEFA Euro, AFCON, Copa América, AFC Asian Cup, Gold Cup, OFC Nations Cup) for all 48 WC 2026 teams — auto-injected into research prompts for international fixtures. SearXNG + LM Studio removed from pipeline; `refresh_today.py` now uses OpenRouter. Daily 11am BST auto-research cron added. New midnight BST refresh workflow catches late team news before kickoff. `KANBAN.md` task board created.
- **v2.62** — Marked 4 World Cup results.
- **v2.61** — Marked 4 World Cup results.
- **v2.60** — Marked 5 World Cup results.
- **v2.59** — Marked 3 World Cup results.
- **v2.58** — Marked 2 World Cup results.
- **v2.57** — Marked 2 World Cup results.
- **v2.56** — Fully automated fixture research: `auto_research.py` + `auto_research.bat` + `.github/workflows/auto-research.yml`. Calls OpenRouter (deepseek:online) after Monday's fetch workflow, researches all stubs, commits to main — zero manual steps. `OPENROUTER_API_KEY` stored as GitHub Actions secret.
- **v2.55** — Auto-marked 1 result (PSG 5-4 Arsenal).
- **v2.54** — Hit Rate stat-card replaces Top Confidence in the league header. Aggregates HIT/MISS across all past graded fixtures (Low-confidence picks excluded — coin flips). Big % with `X of Y` fraction below. Stable across sidebar filter toggles. All Fixtures shows cross-competition rate; per-league views show that league's rate.
- **v2.53** — `make_fixtures.bat` now also writes `fixtures_research_needed_prompt.txt` — a self-contained, ready-to-paste DeepSeek prompt with the fixtures, schema, and canonical team-name list all embedded. Eliminates the last manual editing step: copy → paste → save JSON → `apply_research.bat`.
- **v2.52** — End-to-end DeepSeek research pipeline: `make_fixtures.bat` builds fixture batches → upload to DeepSeek `:online` → drop the returned `deepseek_json_*.json` in the repo → `apply_research.bat` auto-detects, validates atomic, applies, commits dev→main→live, archives. All 72 named-team World Cup fixtures researched this way (4 batches, zero Claude tokens used for the data).
- **v2.51** — World Cup 2026 integration shipped end-to-end: `worldcup` league + new "International" sidebar group (`index.html`); `scripts/fetch-worldcup.js` pulls from public-domain `openfootball/worldcup.json` (no API key needed after API-Football's 2026 paywall blocked us); same script also marks results when openfootball publishes them, so no separate mark-worldcup workflow needed; `.github/workflows/fetch-worldcup.yml` runs Mondays 09:00 UTC and supports manual dispatch.
- **v2.50** — Auto-fetched 104 World Cup 2026 fixture stubs.
- **v2.49** — Auto-fetched 1 upcoming fixture stubs.
- **v2.48** — Auto-marked 17 results (Sunderland 2-1 Chelsea; Brighton & Hove Albion 0-3 Man United; Crystal Palace 1-2 Arsenal, +14 more).
- **v2.47** — Per-fixture HIT / MISS prediction badge + symmetric outcome tags. Past fixtures' score line now reads e.g. `Final Score: 4 – 2 · Home Win · ✅ HIT · 🔗 Match report`. Home Win in blue, Draw in gold, Away Win in red (matches the win-probability palette). Badge logic: highest-probability outcome matches actual → green ✅ HIT; mismatch → red ❌ MISS; Low-confidence picks get no badge (we agreed those are coin-flips).
- **v2.46** — Per-fixture Google search link: `🔗 Score` next to upcoming fixtures' kick-off time, `🔗 Match report` next to played fixtures' final score. Opens a Google search for "Home vs Away" in a new tab — handy for grabbing live score / lineups / news without leaving the page.
- **v2.45** — Auto-marked 1 result (Parma 1-0 Sassuolo).
- **v2.44** — Auto-marked 11 results (Alavés 1-2 Rayo Vallecano; Real Betis 2-1 Levante; Celta 1-0 Sevilla FC, +8 more).
- **v2.43** — Re-researched all 10 Saturday 23 May fixtures with fresh xG/form/news via the now-fixed `refresh_today.bat`.
- **v2.42** — Sidebar Display filters: **Past fixtures** chip group (Off / 2d / Week / All — mutually exclusive) replacing the old binary toggle; **Signal** chip group (All / Strong / Likely / Low — multi-select, e.g. Strong + Likely combinable). Both filters compose via AND. Surfaces the weekend's best picks instantly.
- **v2.41** — Auto-marked 1 result (Fiorentina 1-1 Atalanta).
- **v2.40** — Fixed missing form dots for Burnley vs Wolverhampton and West Ham vs Leeds United. Added `'Burnley': 'Burnley'` to `UNDERSTAT_TEAM_MAP` (Burnley was the only club genuinely missing — Wolves and Leeds already resolved correctly, their fixtures just predated the alias fix). Patched both fixtures' form fields directly with live Understat data.
- **v2.39** — Auto-marked 1 result (Bournemouth 1-1 Man City).
- **v2.38** — Verify workflow now auto-corrects fixture date/time mismatches directly in `index.html` and commits the fix; only genuinely missing fixtures still require manual review.
- **v2.37** — Collapsible day groups in the fixture list: click any date header to hide/show all fixtures for that day. Fixture count shown on the right, chevron rotates to indicate state. Useful for browsing past fixtures — minimise dates you've already reviewed. Bundled fixes: Past Fixtures toggle (which was silently breaking on a `ReferenceError` in the legacy-schema render branch) and the failing Auto-mark results workflow (three brittle regex anchors in `scripts/*.js`).
- **v2.35** — Auto-marked 1 result (Chelsea 2-1 Tottenham).
- **v2.36** — Game-day refresh (`refresh_today.py` + `refresh_today.bat`): targeted reset of fixtures playing within N days, then auto-runs the agent. Lets you incorporate the latest team news / probabilities on matchday in ~3–5 min instead of full week reset.
- **v2.35** — Research pipeline hardening: scored news relevance filter (both-team priority, single-team cap), Understat name-alias resolver (fixes missing xG/form for long club names), prompt rules against fictional scorelines / wrong-opponent / guessed personnel, post-validation retry when analysis doesn't mention both teams.
- **v2.34** — Form dots (last 5 W/D/L) per team in fixture row; fetched from Understat via agent pipeline and stored as `homeForm`/`awayForm` on each fixture. Restored `import datetime` + `fetch_xg` calls in agent.
- **v2.33** — Mobile responsive overhaul (scrollable sidebar, two-line team names, tighter layout). Verdict system reworked: badge now shows predicted outcome (Home Win / Draw / Away Win) + confidence (Low / Likely / Strong); `drawRates` replaced with `momentum`; agent prompt updated for general outcome prediction.
- **v2.32** — Understat xG enrichment added to agent research pipeline (`understatapi`); all 36 unplayed fixtures re-researched with last-6 xG for/against and form per team.
- **v2.31** — Renamed app to Football Analyser; column header renamed to Signal; README updated.
- **v2.30** — Auto-fetched 30 upcoming fixture stubs.
- **v2.28** — Merged 23 auto-marked results into fully-researched DEV fixture data; both analysis and scorelines now live in `index.html`.
- **v2.27** — Local AI research pipeline (`agent.py`) built using LM Studio (Gemma 4B) + SearXNG. Automatically fetches live news, analyses draw probability, and injects full fixture data into `index.html` for all stub fixtures across 5 leagues.
- **v2.26** — Auto-marked 11 results (Man United 3-2 Nottingham; Brentford 2-2 Crystal Palace; Everton 1-3 Sunderland, +8 more).
- **v2.25** — Auto-marked 8 results (Bremen 0-2 Dortmund; Heidenheim 0-2 Mainz; Freiburg 4-1 RB Leipzig, +5 more).
- **v2.24** — Auto-marked 1 result (Aston Villa 4-2 Liverpool).
- **v2.23** — Auto-marked 3 results (Valencia 1-1 Rayo Vallecano; Girona 1-1 Real Sociedad; Real Madrid 2-0 Real Oviedo).
- **v2.22** — Full `staging/` snapshot merged to `main` (GitHub); `README.md` / `CHANGELOG.md` / `FEATURES.md` now describe mark-results Thu–Sun 5pm and fetch preservation of `teamNews` / `context` / `bookOdds`.
- **v2.21** — Conducted deep research for 3 La Liga Matchday 35 fixtures (Valencia, Girona, Real Madrid) with full draw probability analysis. **Same window (CI):** `fetch-fixtures.js` now preserves `teamNews`, `context`, and `bookOdds` when re-serializing fixtures (Monday fetch can no longer strip research); `mark-results.yml` 5pm BST cron extended to Thu–Sun for midweek scorelines.
- **v2.20** — Removed hardcoded fixtures to transition entirely to API-fetched data via GitHub Actions.
- **v2.19** — Auto-marked 3 results (Celta 2-3 Levante; Real Betis 2-1 Elche; Osasuna 1-2 Atleti).
- **v2.18** — Auto-marked 4 results (Tottenham Hotspur 1-1 Leeds United; Tottenham 1-1 Leeds United; Rayo Vallecano 1-1 Girona, +1 more).
- **v2.17** — Auto-fetched 2 upcoming fixture stubs (Premier League 2). Pending deep research.
- **v2.16** — Auto-marked 16 results (West Ham 1-1 Arsenal; Real Oviedo 0-0 Getafe; Barcelona 2-0 Real Madrid, +13 more).
- **v2.15** — Fixture list now has aligned headings for Fixture, League, Research, Draw Probability, and Draw Signal; table width, expanded details, and small text sizing were tuned for readability.
- **v2.14** — Verdict colours now follow a traffic-light scale: Low red, Moderate amber, Good green, Strong blue; matching percentage text and mini-bars improve scanability.
- **v2.13** — `CHANGELOG.md` first column uses **date + time** (`YYYY-MM-DD HH:MM BST`); docs updated for prepend workflow field.
- **v2.12** — `CHANGELOG.md` reordered **newest-first** with the column format line at the top; prepend workflow documented in `AGENTS.md`, `README.md`, `FEATURES.md`.
- **v2.11** — Improved readability of low-contrast labels by making `Fair draw odds` white and updating shared `--text3` color token to white in `index.html`. Added table-based `CHANGELOG.md` and multi-AI workflow guidance in docs.
- **v2.10** — Auto-marked 13 results (Nottingham Forest 1-1 Newcastle United; Crystal Palace 2-2 Everton; Burnley 2-2 Aston Villa, +10 more).
- **v2.9** — Backfilled 16 legacy results with actual scorelines (replaced `'home'`/`'draw'`/`'away'` with `'X-Y'`).
- **v2.8** — Replaced DRAW/HOME/AWAY result badges with actual scorelines. Past fixtures now show "Final Score: X – X" (with "· DRAW" in gold for draws) where the kick-off time used to be.
- **v2.7** — Auto-marked 14 results (Liverpool 1-1 Chelsea; Sunderland 0-0 Manchester United; Fulham 0-1 AFC Bournemouth, +11 more).
- **v2.6** — Auto-fetched 79 upcoming fixture stubs (Premier League 11, La Liga 23, Serie A 15, Bundesliga 12, Ligue 1 18). Pending deep research.
- **v2.5** — Split topbar timestamp into Page (last code change) and Data (last fixture/results update). Auto-fetch fixtures workflow (`fetch-fixtures.js` + `fetch-fixtures.yml`) pulls upcoming stubs from football-data.org every Monday. Auto-mark schedule updated to 5pm + 11pm BST.
- **v2.4** — Auto-mark results workflow. Daily action queries football-data.org for finished matches and patches `result:` in `index.html`, then auto-commits. Works alongside the existing verify-fixtures workflow without retriggering it.
- **v2.3** — `AGENTS.md` guide introduced (originally `CLAUDE.md`) with the after-every-edit convention (bump version, update docs for user-visible changes, keep commits focused).
- **v2.2** — "Past fixtures" toggle in the sidebar (Display section). Default is upcoming-only; toggle ON to include played fixtures with their result badges.
- **v2.1** — Page-updated timestamp in the topbar; version display bumped from v2.
- **v2.1** — `FEATURES.md` (this file).
- **v2.0** — Kick-off time colour fixed (was `--text3` on a near-identical surface, now `--text2`).
- **v2.0** — Fixture verification workflow against football-data.org (daily + on push).
- **v2.0** — README refreshed to match current code (8 leagues, book-odds/edge feature, verification workflow).
- **v2.0** — Value/edge calculation comparing book odds against fair odds.
- **v2.0** — All Fixtures view as the default landing page.
- **v2.0** — Eight competitions: PL, La Liga, Serie A, Bundesliga, Ligue 1, UCL, UEL, UECL.
