import datetime
import json
import re
import requests
from html.parser import HTMLParser
from understatapi import UnderstatClient

LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
SEARXNG_URL  = "http://localhost:8888/search"
MODEL        = "qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2"
HTML_FILE    = "index.html"


# ─── Understat xG ─────────────────────────────────────────────────────────────

# Leagues Understat covers (matches index.html league ids)
UNDERSTAT_LEAGUES = {'pl', 'laliga', 'seriea', 'bundesliga', 'ligue1'}

# Map fixture short names → Understat URL slugs
UNDERSTAT_TEAM_MAP = {
    # Premier League
    'Arsenal': 'Arsenal',
    'Aston Villa': 'Aston_Villa',
    'Bournemouth': 'Bournemouth',
    'Brentford': 'Brentford',
    'Brighton': 'Brighton',
    'Chelsea': 'Chelsea',
    'Crystal Palace': 'Crystal_Palace',
    'Everton': 'Everton',
    'Fulham': 'Fulham',
    'Ipswich': 'Ipswich',
    'Leicester': 'Leicester',
    'Liverpool': 'Liverpool',
    'Man City': 'Manchester_City',
    'Man United': 'Manchester_United',
    'Newcastle': 'Newcastle_United',
    'Nottingham': 'Nottingham_Forest',
    'Southampton': 'Southampton',
    'Spurs': 'Tottenham',
    'Sunderland': 'Sunderland',
    'Tottenham': 'Tottenham',
    'West Ham': 'West_Ham',
    'Wolves': 'Wolverhampton_Wanderers',
    # La Liga
    'Alaves': 'Alaves',
    'Athletic Club': 'Athletic_Club',
    'Atletico Madrid': 'Atletico_Madrid',
    'Barcelona': 'Barcelona',
    'Betis': 'Real_Betis',
    'Celta Vigo': 'Celta_Vigo',
    'Espanol': 'Espanol',
    'Getafe': 'Getafe',
    'Girona': 'Girona',
    'Las Palmas': 'Las_Palmas',
    'Leganes': 'Leganes',
    'Mallorca': 'Mallorca',
    'Osasuna': 'Osasuna',
    'Rayo Vallecano': 'Rayo_Vallecano',
    'Real Betis': 'Real_Betis',
    'Real Madrid': 'Real_Madrid',
    'Real Sociedad': 'Real_Sociedad',
    'Sevilla': 'Sevilla',
    'Valencia': 'Valencia',
    'Valladolid': 'Valladolid',
    'Villarreal': 'Villarreal',
    # Serie A
    'AC Milan': 'AC_Milan',
    'Atalanta': 'Atalanta',
    'Bologna': 'Bologna',
    'Cagliari': 'Cagliari',
    'Como': 'Como',
    'Empoli': 'Empoli',
    'Fiorentina': 'Fiorentina',
    'Genoa': 'Genoa',
    'Inter Milan': 'Internazionale',
    'Juventus': 'Juventus',
    'Lazio': 'Lazio',
    'Lecce': 'Lecce',
    'Monza': 'Monza',
    'Napoli': 'Napoli',
    'Parma': 'Parma',
    'Roma': 'Roma',
    'Torino': 'Torino',
    'Udinese': 'Udinese',
    'Venezia': 'Venezia',
    'Verona': 'Verona',
    # Bundesliga
    'Augsburg': 'Augsburg',
    'Bayern Munich': 'Bayern_Munich',
    'Bayer Leverkusen': 'Bayer_Leverkusen',
    'Bochum': 'Bochum',
    'Borussia Dortmund': 'Borussia_Dortmund',
    'Borussia Monchengladbach': 'Borussia_Monchengladbach',
    'Eintracht Frankfurt': 'Eintracht_Frankfurt',
    'Freiburg': 'Freiburg',
    'Heidenheim': 'Heidenheim',
    'Hoffenheim': 'Hoffenheim',
    'Holstein Kiel': 'Holstein_Kiel',
    'Mainz': 'Mainz_05',
    'RB Leipzig': 'RB_Leipzig',
    'St. Pauli': 'St._Pauli',
    'Stuttgart': 'Stuttgart',
    'Union Berlin': 'Union_Berlin',
    'Werder Bremen': 'Werder_Bremen',
    'Wolfsburg': 'Wolfsburg',
    # Ligue 1
    'Angers': 'Angers',
    'Auxerre': 'Auxerre',
    'Brest': 'Brest',
    'Le Havre': 'Le_Havre',
    'Lens': 'Lens',
    'Lille': 'Lille',
    'Lyon': 'Lyon',
    'Marseille': 'Marseille',
    'Metz': 'Metz',
    'Monaco': 'Monaco',
    'Montpellier': 'Montpellier',
    'Nantes': 'Nantes',
    'Nice': 'Nice',
    'PSG': 'Paris_Saint-Germain',
    'Paris SG': 'Paris_Saint-Germain',
    'Reims': 'Reims',
    'Rennes': 'Rennes',
    'Saint-Etienne': 'Saint-Etienne',
    'Strasbourg': 'Strasbourg',
    'Toulouse': 'Toulouse',
}

