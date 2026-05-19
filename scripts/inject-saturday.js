#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const indexPath = path.join(__dirname, '..', 'index.html');
let html = fs.readFileSync(indexPath, 'utf8');

const research = {
  'Bremen|Dortmund': {
    drawProbability: 22, verdict: 'Low', fairOdds: '4.20\u20134.50',
    factors: {
      formBalance: { score: 35, detail: 'Dortmund are 2nd and finishing strongly. Bremen are 15th, fighting to avoid the relegation playoff.' },
      drawRates: { score: 40, detail: 'Dortmund have been decisive in results recently, with few draws.' },
      headToHead: { score: 35, detail: 'Dortmund have dominated this fixture historically.' },
      goalTendency: { score: 40, detail: 'Dortmund score freely; Bremen leak goals. A one-sided affair is likely.' },
      leagueContext: { score: 45, detail: 'Final day desperation for Bremen. Dortmund want to lock in 2nd place.' }
    },
    teamNews: {
      home: [
        { tag: 'out', text: 'Yukinari Sugawara \u2014 suspended (red card)' },
        { tag: 'out', text: 'Mitchell Weiser \u2014 knee injury' },
        { tag: 'out', text: 'Keke Topp \u2014 knee injury' },
        { tag: 'out', text: 'Leonardo Bittencourt \u2014 injured' },
        { tag: 'key', text: '15th place \u2014 fighting to avoid relegation playoff' }
      ],
      away: [
        { tag: 'out', text: 'Emre Can \u2014 knee injury (captain)' },
        { tag: 'out', text: 'Ramy Bensebaini \u2014 injury' },
        { tag: 'key', text: '2nd place \u2014 looking to secure final position' }
      ]
    },
    context: `Final day drama. Bremen are 15th and need a result to avoid the relegation playoff. They are missing key players through suspension and injury. Dortmund are comfortable in 2nd but will want to finish on a high. The desperation factor slightly increases draw chances, but Dortmund's quality should prevail.`,
    summary: 'Bremen are fighting for survival on the final day but are decimated by absences. Dortmund sit comfortably in 2nd with a far superior squad. A draw is unlikely given the quality gap.'
  },
  'Heidenheim|Mainz': {
    drawProbability: 30, verdict: 'Moderate', fairOdds: '3.20\u20133.40',
    factors: {
      formBalance: { score: 55, detail: 'Both teams are in poor form. Heidenheim lost 3-1 to Koln last week.' },
      drawRates: { score: 60, detail: 'Heidenheim have drawn frequently this season in tight, low-scoring games.' },
      headToHead: { score: 55, detail: 'Competitive recent meetings between these two sides.' },
      goalTendency: { score: 65, detail: 'Heidenheim play a defensive, low-block style. Low-scoring game expected.' },
      leagueContext: { score: 70, detail: 'Heidenheim are 17th on 26 points \u2014 fighting for their Bundesliga life. Mainz are safe in mid-table.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: '17th place, 26 points \u2014 must win to have any chance of survival' },
        { tag: 'key', text: 'Level on points with Wolfsburg (16th) and St. Pauli (18th)' }
      ],
      away: [
        { tag: 'key', text: 'Comfortable in mid-table with nothing to play for' }
      ]
    },
    context: `Heidenheim are in a three-way relegation battle (all on 26 pts with Wolfsburg and St. Pauli). They MUST win to have any chance. Mainz are safe and may field a rotated side. However, Heidenheim's defensive style often produces tight, low-scoring games that can easily end in a draw.`,
    summary: 'A relegation six-pointer for Heidenheim who are in a three-way battle on 26 points. Their defensive style often produces tight games. Mainz have nothing to play for. A nervous, cagey draw is very plausible.'
  },
  'Freiburg|RB Leipzig': {
    drawProbability: 24, verdict: 'Low', fairOdds: '3.80\u20134.20',
    factors: {
      formBalance: { score: 40, detail: 'Leipzig are 3rd with superior firepower. Freiburg are 7th with an inconsistent season.' },
      drawRates: { score: 45, detail: 'Leipzig tend to be decisive in results, winning or losing rather than drawing.' },
      headToHead: { score: 40, detail: 'Leipzig have a strong historical record against Freiburg.' },
      goalTendency: { score: 45, detail: 'Leipzig average nearly 2 goals per game. Expect them to be proactive.' },
      leagueContext: { score: 35, detail: 'Leipzig want to cement 3rd. Freiburg are playing for pride at home.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: '7th place \u2014 final home game of the season' }
      ],
      away: [
        { tag: 'key', text: '3rd place \u2014 looking to cement Champions League qualification' }
      ]
    },
    context: 'Leipzig arrive in strong form and need to protect their 3rd-place finish. Their high-energy, proactive style and superior firepower make them favourites. Freiburg will want to give their home fans a good send-off but lack the consistency to trouble Leipzig.',
    summary: `Leipzig are 3rd with strong attacking numbers and should be too much for an inconsistent Freiburg at home. A draw is possible but Leipzig's quality makes it unlikely.`
  },
  'Frankfurt|Stuttgart': {
    drawProbability: 28, verdict: 'Low', fairOdds: '3.40\u20133.60',
    factors: {
      formBalance: { score: 50, detail: 'Stuttgart are 4th and in form (beat Leverkusen 3-1). Frankfurt are 8th with 1 point from last 4.' },
      drawRates: { score: 50, detail: 'Both sides have had mixed results; draws are possible but not dominant.' },
      headToHead: { score: 55, detail: 'Competitive recent encounters between these two sides.' },
      goalTendency: { score: 55, detail: 'Stuttgart attack aggressively (Undav, Demirovic). Frankfurt leak goals defensively.' },
      leagueContext: { score: 60, detail: 'Stuttgart need a win to guarantee Champions League. Frankfurt chasing Conference League.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: '8th place \u2014 chasing Conference League qualification' },
        { tag: 'key', text: 'Only 1 point from last 4 league matches' }
      ],
      away: [
        { tag: 'key', text: '4th place \u2014 must win to guarantee Champions League spot' },
        { tag: 'key', text: 'In form: beat Leverkusen 3-1 last week' }
      ]
    },
    context: `Huge stakes for Stuttgart who need a win to guarantee a Champions League place. Their attack, led by Undav and Demirovic, has been electric. Frankfurt have been poor recently (1 point in 4) and are leaking goals, making them vulnerable. Both teams have something to play for, but Stuttgart's superior form and motivation tilt things their way.`,
    summary: `Stuttgart need a win for Champions League and arrive in superb form. Frankfurt have been poor with 1 point from 4. Both have stakes but Stuttgart's quality and motivation make a draw unlikely.`
  },
  'St. Pauli|Wolfsburg': {
    drawProbability: 32, verdict: 'Moderate', fairOdds: '3.00\u20133.20',
    factors: {
      formBalance: { score: 55, detail: 'Both teams are in the relegation zone, both desperate. Evenly poor form.' },
      drawRates: { score: 60, detail: 'Tight, nervy relegation games frequently end in draws.' },
      headToHead: { score: 55, detail: 'Competitive recent meetings; no dominant side.' },
      goalTendency: { score: 65, detail: 'Both teams score and concede few goals. A low-scoring, cagey affair is expected.' },
      leagueContext: { score: 75, detail: 'RELEGATION DECIDER. Both on 26 points. The loser goes down. A draw could send both down.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: '18th place, 26 points \u2014 currently in automatic relegation' },
        { tag: 'key', text: 'Level on points with Wolfsburg and Heidenheim' }
      ],
      away: [
        { tag: 'key', text: '16th place, 26 points \u2014 currently in relegation playoff spot' },
        { tag: 'key', text: 'Level on points with St. Pauli and Heidenheim' }
      ]
    },
    context: `The ultimate relegation showdown. St. Pauli (18th) host Wolfsburg (16th) with both teams on 26 points alongside Heidenheim (17th). A draw could be catastrophic for both sides depending on Heidenheim's result. The tension and fear of losing will produce a very cagey, tight encounter \u2014 classic relegation draw territory.`,
    summary: 'A relegation decider with both teams on 26 points. The fear factor and desperation create classic draw conditions. Both will be terrified of losing, making a cagey stalemate very plausible.'
  },
  'Union Berlin|Augsburg': {
    drawProbability: 30, verdict: 'Moderate', fairOdds: '3.20\u20133.40',
    factors: {
      formBalance: { score: 55, detail: 'Union are in decent form at home. Augsburg are a solid mid-table side with nothing to play for.' },
      drawRates: { score: 60, detail: 'Union Berlin are historically a draw-heavy team, especially at home.' },
      headToHead: { score: 60, detail: 'Recent meetings have been tight and low-scoring.' },
      goalTendency: { score: 65, detail: 'Union play a defensive, organised style. Goals will be at a premium.' },
      leagueContext: { score: 50, detail: 'Both teams are safe in mid-table. A dead rubber atmosphere.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: 'Safe in mid-table \u2014 final home game of the season' }
      ],
      away: [
        { tag: 'key', text: 'Safe in mid-table \u2014 nothing to play for' }
      ]
    },
    context: `A mid-table dead rubber between two sides with nothing on the line. Union's defensive, organised approach consistently produces low-scoring affairs, and Augsburg lack the firepower to break them down. Classic end-of-season draw material.`,
    summary: `Two safe mid-table sides in a dead rubber. Union's defensive style and Augsburg's lack of firepower point towards a low-scoring, forgettable draw.`
  },
  "M'gladbach|Hoffenheim": {
    drawProbability: 29, verdict: 'Low', fairOdds: '3.30\u20133.50',
    factors: {
      formBalance: { score: 50, detail: 'Both mid-table sides with inconsistent seasons.' },
      drawRates: { score: 55, detail: 'Both teams have drawn a fair share of matches this season.' },
      headToHead: { score: 55, detail: 'Competitive recent encounters; neither side dominates.' },
      goalTendency: { score: 50, detail: 'Both can score but are also defensively vulnerable. Could go either way.' },
      leagueContext: { score: 45, detail: 'Nothing on the line for either team. End-of-season dead rubber.' }
    },
    teamNews: {
      home: [
        { tag: 'key', text: 'Safe in mid-table \u2014 final home match of the season' }
      ],
      away: [
        { tag: 'key', text: 'Safe in mid-table \u2014 nothing to play for' }
      ]
    },
    context: 'Two mid-table sides with nothing to play for on the final day. Both have been inconsistent all season. The lack of motivation and end-of-season fatigue could produce a dull affair.',
    summary: 'A dead rubber between two safe mid-table sides. Neither has anything to play for, making this hard to call. A draw is possible but not strongly indicated.'
  },
  'Bayern|1. FC Köln': {
    drawProbability: 10, verdict: 'Low', fairOdds: '8.00\u20139.00',
    factors: {
      formBalance: { score: 15, detail: 'Bayern are champions with 86 points and 117 goals. Koln are 14th with awful away form.' },
      drawRates: { score: 15, detail: 'Bayern rarely draw at home, especially against weaker sides.' },
      headToHead: { score: 10, detail: 'A complete mismatch in quality.' },
      goalTendency: { score: 10, detail: 'Bayern have scored 117 goals this season. Expect a rout.' },
      leagueContext: { score: 20, detail: 'Bayern want to hit 89 points and celebrate. Koln have not won away since October.' }
    },
    teamNews: {
      home: [
        { tag: 'out', text: 'Alphonso Davies \u2014 hamstring (season-ending, CL semi-final injury)' },
        { tag: 'key', text: 'Champions with 86 points and 117 goals \u2014 record-breaking season' }
      ],
      away: [
        { tag: 'key', text: '14th place, 32 points \u2014 safe but dreadful away form' },
        { tag: 'key', text: 'No away win since October 2025' }
      ]
    },
    context: 'Bayern Munich celebrate their title on the final day at the Allianz Arena. They have 117 goals and want to reach 89 points. Koln are safe but have not won away since October. This will be a party for Bayern and a battering for Koln.',
    summary: 'Bayern celebrate the title at home with 117 goals already scored. Koln have not won away since October. A draw would be a monumental shock. Expect a rout.'
  },
  'Leverkusen|HSV': {
    drawProbability: 26, verdict: 'Low', fairOdds: '3.60\u20133.80',
    factors: {
      formBalance: { score: 45, detail: 'Leverkusen are 6th but lost 3-1 to Stuttgart last week. HSV are 11th and in good form (2 consecutive wins).' },
      drawRates: { score: 50, detail: 'Both teams produce mixed results; draws are possible.' },
      headToHead: { score: 50, detail: `First top-flight meeting in years after HSV's promotion.` },
      goalTendency: { score: 50, detail: `HSV's counterattacking style (best in league with Bayern) can cause problems.` },
      leagueContext: { score: 45, detail: 'Leverkusen need a win for slim top-4 hopes. HSV are safe and relaxed.' }
    },
    teamNews: {
      home: [
        { tag: 'out', text: 'Nathan Tella \u2014 injury' },
        { tag: 'out', text: 'Martin Terrier \u2014 injury' },
        { tag: 'key', text: '6th place \u2014 slim top-4 hopes depend on other results' }
      ],
      away: [
        { tag: 'key', text: '11th place \u2014 safe, playing relaxed football' },
        { tag: 'key', text: 'Back-to-back wins vs Frankfurt and Freiburg' },
        { tag: 'key', text: 'Counterattacking efficiency tied with Bayern as best in the league' }
      ]
    },
    context: 'Leverkusen need a win for slim top-4 hopes but are coming off a 3-1 defeat. HSV are safe and dangerous \u2014 their counterattacking style (joint-best in the league with Bayern) makes them tricky opponents. A newly-promoted side playing with freedom against a pressured Leverkusen is a recipe for an upset or a draw.',
    summary: `Leverkusen chase top-4 at home but are coming off a defeat. HSV are safe, in form, and dangerous on the counter. A draw is possible but Leverkusen's home advantage should just edge it.`
  }
};

