"""
International team intelligence: FIFA rankings and continental tournament history.
Injected into research prompts for World Cup and other international fixtures.

Rankings: approximate as of World Cup 2026 seeding (early 2026).
Results:  Champions / Final (RU) / SF / QF / R16 / GS / DNQ
'recent': last 3 editions, newest first.
"""

TEAM_INTEL = {

    # ── CONMEBOL ──────────────────────────────────────────────────────────────
    'Argentina': {
        'fifa_rank': 1,
        'wc':   {'best': 'Champions', 'recent': ['2022 Champions', '2018 R16', '2014 Final (RU)']},
        'cont': {'name': 'Copa América', 'best': 'Champions (16×)', 'recent': ['2024 Champions', '2021 Champions', '2019 QF']},
    },
    'Brazil': {
        'fifa_rank': 5,
        'wc':   {'best': 'Champions', 'recent': ['2022 QF', '2018 QF', '2014 SF']},
        'cont': {'name': 'Copa América', 'best': 'Champions (9×)', 'recent': ['2024 QF', '2021 Final (RU)', '2019 Champions']},
    },
    'Colombia': {
        'fifa_rank': 12,
        'wc':   {'best': 'QF (2014)', 'recent': ['2018 R16', '2014 QF', '2006 GS']},
        'cont': {'name': 'Copa América', 'best': 'Champions (2001)', 'recent': ['2024 Final (RU)', '2021 QF', '2019 QF']},
    },
    'Uruguay': {
        'fifa_rank': 16,
        'wc':   {'best': 'Champions', 'recent': ['2022 GS', '2018 QF', '2014 R16']},
        'cont': {'name': 'Copa América', 'best': 'Champions (15×)', 'recent': ['2024 SF', '2021 SF', '2019 QF']},
    },
    'Ecuador': {
        'fifa_rank': 44,
        'wc':   {'best': 'R16 (2006)', 'recent': ['2022 GS', '2014 GS', '2006 R16']},
        'cont': {'name': 'Copa América', 'best': 'SF', 'recent': ['2024 QF', '2021 QF', '2019 GS']},
    },
    'Paraguay': {
        'fifa_rank': 62,
        'wc':   {'best': 'QF', 'recent': ['2010 QF', '2006 R16', '2002 R16']},
        'cont': {'name': 'Copa América', 'best': 'Champions (2×)', 'recent': ['2024 GS', '2021 GS', '2019 QF']},
    },

    # ── CONCACAF ──────────────────────────────────────────────────────────────
    'USA': {
        'fifa_rank': 11,
        'wc':   {'best': 'SF (1930)', 'recent': ['2022 R16', '2014 R16', '2010 R16']},
        'cont': {'name': 'Gold Cup', 'best': 'Champions (7×)', 'recent': ['2023 Champions', '2021 Champions', '2019 Final (RU)']},
    },
    'Mexico': {
        'fifa_rank': 15,
        'wc':   {'best': 'QF', 'recent': ['2022 GS', '2018 R16', '2014 R16']},
        'cont': {'name': 'Gold Cup', 'best': 'Champions (12×)', 'recent': ['2023 SF', '2021 Final (RU)', '2019 Champions']},
    },
    'Canada': {
        'fifa_rank': 40,
        'wc':   {'best': 'GS', 'recent': ['2022 GS', '1986 GS']},
        'cont': {'name': 'Gold Cup', 'best': 'Champions (2000)', 'recent': ['2023 SF', '2021 QF', '2019 QF']},
    },
    'Panama': {
        'fifa_rank': 75,
        'wc':   {'best': 'GS (2018)', 'recent': ['2018 GS']},
        'cont': {'name': 'Gold Cup', 'best': 'Final (RU) (2×)', 'recent': ['2023 QF', '2021 QF', '2019 SF']},
    },
    'Haiti': {
        'fifa_rank': 103,
        'wc':   {'best': 'GS (1974)', 'recent': ['1974 GS']},
        'cont': {'name': 'Gold Cup', 'best': 'Champions (1973)', 'recent': ['2023 GS', '2021 QF', '2019 R16']},
    },
    'Curaçao': {
        'fifa_rank': 82,
        'wc':   {'best': 'GS (debut 2026)', 'recent': ['2026 debut']},
        'cont': {'name': 'Gold Cup', 'best': 'QF', 'recent': ['2023 GS', '2021 QF']},
    },

    # ── UEFA (Europe) ─────────────────────────────────────────────────────────
    'France': {
        'fifa_rank': 2,
        'wc':   {'best': 'Champions', 'recent': ['2022 Final (RU)', '2018 Champions', '2014 QF']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (2×)', 'recent': ['2024 SF', '2021 R16', '2020 R16']},
    },
    'England': {
        'fifa_rank': 5,
        'wc':   {'best': 'Champions (1966)', 'recent': ['2022 QF', '2018 SF', '2014 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Final (RU)', 'recent': ['2024 Final (RU)', '2021 Final (RU)', '2020 QF']},
    },
    'Spain': {
        'fifa_rank': 8,
        'wc':   {'best': 'Champions (2010)', 'recent': ['2022 QF', '2018 R16', '2014 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (4×)', 'recent': ['2024 Champions', '2021 R16', '2020 R16']},
    },
    'Germany': {
        'fifa_rank': 12,
        'wc':   {'best': 'Champions (4×)', 'recent': ['2022 GS', '2018 GS', '2014 Champions']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (3×)', 'recent': ['2024 QF', '2021 R16', '2020 SF']},
    },
    'Portugal': {
        'fifa_rank': 6,
        'wc':   {'best': '3rd (1966)', 'recent': ['2022 QF', '2018 R16', '2014 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (2016)', 'recent': ['2024 QF', '2021 QF', '2020 SF']},
    },
    'Netherlands': {
        'fifa_rank': 7,
        'wc':   {'best': 'Final (RU) (3×)', 'recent': ['2022 QF', '2014 3rd', '2010 Final (RU)']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (1988)', 'recent': ['2024 SF', '2021 R16', '2020 GS']},
    },
    'Belgium': {
        'fifa_rank': 9,
        'wc':   {'best': '3rd (2018)', 'recent': ['2022 GS', '2018 3rd', '2014 QF']},
        'cont': {'name': 'UEFA Euro', 'best': 'QF', 'recent': ['2024 R16', '2021 R16', '2020 QF']},
    },
    'Croatia': {
        'fifa_rank': 10,
        'wc':   {'best': '3rd', 'recent': ['2022 3rd', '2018 Final (RU)', '2014 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'QF', 'recent': ['2024 R16', '2021 R16', '2020 R16']},
    },
    'Switzerland': {
        'fifa_rank': 20,
        'wc':   {'best': 'QF', 'recent': ['2022 QF', '2018 R16', '2014 R16']},
        'cont': {'name': 'UEFA Euro', 'best': 'QF', 'recent': ['2024 QF', '2021 QF', '2020 R16']},
    },
    'Turkey': {
        'fifa_rank': 28,
        'wc':   {'best': '3rd (2002)', 'recent': ['2002 3rd', '1954 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'SF (2008)', 'recent': ['2024 QF', '2021 GS', '2020 R16']},
    },
    'Scotland': {
        'fifa_rank': 40,
        'wc':   {'best': 'GS', 'recent': ['1998 GS', '1990 GS', '1986 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'GS', 'recent': ['2024 GS', '2021 GS']},
    },
    'Norway': {
        'fifa_rank': 38,
        'wc':   {'best': 'QF (1938)', 'recent': ['1998 R16', '1994 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Never qualified (since 2000)', 'recent': ['2024 DNQ', '2021 DNQ', '2020 DNQ']},
    },
    'Austria': {
        'fifa_rank': 25,
        'wc':   {'best': '3rd (1954)', 'recent': ['1998 GS', '1990 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'QF (2024)', 'recent': ['2024 QF', '2021 GS', '2020 GS']},
    },
    'Czech Republic': {
        'fifa_rank': 35,
        'wc':   {'best': 'GS (as independent CZE)', 'recent': ['2006 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (1996)', 'recent': ['2024 GS', '2021 QF', '2020 R16']},
    },
    'Sweden': {
        'fifa_rank': 26,
        'wc':   {'best': 'Final (RU) (1958)', 'recent': ['2018 QF', '2006 R16', '2002 SF']},
        'cont': {'name': 'UEFA Euro', 'best': 'Champions (1992)', 'recent': ['2024 DNQ', '2021 R16', '2020 R16']},
    },
    'Bosnia & Herzegovina': {
        'fifa_rank': 65,
        'wc':   {'best': 'GS (2014)', 'recent': ['2014 GS']},
        'cont': {'name': 'UEFA Euro', 'best': 'Never qualified', 'recent': ['2024 DNQ', '2021 DNQ']},
    },

    # ── CAF (Africa) ──────────────────────────────────────────────────────────
    'Morocco': {
        'fifa_rank': 13,
        'wc':   {'best': 'SF (2022)', 'recent': ['2022 SF', '2018 GS', '2014 DNQ']},
        'cont': {'name': 'AFCON', 'best': 'Champions (1976)', 'recent': ['2023 QF', '2021 QF', '2019 QF']},
    },
    'Senegal': {
        'fifa_rank': 20,
        'wc':   {'best': 'QF (2002)', 'recent': ['2022 R16', '2018 GS', '2002 QF']},
        'cont': {'name': 'AFCON', 'best': 'Champions (2022)', 'recent': ['2023 QF', '2021 Champions', '2019 Final (RU)']},
    },
    'Ivory Coast': {
        'fifa_rank': 48,
        'wc':   {'best': 'GS', 'recent': ['2014 GS', '2010 GS', '2006 GS']},
        'cont': {'name': 'AFCON', 'best': 'Champions (3×)', 'recent': ['2023 Champions', '2021 R16', '2019 QF']},
    },
    'Egypt': {
        'fifa_rank': 35,
        'wc':   {'best': 'GS', 'recent': ['2018 GS', '1990 GS', '1934 GS']},
        'cont': {'name': 'AFCON', 'best': 'Champions (7×)', 'recent': ['2023 R16', '2021 Final (RU)', '2019 R16']},
    },
    'Ghana': {
        'fifa_rank': 60,
        'wc':   {'best': 'QF (2010)', 'recent': ['2022 GS', '2014 GS', '2010 QF']},
        'cont': {'name': 'AFCON', 'best': 'Champions (4×)', 'recent': ['2023 R16', '2021 QF', '2019 R16']},
    },
    'Algeria': {
        'fifa_rank': 45,
        'wc':   {'best': 'R16 (2014)', 'recent': ['2014 R16', '2010 GS', '1986 R16']},
        'cont': {'name': 'AFCON', 'best': 'Champions (2×)', 'recent': ['2023 GS', '2021 GS', '2019 Champions']},
    },
    'DR Congo': {
        'fifa_rank': 52,
        'wc':   {'best': 'GS (as Zaire, 1974)', 'recent': ['1974 GS']},
        'cont': {'name': 'AFCON', 'best': 'Champions (2× as Zaire)', 'recent': ['2023 SF', '2021 R16', '2019 QF']},
    },
    'South Africa': {
        'fifa_rank': 58,
        'wc':   {'best': 'GS', 'recent': ['2010 GS (host)', '2002 GS', '1998 GS']},
        'cont': {'name': 'AFCON', 'best': 'Champions (1996)', 'recent': ['2023 SF', '2021 DNQ', '2019 SF']},
    },
    'Tunisia': {
        'fifa_rank': 30,
        'wc':   {'best': 'GS', 'recent': ['2022 GS', '2018 GS', '2006 GS']},
        'cont': {'name': 'AFCON', 'best': 'Champions (2004)', 'recent': ['2023 QF', '2021 SF', '2019 QF']},
    },
    'Cape Verde': {
        'fifa_rank': 80,
        'wc':   {'best': 'GS (debut 2026)', 'recent': ['2026 debut']},
        'cont': {'name': 'AFCON', 'best': 'QF', 'recent': ['2023 QF', '2021 QF', '2019 DNQ']},
    },

    # ── AFC (Asia / Middle East) ───────────────────────────────────────────────
    'Japan': {
        'fifa_rank': 18,
        'wc':   {'best': 'R16', 'recent': ['2022 R16', '2018 R16', '2014 GS']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (4×)', 'recent': ['2023 QF', '2019 Champions', '2015 Final (RU)']},
    },
    'South Korea': {
        'fifa_rank': 22,
        'wc':   {'best': 'SF (2002)', 'recent': ['2022 R16', '2018 GS', '2014 R16']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (2×)', 'recent': ['2023 Final (RU)', '2019 QF', '2015 Final (RU)']},
    },
    'Iran': {
        'fifa_rank': 25,
        'wc':   {'best': 'GS', 'recent': ['2022 GS', '2018 GS', '2014 GS']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (3×)', 'recent': ['2023 SF', '2019 R16', '2015 SF']},
    },
    'Saudi Arabia': {
        'fifa_rank': 55,
        'wc':   {'best': 'R16 (1994)', 'recent': ['2022 R16', '2018 GS', '2006 GS']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (3×)', 'recent': ['2023 QF', '2019 QF', '2015 GS']},
    },
    'Australia': {
        'fifa_rank': 25,
        'wc':   {'best': 'QF (2006)', 'recent': ['2022 R16', '2018 GS', '2014 GS']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (2015)', 'recent': ['2023 Final (RU)', '2019 R16', '2015 Champions']},
    },
    'Qatar': {
        'fifa_rank': 35,
        'wc':   {'best': 'GS', 'recent': ['2022 GS (host)', '2026 —']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (2×)', 'recent': ['2023 Champions', '2019 Champions', '2015 QF']},
    },
    'Jordan': {
        'fifa_rank': 87,
        'wc':   {'best': 'GS (debut 2026)', 'recent': ['2026 debut']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (2023)', 'recent': ['2023 Champions', '2019 QF', '2015 GS']},
    },
    'Uzbekistan': {
        'fifa_rank': 65,
        'wc':   {'best': 'GS (debut 2026)', 'recent': ['2026 debut']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'QF', 'recent': ['2023 QF', '2019 QF', '2015 GS']},
    },
    'Iraq': {
        'fifa_rank': 63,
        'wc':   {'best': 'GS (1986)', 'recent': ['1986 GS']},
        'cont': {'name': 'AFC Asian Cup', 'best': 'Champions (2007)', 'recent': ['2023 SF', '2019 R16', '2015 QF']},
    },

    # ── OFC (Oceania) ─────────────────────────────────────────────────────────
    'New Zealand': {
        'fifa_rank': 96,
        'wc':   {'best': 'GS (2010)', 'recent': ['2010 GS', '1982 GS']},
        'cont': {'name': 'OFC Nations Cup', 'best': 'Champions (6×)', 'recent': ['2024 Champions', '2022 Champions', '2016 Champions']},
    },
}


def format_team_intel(team: str) -> str | None:
    """Return a one-line context string for a team, or None if not found."""
    d = TEAM_INTEL.get(team)
    if not d:
        return None
    rank  = d['fifa_rank']
    wc    = d['wc']
    cont  = d['cont']
    wc_recent  = ', '.join(wc['recent'])
    cont_recent = ', '.join(cont['recent'])
    return (
        f"{team} (FIFA #{rank}) | "
        f"WC best: {wc['best']} — recent: {wc_recent} | "
        f"{cont['name']} best: {cont['best']} — recent: {cont_recent}"
    )


def build_intel_block(home: str, away: str) -> str:
    """Return an INTERNATIONAL CONTEXT block for injection into a research prompt."""
    h = format_team_intel(home)
    a = format_team_intel(away)
    if not h and not a:
        return ''
    lines = ['INTERNATIONAL CONTEXT (use to calibrate probabilities):']
    if h:
        lines.append(f'  Home — {h}')
    if a:
        lines.append(f'  Away — {a}')
    lines.append('')
    return '\n'.join(lines)


INTERNATIONAL_COMPETITIONS = {
    'World Cup 2026',
    'World Cup',
    'UEFA Euro',
    'AFCON',
    'Copa América',
    'AFC Asian Cup',
    'Gold Cup',
    'OFC Nations Cup',
    'Nations League',
}


def is_international(competition: str) -> bool:
    """True if the competition is an international (national-team) fixture."""
    return any(c.lower() in competition.lower() for c in INTERNATIONAL_COMPETITIONS)
