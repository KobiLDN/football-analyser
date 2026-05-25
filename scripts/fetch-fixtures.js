#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.FOOTBALL_DATA_API_KEY;
if (!API_KEY) {
  console.error('FOOTBALL_DATA_API_KEY not set');
  process.exit(2);
}

// How many days ahead to fetch. Defaults to 8 (next week).
const DAYS_AHEAD = parseInt(process.env.DAYS_AHEAD || '8', 10);

const COMP = {
  pl: 'PL', laliga: 'PD', seriea: 'SA',
  bundesliga: 'BL1', ligue1: 'FL1', ucl: 'CL'
};

const TZ = {
  pl: 'Europe/London', laliga: 'Europe/Madrid', seriea: 'Europe/Rome',
  bundesliga: 'Europe/Berlin', ligue1: 'Europe/Paris', ucl: 'Europe/London'
};

const MONTHS = {
  January:0, February:1, March:2, April:3, May:4, June:5,
  July:6, August:7, September:8, October:9, November:10, December:11
};

function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
function escapeJs(s) { return (s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'"); }

function loadLeagues(html) {
  const m = html.match(/const LEAGUES = (\[[\s\S]*?\n\]);/);
  if (!m) throw new Error('Could not extract LEAGUES from index.html');
  return eval(m[1]);
}

function localParts(utcIso, tz) {
  const d = new Date(utcIso);
  const fmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: tz, weekday: 'long', day: 'numeric', month: 'long',
    hour: '2-digit', minute: '2-digit', hour12: false
  }).formatToParts(d);
  const get = t => fmt.find(p => p.type === t).value;
  return {
    day: `${get('weekday')} ${get('day')} ${get('month')}`,
    time: `${get('hour')}:${get('minute')}`
  };
}

function teamLabel(t) {
  // Prefer shortName, but use the full name if it's clearly a recognisable form
  const sn = (t.shortName || '').trim();
  const n = (t.name || '').trim();
  // Strip noise suffixes from full name for a cleaner label
  let preferred = sn || n;
  // If shortName is a less common variant (e.g. "Brighton Hove"), fall back to a stripped name
  if (sn && /\bhove\b/i.test(sn)) preferred = n.replace(/ FC$/i, '');
  return preferred;
}

