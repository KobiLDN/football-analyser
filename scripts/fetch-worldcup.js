#!/usr/bin/env node
//
// Auto-fetch FIFA World Cup 2026 fixtures from openfootball/worldcup.json
// (https://github.com/openfootball/worldcup.json) — free, public-domain,
// no API key required. Maps openfootball's JSON shape to our fixture format
// and merges into the 'worldcup' league in index.html.
//
// Env:
//   WC_SEASON   — optional, default 2026 (controls which subdirectory to fetch)
//

const fs = require('fs');
const path = require('path');

const SEASON     = parseInt(process.env.WC_SEASON || '2026', 10);
const SOURCE_URL = `https://raw.githubusercontent.com/openfootball/worldcup.json/master/${SEASON}/worldcup.json`;
const DISPLAY_TZ = 'Europe/London';   // kick-off times displayed in UK time

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

// Parse openfootball's "HH:MM UTC±N" and the date string into a real Date,
// then format for display in DISPLAY_TZ. Examples:
//   "2026-06-11" + "13:00 UTC-6"  →  Date(2026-06-11 13:00 UTC-6)
//   "2026-06-11" + "20:00"        →  treat naïve as UTC
function parseOpenfootballDate(dateStr, timeStr) {
  // Match "HH:MM" optionally followed by " UTC±N" or " UTC±N:MM"
  const m = (timeStr || '').match(/^(\d{1,2}):(\d{2})(?:\s*UTC([+-]\d{1,2})(?::?(\d{2}))?)?/);
  if (!m) return null;
  const [, hh, mm, tzH, tzM] = m;
  const offsetMin = tzH ? (parseInt(tzH, 10) * 60 + (tzM ? parseInt(tzM, 10) : 0)) : 0;
  // Build a UTC Date by subtracting the venue's offset from the local time.
  // e.g. 13:00 UTC-6 → UTC is 13:00 + 6h = 19:00
  const [y, mo, d] = dateStr.split('-').map(Number);
  const utcMs = Date.UTC(y, mo - 1, d, parseInt(hh, 10), parseInt(mm, 10)) - offsetMin * 60 * 1000;
  return new Date(utcMs);
}

function localParts(date, tz) {
  const fmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: tz, weekday: 'long', day: 'numeric', month: 'long',
    hour: '2-digit', minute: '2-digit', hour12: false
  }).formatToParts(date);
  const get = t => fmt.find(p => p.type === t).value;
  return {
    day:  `${get('weekday')} ${get('day')} ${get('month')}`,
    time: `${get('hour')}:${get('minute')}`,
  };
}

async function fetchOpenfootball() {
  const r = await fetch(SOURCE_URL);
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  return r.json();
}

// Serialize a fixture, preserving existing research fields if present.
// New stubs get neutral 33/34/33 placeholder values until auto-research runs.
function formatFixtureLiteral(f) {
  const resultStr = f.result === null ? 'null' : `'${escapeJs(f.result)}'`;

  const homeWin  = f.homeWin  ?? 33;
  const draw     = f.draw     ?? 34;
  const awayWin  = f.awayWin  ?? 33;
  const verdict  = f.verdict  || 'Low';
  const fairOdds = f.fairOdds || '3.00–3.40';

  const homeFormBlock = f.homeForm ? `\n        homeForm: '${escapeJs(f.homeForm)}',` : '';
  const awayFormBlock = f.awayForm ? `\n        awayForm: '${escapeJs(f.awayForm)}',` : '';

  const fb  = f.factors?.formBalance   || { score: 50, detail: 'Pending deep research.' };
  const mom = f.factors?.momentum      || { score: 50, detail: 'Pending deep research.' };
  const h2h = f.factors?.headToHead    || { score: 50, detail: 'Pending deep research.' };
  const gt  = f.factors?.goalTendency  || { score: 50, detail: 'Pending deep research.' };
  const lc  = f.factors?.leagueContext || { score: 50, detail: 'Pending deep research.' };

  const serializeItems = items => {
    if (!items || !items.length) return '[]';
    return `[\n${items.map(i => `              { tag: '${escapeJs(i.tag)}', text: '${escapeJs(i.text)}' }`).join(',\n')}\n            ]`;
  };

  const teamNewsBlock = f.teamNews
    ? `,\n        teamNews: {\n          home: ${serializeItems(f.teamNews.home)},\n          away: ${serializeItems(f.teamNews.away)}\n        }`
    : '';

  const contextBlock = f.context ? `,\n        context: '${escapeJs(f.context)}'` : '';
  const summary = f.summary ? `'${escapeJs(f.summary)}'` : "'Pending deep research.'";

  return `      {
        day: '${escapeJs(f.day)}',
        home: '${escapeJs(f.home)}', away: '${escapeJs(f.away)}', time: '${f.time}',
        result: ${resultStr}, homeWin: ${homeWin}, draw: ${draw}, awayWin: ${awayWin}, verdict: '${escapeJs(verdict)}', fairOdds: '${escapeJs(fairOdds)}',${homeFormBlock}${awayFormBlock}
        factors: {
          formBalance:   { score: ${fb.score}, detail: '${escapeJs(fb.detail)}' },
          momentum:      { score: ${mom.score}, detail: '${escapeJs(mom.detail)}' },
          headToHead:    { score: ${h2h.score}, detail: '${escapeJs(h2h.detail)}' },
          goalTendency:  { score: ${gt.score}, detail: '${escapeJs(gt.detail)}' },
          leagueContext: { score: ${lc.score}, detail: '${escapeJs(lc.detail)}' }
        }${teamNewsBlock}${contextBlock},
        summary: ${summary}
      }`;
}

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