# Map index.html league display names → league ids
LEAGUE_NAME_TO_ID = {
    'Premier League':    'pl',
    'La Liga':           'laliga',
    'Serie A':           'seriea',
    'Bundesliga':        'bundesliga',
    'Ligue 1':           'ligue1',
    'Champions League':  'ucl',
    'Europa League':     'uel',
    'Conference League': 'uecl',
}


def get_season_year():
    """Return the Understat season start year (e.g. 2025 for the 2025-26 season)."""
    now = datetime.datetime.now()
    return now.year - 1 if now.month <= 7 else now.year


def fetch_xg(team, league_id):
    """
    Fetch last-6 xG stats for a team from Understat via understatapi.
    Returns a dict with averages and form string, or None if unavailable.
    """
    if league_id not in UNDERSTAT_LEAGUES:
        return None
    slug = UNDERSTAT_TEAM_MAP.get(team)
    if not slug:
        return None

    season = str(get_season_year())
    try:
        with UnderstatClient() as understat:
            matches = understat.team(team=slug).get_match_data(season=season)

        all_played = [m for m in matches if m.get('isResult')]
        last6 = all_played[-6:]
        last5 = all_played[-5:]
        if not last6:
            return None

        xg_for     = [float(m['xG'][m['side']]) for m in last6]
        xg_against = [float(m['xG']['a' if m['side'] == 'h' else 'h']) for m in last6]
        form       = [m['result'].upper() for m in last5]

        return {
            'xg_for_avg':     round(sum(xg_for)     / len(xg_for),     2),
            'xg_against_avg': round(sum(xg_against) / len(xg_against), 2),
            'form':           ' '.join(form),   # last 5, oldest → newest
            'games':          len(last6),
        }
    except Exception as e:
        print(f"  xG fetch failed for {team}: {e}")
        return None


# ─── HTML helpers ─────────────────────────────────────────────────────────────

def load_html():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()

def save_html(content):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def find_stubs(html):
    """Return (home, away) for every stub fixture by searching backwards from the stub marker."""
    stubs = []
    for m in re.finditer(r"summary:\s*'Pending deep research\.'", html):
        prefix = html[max(0, m.start() - 5000):m.start()]
        home_matches = list(re.finditer(r"home:\s*'([^']+)'", prefix))
        away_matches = list(re.finditer(r"away:\s*'([^']+)'", prefix))
        if home_matches and away_matches:
            stubs.append((home_matches[-1].group(1), away_matches[-1].group(1)))
    return stubs