// Now patch each fixture
function loadLeagues(html) {
  const m = html.match(/const LEAGUES = (\[[\s\S]*?\n\]);/);
  if (!m) throw new Error('Could not extract LEAGUES');
  return eval(m[1]);
}

const LEAGUES = loadLeagues(html);
const bl = LEAGUES.find(l => l.id === 'bundesliga');
if (!bl) throw new Error('No bundesliga league found');

let count = 0;
for (const f of bl.fixtures) {
  if (!f.day.includes('Saturday')) continue;
  const key = `${f.home}|${f.away}`;
  const r = research[key];
  if (!r) {
    console.log(`No research for: ${key}`);
    continue;
  }

  // Build the replacement text by finding the fixture in HTML
  const homeEsc = f.home.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const awayEsc = f.away.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // Find and replace drawProbability
  const dpPattern = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}', time: '[^']+',\\s*\\n\\s*result: null, drawProbability: )\\d+`);
  if (dpPattern.test(html)) {
    html = html.replace(dpPattern, `$1${r.drawProbability}`);
  }

  // Replace verdict
  const verdPattern = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?result: null, drawProbability: \\d+, verdict: ')[^']+(')`);
  if (verdPattern.test(html)) {
    html = html.replace(verdPattern, `$1${r.verdict}$2`);
  }

  // Replace fairOdds
  const oddsPattern = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?fairOdds: ')[^']+(')`);
  if (oddsPattern.test(html)) {
    html = html.replace(oddsPattern, `$1${r.fairOdds}$2`);
  }

  // Replace each factor
  for (const [factorKey, factorVal] of Object.entries(r.factors)) {
    const scoreP = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?${factorKey}:\\s*\\{ score: )\\d+`);
    if (scoreP.test(html)) {
      html = html.replace(scoreP, `$1${factorVal.score}`);
    }
    const detailEsc = factorVal.detail.replace(/'/g, "\\'");
    const detP = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?${factorKey}:\\s*\\{ score: \\d+, detail: ')[^']*(')`);
    if (detP.test(html)) {
      html = html.replace(detP, `$1${detailEsc}$2`);
    }
  }

  // Replace summary
  const sumEsc = r.summary.replace(/'/g, "\\'");
  const sumP = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?summary: ')Pending deep research\\.(')`);
  if (sumP.test(html)) {
    html = html.replace(sumP, `$1${sumEsc}$2`);
  }

  // Add teamNews and context before the summary line
  if (r.teamNews) {
    const tnHome = r.teamNews.home.map(i => `            { tag: '${i.tag}', text: '${i.text.replace(/'/g, "\\'")}' }`).join(',\n');
    const tnAway = r.teamNews.away.map(i => `            { tag: '${i.tag}', text: '${i.text.replace(/'/g, "\\'")}' }`).join(',\n');
    const tnBlock = `        teamNews: {\n          home: [\n${tnHome}\n          ],\n          away: [\n${tnAway}\n          ]\n        },\n`;
    const ctxBlock = r.context ? `        context: '${r.context.replace(/'/g, "\\'")}',\n` : '';

    // Insert before the summary line for this fixture
    const insertPattern = new RegExp(`(home: '${homeEsc}', away: '${awayEsc}'[\\s\\S]*?leagueContext:\\s*\\{[^}]+\\}\\s*\\n\\s*\\},\\n)(\\s*summary:)`);
    if (insertPattern.test(html)) {
      html = html.replace(insertPattern, `$1${tnBlock}${ctxBlock}$2`);
    } else {
      console.log(`Could not find insert point for teamNews: ${key}`);
    }
  }

  count++;
  console.log(`✓ ${f.home} vs ${f.away}: ${r.drawProbability}% ${r.verdict}`);
}

fs.writeFileSync(indexPath, html);
console.log(`\nUpdated ${count} Bundesliga fixtures.`);
