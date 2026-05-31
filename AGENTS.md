# Agent Guide (Read First)

This file is for any AI or human contributor working in this repo.

## Read order before editing

1. `AGENTS.md` (this file)
2. `CHANGELOG.md` (newest entry is first row under the header)
3. `FEATURES.md` (Backlog/Done context)
4. `README.md` (product/developer context)

## After every edit

When you commit a change, update these in the same commit:

1. **`index.html` topbar**
   - Bump version by `0.1` (example: `v2.11 -> v2.12`)
   - Refresh `Page · <date> <time> BST`
2. **`CHANGELOG.md`**
   - Prepend one new table row (immediately under the header) with **date and time** (`YYYY-MM-DD HH:MM BST`), AI Name, and Changed — **newest first**; same day, use time to order.
3. **`FEATURES.md`**
   - Add a **Done** entry for user-visible shipped work
   - Remove matching Backlog item if completed
4. **`README.md`**
   - Update only if user-visible behavior or developer workflow changed

## Version scheme

- Project stays on v2 line for this season build.
- Each commit to `main` increments minor by `0.1`.
- After `v2.9` comes `v2.10`, `v2.11`, etc.
- Reserve `v3` for major redesign/season rollover.

## Branching and merging

- Work on a feature branch when possible; avoid direct risky edits on `main`.
- Open PR and squash-merge to keep history clean.
- Never force-push `main`.

## Sensitive data

- Never commit API keys.
- Keep secrets in GitHub Actions secrets.
- `FOOTBALL_DATA_API_KEY` — required by fetch-fixtures, mark-results, verify-fixtures, backfill-scores workflows (football-data.org).
- `OPENROUTER_API_KEY` — required by auto-research workflow (OpenRouter deepseek:online).

## Style and scope

- Match the dark theme tokens in `:root` in `index.html`.
- Keep comments minimal; only add when intent is non-obvious.
- Keep commits focused to one logical change.