def get_fixture_meta(html, home, away):
    """Extract day, time, result by searching backwards from the stub marker."""
    for m in re.finditer(r"summary:\s*'Pending deep research\.'", html):
        prefix = html[max(0, m.start() - 5000):m.start()]
        home_m = list(re.finditer(r"home:\s*'([^']+)'", prefix))
        away_m = list(re.finditer(r"away:\s*'([^']+)'", prefix))
        if not home_m or not away_m:
            continue
        if home_m[-1].group(1) != home or away_m[-1].group(1) != away:
            continue
        day_m    = list(re.finditer(r"day:\s*'([^']+)'", prefix))
        time_m   = list(re.finditer(r"time:\s*'([^']+)'", prefix))
        result_m = list(re.finditer(r"result:\s*([^,]+),", prefix))
        day    = day_m[-1].group(1)    if day_m    else "Unknown"
        time_  = time_m[-1].group(1)   if time_m   else "00:00"
        result = result_m[-1].group(1).strip().strip("'") if result_m else ""
        return day, time_, None if result in ("null", "") else result
    return "Unknown", "00:00", None


def get_league_for_fixture(html, home, away):
    league_pattern  = re.compile(r"name:\s*'([^']+)'.*?fixtures:\s*\[", re.DOTALL)
    fixture_pattern = re.compile(
        r"home:\s*'" + re.escape(home) + r"',\s*away:\s*'" + re.escape(away) + r"'"
    )
    for lm in league_pattern.finditer(html):
        league_name  = lm.group(1)
        league_start = lm.end()
        next_league  = html.find("name:", league_start + 10)
        block        = html[league_start:next_league if next_league > 0 else league_start + 50000]
        if fixture_pattern.search(block):
            return league_name
    return "Unknown"


