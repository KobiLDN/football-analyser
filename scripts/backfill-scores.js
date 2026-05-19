#!/usr/bin/env node
// One-off backfill: replaces old-format result fields ('home'|'draw'|'away')
// with actual scorelines (e.g. '2-1') by querying football-data.org.
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.FOOTBALL_DATA_API_KEY;
if (!API_KEY) {
  console.error('FOOTBALL_DATA_API_KEY not set');
  process.exit(2);
}

const COMP = {
  pl: 'PL', laliga: 'PD', seriea: 'SA',
  bundesliga: 'BL1', ligue1: 'FL1', ucl: 'CL'
};

const MONTHS = {
  January:0, February:1, March:2, April:3, May:4, June:5,
  July:6, August:7, September:8, October:9, November:10, December:11
};

function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function loadLeagues(html) {
  const m = html.match(/const LEAGUES = (\[[\s\S]*?\n\]);/);
  if (!m) throw new Error('Could not extract LEAGUES from index.html');
  return eval(m[1]);
}

function normTeam(s) {
  let n = s.toLowerCase().trim().replace(/&/g, ' and ');
  if (/^man united$|^man utd$/.test(n)) n = 'manchester united';
  else if (/^man city$/.test(n)) n = 'manchester city';
  else if (/^wolves$/.test(n)) n = 'wolverhampton';
  else if (/^spurs$/.test(n)) n = 'tottenham';
  n = n
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\b(fc|afc|cf|sc|bk|club|wanderers|hotspur|albion|hove|and)\b/g, '')
    .replace(/\s+/g, ' ').trim();
  return n;
}

function teamMatch(apiTeam, repoName) {
  const cands = [apiTeam.shortName, apiTeam.name].filter(Boolean);
  const nb = normTeam(repoName);
  if (!nb) return false;
  return cands.some(c => {
    const na = normTeam(c);
    return na && (na === nb || na.includes(nb) || nb.includes(na));
  });
}

async function fetchFinished(comp, dateFrom, dateTo) {
  const url = `https://api.football-data.org/v4/competitions/${comp}/matches?status=FINISHED&dateFrom=${dateFrom}&dateTo=${dateTo}`;
  const r = await fetch(url, { headers: { 'X-Auth-Token': API_KEY } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return j.matches || [];
}

// Replace `result: 'home'|'away'|'draw'` with `result: 'X-Y'` for a specific fixture.
function patchOldResult(html, fixture, scoreStr) {
  const homeEsc = escapeRegex(fixture.home);
  const awayEsc = escapeRegex(fixture.away);
  const dayEsc = escapeRegex(fixture.day);
  const pattern = new RegExp(
    `(day: '${dayEsc}'[\\s\\S]*?home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?)result: '(home|away|draw)'`
  );
  if (!pattern.test(html)) {
    throw new Error(`Could not locate fixture: ${fixture.home} vs ${fixture.away} on ${fixture.day}`);
  }
  return html.replace(pattern, `$1result: '${scoreStr}'`);
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

function addFeaturesEntry(features, version, count) {
  const noun = count === 1 ? 'result' : 'results';
  const entry = `- **${version}** — Backfilled ${count} legacy ${noun} with actual scorelines (replaced \`'home'\`/\`'draw'\`/\`'away'\` with \`'X-Y'\`).\n`;
  return features.replace(/(## Done\r?\n\r?\n)/, `$1${entry}`);
}

(async () => {
  const root = path.join(__dirname, '..');
  const indexPath = path.join(root, 'index.html');
  const featuresPath = path.join(root, 'FEATURES.md');

  let html = fs.readFileSync(indexPath, 'utf8');
  let features = fs.readFileSync(featuresPath, 'utf8');

  const LEAGUES = loadLeagues(html);
  let backfilled = 0;

  for (const league of LEAGUES) {
    const comp = COMP[league.id];
    if (!comp) continue;
    const oldFormat = league.fixtures.filter(f =>
      f.result && !String(f.result).includes('-') &&
      ['home', 'away', 'draw'].includes(f.result)
    );
    if (!oldFormat.length) continue;

    // Build a wide date window covering all old-format fixtures in this league
    const year = new Date().getFullYear();
    const ms = oldFormat.map(f => MONTHS[f.day.split(/\s+/)[2]]);
    const ds = oldFormat.map(f => +f.day.split(/\s+/)[1]);
    // Widen by a few days to handle year boundaries / time zones
    const minD = new Date(Date.UTC(year, Math.min(...ms), Math.min(...ds) - 2));
    const maxD = new Date(Date.UTC(year, Math.max(...ms), Math.max(...ds) + 2));
    const dateFrom = minD.toISOString().slice(0, 10);
    const dateTo = maxD.toISOString().slice(0, 10);

    let api;
    try {
      api = await fetchFinished(comp, dateFrom, dateTo);
    } catch (e) {
      console.error(`✗ ${league.name}: ${e.message}`);
      continue;
    }
    if (!api.length) {
      console.log(`-- ${league.name}: no FINISHED matches in window`);
      continue;
    }

    for (const f of oldFormat) {
      const m = api.find(x => teamMatch(x.homeTeam, f.home) && teamMatch(x.awayTeam, f.away));
      if (!m || m.status !== 'FINISHED') {
        console.log(`-- not found: ${f.home} vs ${f.away} (${f.day})`);
        continue;
      }
      const hs = m.score?.fullTime?.home;
      const as = m.score?.fullTime?.away;
      if (hs == null || as == null) continue;
      const scoreStr = `${hs}-${as}`;
      try {
        html = patchOldResult(html, f, scoreStr);
        backfilled++;
        console.log(`✓ ${f.home} ${scoreStr} ${f.away} (was '${f.result}')`);
      } catch (e) {
        console.error(`✗ ${e.message}`);
      }
    }
  }

  if (!backfilled) {
    console.log('Nothing to backfill.');
    return;
  }

  const bumped = bumpVersion(html);
  html = refreshDataTimestamp(bumped.html);
  features = addFeaturesEntry(features, bumped.version, backfilled);

  fs.writeFileSync(indexPath, html);
  fs.writeFileSync(featuresPath, features);

  console.log(`\nBackfilled ${backfilled} → ${bumped.version}`);
})().catch(e => { console.error('Fatal:', e); process.exit(2); });
