import datetime
import json
import re
import requests
from understatapi import UnderstatClient

from team_intel import build_intel_block, is_international

HTML_FILE = "index.html"


# ─── Understat xG ─────────────────────────────────────────────────────────────

UNDERSTAT_LEAGUES = {'pl', 'laliga', 'seriea', 'bundesliga', 'ligue1'}

UNDERSTAT_TEAM_MAP = {
    # Premier League
    'Arsenal': 'Arsenal',
    'Aston Villa': 'Aston_Villa',
    'Bournemouth': 'Bournemouth',
    'Brentford': 'Brentford',
    'Brighton': 'Brighton',
    'Burnley': 'Burnley',
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

UNDERSTAT_ALIASES = {
    'Brighton & Hove Albion':   'Brighton',
    'Wolverhampton':            'Wolves',
    'Wolverhampton Wanderers':  'Wolves',
    'Tottenham Hotspur':        'Tottenham',
    'Nottingham Forest':        'Nottingham',
    'West Ham United':          'West Ham',
    'Newcastle United':         'Newcastle',
    'Manchester United':        'Man United',
    'Manchester City':          'Man City',
    'AFC Bournemouth':          'Bournemouth',
    'Ipswich Town':             'Ipswich',
    'Leicester City':           'Leicester',
    'Leeds United':             'Leeds',
    'Leeds':                    'Leeds',
}

UNDERSTAT_TEAM_MAP['Leeds'] = 'Leeds'

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


def understat_slug(team):
    if team in UNDERSTAT_TEAM_MAP:
        return UNDERSTAT_TEAM_MAP[team]
    alias = UNDERSTAT_ALIASES.get(team)
    if alias and alias in UNDERSTAT_TEAM_MAP:
        return UNDERSTAT_TEAM_MAP[alias]
    return None


def get_season_year():
    now = datetime.datetime.now()
    return now.year - 1 if now.month <= 7 else now.year


def fetch_xg(team, league_id):
    if league_id not in UNDERSTAT_LEAGUES:
        return None
    slug = understat_slug(team)
    if not slug:
        print(f"  NOTE: no Understat slug for '{team}' — no xG/form")
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
            'form':           ' '.join(form),
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
    stubs = []
    for m in re.finditer(r"summary:\s*'Pending deep research\.'", html):
        prefix = html[max(0, m.start() - 5000):m.start()]
        home_matches = list(re.finditer(r"home:\s*'([^']+)'", prefix))
        away_matches = list(re.finditer(r"away:\s*'([^']+)'", prefix))
        if home_matches and away_matches:
            stubs.append((home_matches[-1].group(1), away_matches[-1].group(1)))
    return stubs


def get_fixture_meta(html, home, away):
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
    for m in re.finditer(r"summary:\s*'Pending deep research\.'", html):
        prefix = html[max(0, m.start() - 5000):m.start()]
        home_m = list(re.finditer(r"home:\s*'([^']+)'", prefix))
        away_m = list(re.finditer(r"away:\s*'([^']+)'", prefix))
        if not home_m or not away_m:
            continue
        if home_m[-1].group(1) != home or away_m[-1].group(1) != away:
            continue

        home_abs    = max(0, m.start() - 5000) + home_m[-1].start()
        block_start = html.rfind('{', 0, home_abs)

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


# ─── Prompt + JSON helpers (used by bench.py) ─────────────────────────────────

# Clubs whose plain token is too generic — match only by explicit phrase.
TEAM_MATCH_PHRASES = {
    'Man United':         ['man united', 'man utd', 'manchester united'],
    'Manchester United':  ['man united', 'man utd', 'manchester united'],
    'Man City':           ['man city', 'manchester city'],
    'Manchester City':    ['man city', 'manchester city'],
    'Leeds United':       ['leeds'],
    'Leeds':              ['leeds'],
    'Newcastle United':   ['newcastle'],
    'Newcastle':          ['newcastle'],
    'West Ham United':    ['west ham'],
    'West Ham':           ['west ham'],
    'Leicester City':     ['leicester'],
    'Leicester':          ['leicester'],
    'PSG':                ['psg', 'paris saint', 'paris sg'],
    'Paris SG':           ['psg', 'paris saint', 'paris sg'],
    'Paris Saint-Germain':['psg', 'paris saint', 'paris sg'],
    'AC Milan':           ['ac milan', 'milan'],
    'AC Pisa':            ['ac pisa', 'pisa'],
    'Como 1907':          ['como'],
    'RB Leipzig':         ['rb leipzig', 'leipzig'],
}


def team_tokens(name):
    if name in TEAM_MATCH_PHRASES:
        return TEAM_MATCH_PHRASES[name]
    stop = {'town', 'city', 'united', 'hove', 'albion', 'wanderers',
            'hotspur', 'forest', 'real', 'club'}
    toks = [w for w in re.split(r'[\s&.]+', name.lower()) if len(w) > 3]
    sig = [w for w in toks if w not in stop]
    return sig or toks or [name.lower()]


def build_prompt(home, away, competition, articles):
    news = "\n".join(articles) if articles else "No live news available."
    intel_block = build_intel_block(home, away) if is_international(competition) else ''
    return f"""Analyse this fixture and estimate win probabilities.

FIXTURE: {home} (home) vs {away} (away) — {competition}

{intel_block}
CRITICAL RULES — read before anything else:
- This exact match is {home} vs {away}. If a news article is about
  {home} or {away} playing a DIFFERENT opponent, use it only for that
  team's form/injuries — NEVER analyse the other opponent's match.
- This match HAS NOT been played yet. Do NOT invent a scoreline,
  goals, goalscorers, or match events. No "X scored an early goal".
- Only name players or managers that appear explicitly in the news
  below. Do not guess a manager's name or invent injuries.
- Every factor detail, context and summary MUST be about {home}
  versus {away} specifically — no other fixture.

CURRENT NEWS:
{news}

Return ONLY this JSON structure — no markdown, no code fences, no explanation:

{{
  "homeWin": <integer 0-100>,
  "draw": <integer 0-100>,
  "awayWin": <integer 0-100>,
  "verdict": "<Low|Likely|Strong>",
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
Use real player names from the news where available.
"""


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