def escape_js_string(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def format_team_news(items):
    if not items:
        return "[]"
    lines = [
        f"            {{ tag: '{item.get('tag','key')}', text: '{escape_js_string(item.get('text',''))}' }}"
        for item in items
    ]
    return "[\n" + ",\n".join(lines) + "\n          ]"


def build_replacement(home, away, day, time_, result, analysis, home_form=None, away_form=None):
    hw      = analysis["homeWin"]
    d       = analysis["draw"]
    aw      = analysis["awayWin"]
    verdict = analysis["verdict"]
    odds    = escape_js_string(analysis["fairOdds"])
    f       = analysis["factors"]
    tn      = analysis.get("teamNews", {"home": [], "away": []})
    context = escape_js_string(analysis.get("context", ""))
    summary = escape_js_string(analysis.get("summary", ""))

    def factor(key):
        v = f.get(key, {})
        score  = v.get('score', 50)  if isinstance(v, dict) else 50
        detail = v.get('detail', '') if isinstance(v, dict) else str(v)
        return f"{{ score: {score}, detail: '{escape_js_string(detail)}' }}"

    result_str = f"'{result}'" if result else "null"
    home_form_line = f"\n        homeForm: '{home_form}'," if home_form else ""
    away_form_line = f"\n        awayForm: '{away_form}'," if away_form else ""

    return f"""{{
        day: '{day}',
        home: '{escape_js_string(home)}', away: '{escape_js_string(away)}', time: '{time_}',
        result: {result_str}, homeWin: {hw}, draw: {d}, awayWin: {aw}, verdict: '{verdict}', fairOdds: '{odds}',{home_form_line}{away_form_line}
        factors: {{
          formBalance:   {factor('formBalance')},
          momentum:      {factor('momentum')},
          headToHead:    {factor('headToHead')},
          goalTendency:  {factor('goalTendency')},
          leagueContext: {factor('leagueContext')}
        }},
        teamNews: {{
          home: {format_team_news(tn.get('home', []))},
          away: {format_team_news(tn.get('away', []))}
        }},
        context: '{context}',
        summary: '{summary}'
      }}"""


def patch_fixture(html, home, away, replacement):
    """Replace the correct stub block by matching backwards from the stub marker."""
    for m in re.finditer(r"summary:\s*'Pending deep research\.'", html):
        prefix = html[max(0, m.start() - 5000):m.start()]
        home_m = list(re.finditer(r"home:\s*'([^']+)'", prefix))
        away_m = list(re.finditer(r"away:\s*'([^']+)'", prefix))
        if not home_m or not away_m:
            continue
        if home_m[-1].group(1) != home or away_m[-1].group(1) != away:
            continue

        # Find block start: scan backwards for the opening {
        home_abs    = max(0, m.start() - 5000) + home_m[-1].start()
        block_start = html.rfind('{', 0, home_abs)

        # Find block end: count braces forward from block_start
        depth = 0
        block_end = block_start
        for i in range(block_start, min(len(html), m.end() + 500)):
            if html[i] == '{':
                depth += 1
            elif html[i] == '}':
                depth -= 1
                if depth == 0:
                    block_end = i + 1
                    break

        return html[:block_start] + replacement + html[block_end:]

    print(f"  WARNING: stub not found for {home} vs {away}")
    return html


# ─── News fetching ────────────────────────────────────────────────────────────

def fetch_article_text(url, max_chars=1500):
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.chunks = []
                self.skip   = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self.skip = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self.skip = False
            def handle_data(self, data):
                if not self.skip:
                    t = data.strip()
                    if len(t) > 40:
                        self.chunks.append(t)

        p = TextExtractor()
        p.feed(resp.text)
        return " ".join(p.chunks)[:max_chars]
    except Exception:
        return ""


def is_relevant(text, home, away):
    """Return True if the article mentions at least one of the two teams."""
    t = text.lower()
    # Use first word of each team name to handle short refs (e.g. 'Brighton', 'United')
    home_tokens = [w for w in home.lower().split() if len(w) > 3]
    away_tokens = [w for w in away.lower().split() if len(w) > 3]
    for token in home_tokens + away_tokens:
        if token in t:
            return True
    return False


def fetch_news(home, away, max_results=8, full_text_limit=4):
    queries = [
        f"{home} {away} preview team news",
        f"{home} injuries",
        f"{away} injuries",
    ]
    seen, articles, full_text_count = set(), [], 0

    for q in queries:
        try:
            resp = requests.get(SEARXNG_URL, params={
                "q": q, "format": "json", "categories": "news"
            }, timeout=10)
            resp.raise_for_status()
            for r in resp.json().get("results", [])[:max_results]:
                url = r.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                title   = r.get("title", "").strip()
                snippet = r.get("content", "").strip()
                if full_text_count < full_text_limit:
                    body = fetch_article_text(url)
                    full_text_count += 1
                    if body:
                        if is_relevant(body, home, away):
                            articles.append(f"[{title}]\n{body}")
                        elif is_relevant(title + ' ' + snippet, home, away):
                            articles.append(f"- {title}: {snippet}")
                        continue
                if (title or snippet) and is_relevant(title + ' ' + snippet, home, away):
                    articles.append(f"- {title}: {snippet}")
        except Exception as e:
            print(f"  SearXNG error: {e}")

    # Fallback: if filter was too aggressive, return unfiltered snippets
    if not articles:
        print(f"  WARNING: relevance filter dropped all articles — using unfiltered snippets")
        for q in queries:
            try:
                resp = requests.get(SEARXNG_URL, params={
                    "q": q, "format": "json", "categories": "news"
                }, timeout=10)
                resp.raise_for_status()
                for r in resp.json().get("results", [])[:4]:
                    title   = r.get("title", "").strip()
                    snippet = r.get("content", "").strip()
                    if title or snippet:
                        articles.append(f"- {title}: {snippet}")
            except Exception:
                pass

    return articles


# ─── LM Studio ───────────────────────────────────────────────────────────────

def build_prompt(home, away, competition, articles):
    news = "\n".join(articles) if articles else "No live news available."
    return f"""Analyse this fixture and estimate win probabilities.

FIXTURE: {home} vs {away} — {competition}

CURRENT NEWS:
{news}

Return ONLY this JSON structure — no markdown, no code fences, no explanation:

{{
  "homeWin": <integer 0-100>,
  "draw": <integer 0-100>,
  "awayWin": <integer 0-100>,
  "verdict": "<Low|Moderate|Good|Strong>",
  "fairOdds": "<e.g. 3.50–3.80>",
  "factors": {{
    "formBalance":   {{ "score": <0-100>, "detail": "<text>" }},
    "momentum":      {{ "score": <0-100>, "detail": "<text>" }},
    "headToHead":    {{ "score": <0-100>, "detail": "<text>" }},
    "goalTendency":  {{ "score": <0-100>, "detail": "<text>" }},
    "leagueContext": {{ "score": <0-100>, "detail": "<text>" }}
  }},
  "teamNews": {{
    "home": [{{ "tag": "<out|doubt|key>", "text": "<player — reason>" }}],
    "away": [{{ "tag": "<out|doubt|key>", "text": "<player — reason>" }}]
  }},
  "context": "<tactical narrative paragraph>",
  "summary": "<2-3 sentence summary>"
}}

IMPORTANT: homeWin + draw + awayWin MUST sum to exactly 100.
Verdict is the confidence in whichever outcome has the highest probability:
  Low    = highest outcome below 50% — too close to call
  Likely = highest outcome 50-64% — one outcome favoured
  Strong = highest outcome 65%+ — dominant favourite
Factor scores: 50 = neutral; score each factor based on its impact on the most likely outcome.
  momentum: which team has better recent form and momentum heading in.
Use real player names from the news where available.
"""


def call_lmstudio(prompt):
    resp = requests.post(LMSTUDIO_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a football analyst. Return only valid JSON — no markdown, no code fences."},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10000
    }, timeout=180)
    resp.raise_for_status()
    msg = resp.json()["choices"][0]["message"]
    return msg.get("content", "").strip() or msg.get("reasoning_content", "").strip()


