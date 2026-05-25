#!/usr/bin/env node
//
// Auto-fetch FIFA World Cup 2026 fixtures from api-football.com
// Mirrors fetch-fixtures.js but targets a different data source because
// football-data.org's free tier does not include the World Cup.
//
// Env:
//   API_FOOTBALL_KEY   — required (https://www.api-football.com/, free tier)
//   WC_SEASON          — optional, default 2026
//

const fs = require('fs');
const path = require('path');

const API_KEY = process.env.API_FOOTBALL_KEY;
if (!API_KEY) {
  console.error('API_FOOTBALL_KEY not set');
  process.exit(2);
}

const SEASON    = parseInt(process.env.WC_SEASON || '2026', 10);
const LEAGUE_ID = 1;                  // 1 = FIFA World Cup on api-football.com
const TZ        = 'Europe/London';    // display timezone for kick-off times

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

async function fetchWorldCupFixtures() {
  const url = `https://v3.football.api-sports.io/fixtures?league=${LEAGUE_ID}&season=${SEASON}`;
  const r = await fetch(url, { headers: { 'x-apisports-key': API_KEY } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  const j = await r.json();
  if (j.errors && Object.keys(j.errors).length) {
    throw new Error(`API errors: ${JSON.stringify(j.errors)}`);
  }
  return j.response || [];
}

// Build the JS object literal for a fixture stub. Uses the new schema
// (homeWin/draw/awayWin) with a neutral 33/34/33 split, plus a momentum
// factor — same format produced by fetch-fixtures.js post-fix so the
// renderer + agent treat World Cup fixtures identically.
function formatFixtureLiteral(f) {
  return `      {
        day: '${escapeJs(f.day)}',
        home: '${escapeJs(f.home)}', away: '${escapeJs(f.away)}', time: '${f.time}',
        result: null, homeWin: 33, draw: 34, awayWin: 33, verdict: 'Low', fairOdds: '3.00–3.40',
        factors: {
          formBalance:   { score: 50, detail: 'Pending research.' },
          momentum:      { score: 50, detail: 'Pending research.' },
          headToHead:    { score: 50, detail: 'Pending research.' },
          goalTendency:  { score: 50, detail: 'Pending research.' },
          leagueContext: { score: 50, detail: 'Pending research.' }
        },
        summary: 'Pending deep research.'
      }`;
}

// Walk through HTML to find the closing ']' of the World Cup fixtures
// array, with bracket counting that's aware of strings and escapes.
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

function addFeaturesEntry(features, version, added) {
  const entry = `- **${version}** — Auto-fetched ${added} World Cup 2026 fixture stubs.\n`;
  return features.replace(/(## Done\r?\n\r?\n)/, `$1${entry}`);
}

(async () => {
  const root = path.join(__dirname, '..');
  const indexPath = path.join(root, 'index.html');
  const featuresPath = path.join(root, 'FEATURES.md');

  let html = fs.readFileSync(indexPath, 'utf8');
  let features = fs.readFileSync(featuresPath, 'utf8');

  console.log(`Fetching World Cup ${SEASON} fixtures from api-football.com...`);
  let apiFixtures;
  try {
    apiFixtures = await fetchWorldCupFixtures();
  } catch (e) {
    console.error(`✗ Fetch failed: ${e.message}`);
    process.exit(1);
  }
  console.log(`  ${apiFixtures.length} fixtures returned from API`);

  if (!apiFixtures.length) {
    console.log('No fixtures available yet — schedule may not be published.');
    return;
  }

  // Load existing World Cup fixtures so we can preserve any already
  // researched / marked, and only ADD genuinely new ones.
  const LEAGUES = loadLeagues(html);
  const wc = LEAGUES.find(l => l.id === 'worldcup');
  if (!wc) throw new Error("No 'worldcup' league found in index.html");
  const existing = wc.fixtures || [];

  const seen = new Set(existing.map(f => `${f.home}|${f.away}|${f.day}`));
  const mapped = apiFixtures
    .filter(m => m.teams && m.teams.home && m.teams.away)
    .map(m => {
      const { day, time } = localParts(m.fixture.date, TZ);
      return {
        day,
        time,
        home: m.teams.home.name,
        away: m.teams.away.name,
        result: null,
      };
    });

  const fresh = mapped.filter(f => !seen.has(`${f.home}|${f.away}|${f.day}`));
  console.log(`  ${fresh.length} new fixtures to insert (${mapped.length - fresh.length} already known)`);

  if (!fresh.length) {
    console.log('Nothing to add.');
    return;
  }

  // Combine existing + new, sort by date for tidy rendering
  const combined = [...existing, ...fresh].sort((a, b) => {
    const da = `${a.day}T${a.time}`;
    const db = `${b.day}T${b.time}`;
    return da.localeCompare(db);
  });

  html = replaceFixtures(html, 'worldcup', combined);

  const bumped = bumpVersion(html);
  html = refreshDataTimestamp(bumped.html);
  features = addFeaturesEntry(features, bumped.version, fresh.length);

  fs.writeFileSync(indexPath, html);
  fs.writeFileSync(featuresPath, features);

  console.log(`\nAdded ${fresh.length} stubs → ${bumped.version}`);
})().catch(e => { console.error('Fatal:', e); process.exit(2); });