function addFeaturesEntry(features, version, added, marked) {
  const parts = [];
  if (added)  parts.push(`Auto-fetched ${added} World Cup ${SEASON} fixture stubs.`);
  if (marked) parts.push(`Marked ${marked} World Cup result${marked === 1 ? '' : 's'}.`);
  const msg = parts.join(' ');
  if (!msg) return features;
  const entry = `- **${version}** — ${msg}\n`;
  return features.replace(/(## Done\r?\n\r?\n)/, `$1${entry}`);
}

(async () => {
  const root = path.join(__dirname, '..');
  const indexPath    = path.join(root, 'index.html');
  const featuresPath = path.join(root, 'FEATURES.md');

  let html     = fs.readFileSync(indexPath, 'utf8');
  let features = fs.readFileSync(featuresPath, 'utf8');

  console.log(`Fetching World Cup ${SEASON} fixtures from openfootball...`);
  let json;
  try {
    json = await fetchOpenfootball();
  } catch (e) {
    console.error(`✗ Fetch failed: ${e.message}`);
    process.exit(1);
  }
  const apiMatches = json.matches || [];
  console.log(`  ${apiMatches.length} matches returned`);

  if (!apiMatches.length) {
    console.log('No fixtures available yet.');
    return;
  }

  // Existing data — preserve previously researched / marked fixtures
  const LEAGUES = loadLeagues(html);
  const wc = LEAGUES.find(l => l.id === 'worldcup');
  if (!wc) throw new Error("No 'worldcup' league found in index.html");
  const existing = wc.fixtures || [];
  const byKey = new Map();
  existing.forEach(f => byKey.set(`${f.home}|${f.away}|${f.day}`, f));

  // Map openfootball matches to our format
  const mapped = apiMatches
    .map(m => {
      const date = parseOpenfootballDate(m.date, m.time);
      if (!date) return null;
      const { day, time } = localParts(date, DISPLAY_TZ);
      const result = (m.score && m.score.ft && Array.isArray(m.score.ft))
        ? `${m.score.ft[0]}-${m.score.ft[1]}`
        : null;
      return { day, time, home: m.team1, away: m.team2, result };
    })
    .filter(Boolean);

  let added = 0, marked = 0;
  const combined = mapped.map(m => {
    const key = `${m.home}|${m.away}|${m.day}`;
    const prior = byKey.get(key);
    if (!prior) {
      added++;
      return m;
    }
    // Preserve prior analysis fields; refresh only result if newly available
    if (!prior.result && m.result) marked++;
    return { ...prior, day: m.day, time: m.time, result: prior.result || m.result };
  });

  // Sort by date then time for tidy rendering
  combined.sort((a, b) => {
    const k = (f) => {
      const p = f.day.split(' ');           // ["Thursday", "11", "June"]
      return new Date(SEASON, MONTHS[p[2]] || 0, parseInt(p[1] || '1', 10),
                      parseInt(f.time.split(':')[0] || '0', 10),
                      parseInt(f.time.split(':')[1] || '0', 10)).getTime();
    };
    return k(a) - k(b);
  });

  console.log(`  ${added} new fixtures inserted, ${marked} previously-unplayed now have a score`);

  if (added === 0 && marked === 0) {
    console.log('Nothing to commit.');
    return;
  }

  html = replaceFixtures(html, 'worldcup', combined);
  const bumped = bumpVersion(html);
  html = refreshDataTimestamp(bumped.html);
  features = addFeaturesEntry(features, bumped.version, added, marked);

  fs.writeFileSync(indexPath, html);
  fs.writeFileSync(featuresPath, features);
  console.log(`\nSaved → ${bumped.version}`);
})().catch(e => { console.error('Fatal:', e); process.exit(2); });