def parse_json(raw):
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)
    return json.loads(raw.strip())


# ─── Main loop ────────────────────────────────────────────────────────────────

def run():
    html  = load_html()
    stubs = find_stubs(html)
    total = len(stubs)

    if not stubs:
        print("No stub fixtures found — nothing to do.")
        return

    print(f"Found {total} stub fixtures to research.\n")

    for i, (home, away) in enumerate(stubs, 1):
        print(f"[{i}/{total}] {home} vs {away}")

        html        = load_html()
        day, time_, result = get_fixture_meta(html, home, away)
        competition = get_league_for_fixture(html, home, away)

        league_id = LEAGUE_NAME_TO_ID.get(competition, '')
        home_xg = fetch_xg(home, league_id)
        away_xg = fetch_xg(away, league_id)
        home_form = home_xg['form'] if home_xg else None
        away_form = away_xg['form'] if away_xg else None
        if home_xg:
            print(f"  xG {home}: for={home_xg['xg_for_avg']} vs={home_xg['xg_against_avg']} form={home_form}")
        if away_xg:
            print(f"  xG {away}: for={away_xg['xg_for_avg']} vs={away_xg['xg_against_avg']} form={away_form}")

        print(f"  Fetching news...")
        articles = fetch_news(home, away)
        print(f"  {len(articles)} articles found")

        print(f"  Querying {MODEL}...")
        try:
            analysis = parse_json(call_lmstudio(build_prompt(home, away, competition, articles)))
        except Exception as e:
            print(f"  FAILED: {e} — skipping\n")
            continue

        html = patch_fixture(html, home, away,
                             build_replacement(home, away, day, time_, result, analysis,
                                               home_form=home_form, away_form=away_form))
        save_html(html)
        print(f"  Done — H:{analysis['homeWin']}% D:{analysis['draw']}% A:{analysis['awayWin']}% · {analysis['verdict']}\n")

    print("All fixtures researched.")


if __name__ == "__main__":
    run()