async function fetchScheduled(comp, dateFrom, dateTo) {
  const url = `https://api.football-data.org/v4/competitions/${comp}/matches?status=SCHEDULED,TIMED&dateFrom=${dateFrom}&dateTo=${dateTo}`;
  const r = await fetch(url, { headers: { 'X-Auth-Token': API_KEY } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return j.matches || [];
}

function formatFixtureLiteral(f) {
  const rs = f.result === null ? 'null' : `'${escapeJs(f.result)}'`;
  const verd = f.verdict ? `'${escapeJs(f.verdict)}'` : "'Low'";
  const odds = f.fairOdds ? `'${escapeJs(f.fairOdds)}'` : "'4.00\u20134.50'";

  // Probability fields \u2014 emit new schema (homeWin/draw/awayWin) if any of
  // them exist, otherwise fall back to legacy drawProbability so really old
  // fixtures still serialize. Stub fixtures created by THIS script use the
  // new schema with neutral 33/34/33.
  const hasNew = f.homeWin !== undefined || f.draw !== undefined || f.awayWin !== undefined;
  const probBlock = hasNew
    ? `homeWin: ${f.homeWin ?? 33}, draw: ${f.draw ?? 34}, awayWin: ${f.awayWin ?? 33}`
    : `drawProbability: ${f.drawProbability ?? 25}`;

  // Optional form-dot fields (Understat-derived, last 5 W/D/L per team).
  const homeFormBlock = f.homeForm ? `\n        homeForm: '${escapeJs(f.homeForm)}',` : '';
  const awayFormBlock = f.awayForm ? `\n        awayForm: '${escapeJs(f.awayForm)}',` : '';

  // Factor block \u2014 accept either the new 'momentum' name or the legacy
  // 'drawRates' name, and emit whichever the fixture currently uses so we
  // don't silently rename / lose data.
  const fb  = f.factors?.formBalance    || { score: 50, detail: 'Pending research.' };
  const mom = f.factors?.momentum;
  const dr  = f.factors?.drawRates;
  const h2h = f.factors?.headToHead     || { score: 50, detail: 'Pending research.' };
  const gt  = f.factors?.goalTendency   || { score: 50, detail: 'Pending research.' };
  const lc  = f.factors?.leagueContext  || { score: 50, detail: 'Pending research.' };

  // Prefer momentum (new schema). Fall back to drawRates. Default if neither.
  const tempo = mom || dr || { score: 50, detail: 'Pending research.' };
  const tempoName = mom ? 'momentum' : (dr ? 'drawRates' : 'momentum');
  const tempoLabel = tempoName === 'momentum' ? 'momentum:     ' : 'drawRates:    ';

  const sum = f.summary ? `'${escapeJs(f.summary)}'` : "'Pending deep research.'";

  // Serialize teamNews if present
  let teamNewsBlock = '';
  if (f.teamNews) {
    const serializeItems = items => {
      if (!items || !items.length) return '[]';
      return `[\n${items.map(i => `              { tag: '${escapeJs(i.tag)}', text: '${escapeJs(i.text)}' }`).join(',\n')}\n            ]`;
    };
    teamNewsBlock = `,\n        teamNews: {\n          home: ${serializeItems(f.teamNews.home)},\n          away: ${serializeItems(f.teamNews.away)}\n        }`;
  }

  // Serialize context if present
  const contextBlock = f.context ? `,\n        context: '${escapeJs(f.context)}'` : '';

  // Serialize bookOdds if present
  const bookOddsBlock = f.bookOdds != null ? `,\n        bookOdds: ${f.bookOdds}` : '';

  return `      {
        day: '${escapeJs(f.day)}',
        home: '${escapeJs(f.home)}', away: '${escapeJs(f.away)}', time: '${f.time}',
        result: ${rs}, ${probBlock}, verdict: ${verd}, fairOdds: ${odds},${homeFormBlock}${awayFormBlock}
        factors: {
          formBalance:   { score: ${fb.score}, detail: '${escapeJs(fb.detail)}' },
          ${tempoLabel} { score: ${tempo.score}, detail: '${escapeJs(tempo.detail)}' },
          headToHead:    { score: ${h2h.score}, detail: '${escapeJs(h2h.detail)}' },
          goalTendency:  { score: ${gt.score}, detail: '${escapeJs(gt.detail)}' },
          leagueContext: { score: ${lc.score}, detail: '${escapeJs(lc.detail)}' }
        }${teamNewsBlock}${contextBlock}${bookOddsBlock},
        summary: ${sum}
      }`;
}

// Walk through HTML to find the closing ']' of a league's fixtures array, with bracket counting
// that's aware of strings and escapes.
function findFixturesClose(html, leagueId) {
  const idMatch = html.match(new RegExp(`id: '${escapeRegex(leagueId)}'`));
  if (!idMatch) return -1;
  const fixIdx = html.indexOf('fixtures: [', idMatch.index);
  if (fixIdx === -1) return -1;
  let depth = 1;
  let pos = fixIdx + 'fixtures: ['.length;
  while (pos < html.length && depth > 0) {
    const c = html[pos];
    if (c === "'" || c === '"' || c === '`') {
      const quote = c;
      pos++;
      while (pos < html.length) {
        if (html[pos] === '\\') { pos += 2; continue; }
        if (html[pos] === quote) { pos++; break; }
        pos++;
      }
      continue;
    }
    if (c === '/' && html[pos + 1] === '/') {
      while (pos < html.length && html[pos] !== '\n') pos++;
      continue;
    }
    if (c === '[') depth++;
    else if (c === ']') {
      depth--;
      if (depth === 0) return pos;
    }
    pos++;
  }
  return -1;
}

function replaceFixtures(html, leagueId, newFixturesArray) {
  const idMatch = html.match(new RegExp(`id: '${escapeRegex(leagueId)}'`));
  if (!idMatch) throw new Error(`Could not find league id ${leagueId}`);
  const fixIdx = html.indexOf('fixtures: [', idMatch.index);
  if (fixIdx === -1) throw new Error(`Could not find fixtures array for ${leagueId}`);
  const startPos = fixIdx + 'fixtures: ['.length;
  
  const closeIdx = findFixturesClose(html, leagueId);
  if (closeIdx === -1) throw new Error(`Could not find close for ${leagueId}`);
  
  const fixturesText = newFixturesArray.map(formatFixtureLiteral).join(',\n\n');
  const insertion = newFixturesArray.length ? `\n\n${fixturesText}\n    ` : '';
  
  return html.slice(0, startPos) + insertion + html.slice(closeIdx);
}

function bumpVersion(html) {
  // Tolerate either '·' (middle dot) or '–' (en dash) as separator
  const m = html.match(/<span>v(\d+)\.(\d+) ([·–-]) 2025–26<\/span>/);
  if (!m) throw new Error('Could not find version in topbar');
  const next = `${m[1]}.${+m[2] + 1}`;
  const sep = m[3];
  return {
    html: html.replace(m[0], `<span>v${next} ${sep} 2025–26</span>`),
    version: `v${next}`
  };
}

function refreshDataTimestamp(html) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: false
  }).formatToParts(new Date());
  const get = t => parts.find(p => p.type === t).value;
  const ts = `${get('day')} ${get('month')} ${get('year')} ${get('hour')}:${get('minute')} BST`;
  return html.replace(/<div class="updated-tag">Data · [^<]+<\/div>/, `<div class="updated-tag">Data · ${ts}</div>`);
}

