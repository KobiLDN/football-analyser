# DeepSeek research prompt template

Copy this into DeepSeek (web-search enabled), replacing `[HOME]`, `[AWAY]`, `[DATE]`.

DeepSeek returns the JSON; paste it into `research.json` and run `apply_research.bat`.

**Multiple fixtures in one go:** `research.json` can also be an array of
fixtures, e.g.

```json
[
  { ...fixture 1... },
  { ...fixture 2... },
  { ...fixture 3... }
]
```

The script validates all of them first, then applies and commits in one go.
Useful for "research this whole gameweek" — give DeepSeek a list and ask for
a JSON array back.

---

```
Research the football fixture [HOME] vs [AWAY] played on [DATE].

Use web search for current team news, injuries, recent form (last 5 results),
head-to-head, and pundit consensus. Then return ONLY this JSON object — no
markdown, no prose around it, no code fence:

{
  "home": "<EXACT team name from the canonical list below — e.g. 'Man United' not 'Manchester United', 'PSG' not 'Paris Saint-Germain'>",
  "away": "<EXACT team name from the canonical list below>",
  "day": "<Weekday DD Month, e.g. 'Sunday 24 May'>",
  "time": "<HH:MM UK time, e.g. '16:00'>",
  "result": "<X-Y if played, else null>",
  "homeWin": <integer 0-100>,
  "draw":    <integer 0-100>,
  "awayWin": <integer 0-100>,
  "verdict": "<Low|Likely|Strong>",
  "fairOdds": "<decimal odds range for leading outcome, e.g. '2.10-2.30'>",
  "homeForm": "<5 chars from W/D/L space-separated, oldest first, e.g. 'W W L D L'>",
  "awayForm": "<same format>",
  "factors": {
    "formBalance":   { "score": <0-100>, "detail": "<one sentence>" },
    "momentum":      { "score": <0-100>, "detail": "<one sentence>" },
    "headToHead":    { "score": <0-100>, "detail": "<one sentence>" },
    "goalTendency":  { "score": <0-100>, "detail": "<one sentence>" },
    "leagueContext": { "score": <0-100>, "detail": "<one sentence>" }
  },
  "teamNews": {
    "home": [{ "tag": "<out|doubt|key>", "text": "<Player — short reason>" }],
    "away": [{ "tag": "<out|doubt|key>", "text": "<Player — short reason>" }]
  },
  "context": "<2-4 sentence tactical / motivational paragraph mentioning real player names and current stakes>",
  "summary": "<2-3 sentence summary with specifics — no generic football tropes>"
}

RULES:
- homeWin + draw + awayWin MUST sum to exactly 100
- verdict = Strong if leading outcome ≥65%, Likely if 50-64%, Low if <50%
- If news is thin or contradictory, set verdict to Low and probabilities close
  to 33/34/33. Do not pad with generic phrases.
- Use real player names from your web search, not placeholders
- 'tag' field MUST be exactly one of: out | doubt | key
- 'out' = ruled out, 'doubt' = uncertain, 'key' = important player to watch
- Form string is OLDEST -> NEWEST (5 results, single space between each W/D/L)
- fairOdds is an estimated decimal odds range for the leading outcome
```

---

## Naming exactness matters

The script matches on `home + away + day` *exactly* against `index.html`.
If DeepSeek calls a team "Manchester United" but the site has "Man United",
the apply step will fail with "Fixture not found". Either:
- Tell DeepSeek the exact site name in the prompt
- Or edit `research.json` before running the script

---

# Canonical team names (use these EXACTLY in the JSON)
These match the team strings already in `index.html`. Using a different
variant (e.g. 'Manchester United' instead of 'Man United') will cause
`apply_research.py` to fail with 'Fixture not found'.

### Premier League
Arsenal, Aston Villa, Bournemouth, Brentford, Brighton & Hove Albion, Burnley, Chelsea, Crystal Palace, Everton, Fulham, Leeds United, Liverpool, Man City, Man United, Newcastle, Nottingham, Sunderland, Tottenham, West Ham, Wolverhampton

### La Liga
Alavés, Athletic, Atleti, Barça, Celta, Elche, Espanyol, Getafe, Girona, Levante, Mallorca, Osasuna, Rayo Vallecano, Real Betis, Real Madrid, Real Oviedo, Real Sociedad, Sevilla FC, Valencia, Villarreal

### Serie A
AC Pisa, Atalanta, Bologna, Cagliari, Como 1907, Cremonese, Fiorentina, Genoa, Inter, Juventus, Lazio, Lecce, Milan, Napoli, Parma, Roma, Sassuolo, Torino, Udinese, Verona

### Bundesliga
1. FC Köln, Augsburg, Bayern, Bremen, Dortmund, Frankfurt, Freiburg, HSV, Heidenheim, Hoffenheim, Leverkusen, Mainz, Mönchengladbach, RB Leipzig, St. Pauli, Stuttgart, Union Berlin, Wolfsburg

### Ligue 1
Angers SCO, Auxerre, Brest, FC Metz, Le Havre, Lille, Lorient, Marseille, Monaco, Nantes, Nice, Olympique Lyon, PSG, Paris FC, RC Lens, Stade Rennais, Strasbourg, Toulouse

### Champions League
Arsenal, PSG

### World Cup 2026
Algeria, Argentina, Australia, Austria, Belgium, Bosnia & Herzegovina, Brazil, Canada, Cape Verde, Colombia, Croatia, Curaçao, Czech Republic, DR Congo, Ecuador, Egypt, England, France, Germany, Ghana, Haiti, Iran, Iraq, Ivory Coast, Japan, Jordan, Mexico, Morocco, Netherlands, New Zealand, Norway, Panama, Paraguay, Portugal, Qatar, Saudi Arabia, Scotland, Senegal, South Africa, South Korea, Spain, Sweden, Switzerland, Tunisia, Turkey, USA, Uruguay, Uzbekistan