function addFeaturesEntry(features, version, totalAdded, totalPruned) {
  const msgAdded = totalAdded ? `Auto-fetched ${totalAdded} upcoming fixture stubs.` : '';
  const msgPruned = totalPruned ? `Pruned ${totalPruned} old fixtures.` : '';
  const msg = [msgAdded, msgPruned].filter(Boolean).join(' ');
  const entry = `- **${version}** — ${msg}\n`;
  return features.replace(/(## Done\r?\n\r?\n)/, `$1${entry}`);
}

function isTooOld(dayStr) {
  const parts = dayStr.split(/\\s+/);
  if (parts.length < 3) return false;
  const dd = +parts[1];
  const m = MONTHS[parts[2]];
  if (m === undefined) return false;
  
  const today = new Date();
  const year = today.getFullYear();
  let fixDate = new Date(Date.UTC(year, m, dd));
  
  // Wrap around for year boundaries
  if (fixDate > new Date(today.getTime() + 180 * 24 * 60 * 60 * 1000)) {
    fixDate = new Date(Date.UTC(year - 1, m, dd));
  }
  
  const diffDays = (today.getTime() - fixDate.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays > 7;
}

(async () => {
  const root = path.join(__dirname, '..');
  const indexPath = path.join(root, 'index.html');
  const featuresPath = path.join(root, 'FEATURES.md');

  let html = fs.readFileSync(indexPath, 'utf8');
  let features = fs.readFileSync(featuresPath, 'utf8');

  const LEAGUES = loadLeagues(html);

  // Compute date range: tomorrow → tomorrow + DAYS_AHEAD
  const start = new Date();
  start.setUTCDate(start.getUTCDate() + 1);
  const end = new Date(start);
  end.setUTCDate(end.getUTCDate() + DAYS_AHEAD);
  const dateFrom = start.toISOString().slice(0, 10);
  const dateTo = end.toISOString().slice(0, 10);

  console.log(`Fetching fixtures from ${dateFrom} → ${dateTo}`);

  const perLeague = [];
  let totalPruned = 0;

  for (const league of LEAGUES) {
    const comp = COMP[league.id];
    const tz = TZ[league.id];
    
    // 1. Prune existing old fixtures
    const keptFixtures = [];
    let prunedInLeague = 0;
    for (const f of league.fixtures) {
      if (isTooOld(f.day)) {
        prunedInLeague++;
      } else {
        keptFixtures.push(f);
      }
    }
    totalPruned += prunedInLeague;

    if (!comp) {
      console.log(`-- skip ${league.name} (not on free tier). Pruned ${prunedInLeague}.`);
      html = replaceFixtures(html, league.id, keptFixtures);
      continue;
    }

    let api;
    try {
      api = await fetchScheduled(comp, dateFrom, dateTo);
    } catch (e) {
      console.error(`✗ ${league.name}: ${e.message}`);
      html = replaceFixtures(html, league.id, keptFixtures);
      continue;
    }

    // Build a Set of kept (home|away|day) keys to dedupe
    const existing = new Set(keptFixtures.map(f => `${f.home}|${f.away}|${f.day}`));

    const fresh = [];
    if (api.length) {
      for (const m of api) {
        const parts = localParts(m.utcDate, tz);
        const home = teamLabel(m.homeTeam);
        const away = teamLabel(m.awayTeam);
        const key = `${home}|${away}|${parts.day}`;
        if (existing.has(key)) continue;
        fresh.push({ home, away, day: parts.day, time: parts.time });
        existing.add(key);
      }
    }

    console.log(`+ ${league.name}: ${fresh.length} new fixtures, ${prunedInLeague} pruned.`);
    if (fresh.length) {
      fresh.forEach(f => console.log(`    ${f.day} ${f.time}  ${f.home} vs ${f.away}`));
    }

    const mergedFixtures = keptFixtures.concat(fresh);
    html = replaceFixtures(html, league.id, mergedFixtures);
    perLeague.push({ league: league.name, count: fresh.length });
  }

  const totalAdded = perLeague.reduce((s, p) => s + p.count, 0);

  if (totalAdded === 0 && totalPruned === 0) {
    console.log('\nNothing new to add or prune.');
    return;
  }

  const bumped = bumpVersion(html);
  html = refreshDataTimestamp(bumped.html);
  features = addFeaturesEntry(features, bumped.version, totalAdded, totalPruned);

  fs.writeFileSync(indexPath, html);
  fs.writeFileSync(featuresPath, features);

  const total = perLeague.reduce((s, p) => s + p.count, 0);
  console.log(`\nAdded ${total} fixtures → ${bumped.version}`);
})().catch(e => { console.error('Fatal:', e); process.exit(2); });
