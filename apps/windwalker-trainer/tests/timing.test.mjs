import test from 'node:test';
import assert from 'node:assert/strict';
import { Combat } from '../dist/combat.js';
import { CALIBRATION } from '../dist/calibration.js';
import { referenceDecision } from '../dist/policy.js';

const HASTE = 1.19;
const TOLERANCE = 1e-8;
const session = (options = {}) => new Combat({ initialChi: 6, critMode: 'none', seed: 1026, ...options });
const normalFists = c => c.hits.filter(h => h.skill === 'fists' && !h.tier);

function near(actual, expected, message) {
  assert.ok(Math.abs(actual - expected) < TOLERANCE,
    `${message}: expected ${expected}, received ${actual}`);
}

function advanceTo(c, time) {
  assert.ok(time >= c.time - TOLERANCE, 'test must advance simulation time monotonically');
  c.advance(Math.max(0, time - c.time));
  near(c.time, time, 'simulation reaches the requested boundary');
}

function castNow(c, skill) {
  const count = c.casts.length;
  assert.equal(c.cast(skill).ok, true, `${skill} must be accepted`);
  assert.equal(c.casts.length, count + 1, `${skill} must execute now, not merely enter the queue`);
  return c.casts.at(-1);
}

function times(actual, expected, message) {
  assert.equal(actual.length, expected.length, `${message}: pulse count`);
  actual.forEach((time, i) => near(time, expected[i], `${message}: pulse ${i}`));
}

function dragonWindow() {
  const c = session();
  castNow(c, 'fists');
  advanceTo(c, 4);
  castNow(c, 'sun');
  assert.ok(c.buffLeft('dragonReady') > 0, 'both running core cooldowns grant the ready buff');
  return c;
}

test('timing fixtures use the fixed nineteen-percent haste profile without mutating calibration', () => {
  near(CALIBRATION.stats.haste_pct, 0.19, 'fixed profile haste');
  near(session().haste(), HASTE, 'unbuffed haste multiplier');
});

// SimC sc_monk.cpp: SCK ground expiration applies CDR independently of the channel and its last pulse.
for (const [targets, bloodlust] of [[1, false], [3, false], [5, false], [8, false], [5, true]]) {
  test(`SCK CDR occurs once at cast +1.5s, not the last ground pulse (${targets} targets, lust=${bloodlust})`, () => {
    const c = session({ targets, bloodlust });
    advanceTo(c, 2);
    c.cooldowns.fists = 24;
    const start = c.time;
    const haste = HASTE * (bloodlust ? 1.3 : 1);
    const pulseInterval = 1.5 / haste / 4 - 0.1;
    const reduction = 0.5 * Math.min(targets, 5);
    castNow(c, 'crane');

    advanceTo(c, start + 3 * pulseInterval);
    times(c.hits.filter(h => h.skill === 'crane').map(h => h.time),
      [0, 1, 2, 3].map(i => start + i * pulseInterval), 'SCK ground pulses');
    near(c.remaining('fists'), 24 / haste - 3 * pulseInterval, 'no CDR on the last damage pulse');

    advanceTo(c, start + 1.499);
    assert.equal(c.channel, null, 'the haste-scaled SCK channel has already ended');
    near(c.remaining('fists'), 24 / haste - 1.499, 'no CDR before fixed ground expiration');
    advanceTo(c, start + 1.5);
    near(c.remaining('fists'), 24 / haste - 1.5 - reduction, 'CDR at fixed ground expiration');
    advanceTo(c, start + 2);
    near(c.remaining('fists'), 24 / haste - 2 - reduction, 'no duplicate CDR after expiration');
  });
}

for (const cancelAt of [0, 0.1]) {
  test(`canceling SCK at +${cancelAt}s preserves all ground hits and delayed CDR without clipping FoF`, () => {
    const c = session({ targets: 5 });
    c.cooldowns.fists = 24;
    castNow(c, 'crane');
    advanceTo(c, cancelAt);
    assert.equal(c.cancel({ source: 'keyboard', key: 'X' }), true);
    assert.equal(c.channel, null);

    advanceTo(c, 0.8);
    const interval = 1.5 / HASTE / 4 - 0.1;
    times(c.hits.filter(h => h.skill === 'crane').map(h => h.time),
      [0, interval, 2 * interval, 3 * interval], 'ground pulses survive explicit cancellation');
    advanceTo(c, 1.499);
    near(c.remaining('fists'), 24 / HASTE - 1.499, 'cancellation does not apply CDR early');
    advanceTo(c, 1.5);
    near(c.remaining('fists'), 24 / HASTE - 1.5 - 2.5, 'delayed CDR survives explicit cancellation');
    assert.equal(c.summary().clippedFists, 0);
    assert.equal(c.events.filter(e => e.type === 'clippedFists').length, 0);
  });
}

for (const change of ['gain', 'expire']) {
  test(`FoF snapshots haste when bloodlust changes mid-channel (${change})`, () => {
    const c = session();
    if (change === 'expire') c.setBuff('bloodlust', 0.4);
    castNow(c, 'fists');
    const interval = change === 'gain' ? 0.840 : 0.646;
    const expectedEnd = 4 * interval;
    near(c.channel.end, expectedEnd, 'FoF end is fixed on cast');

    advanceTo(c, 0.4);
    if (change === 'gain') c.setBuff('bloodlust', 40);
    near(c.haste(), HASTE * (change === 'gain' ? 1.3 : 1), 'live haste changes');
    near(c.channel.end, expectedEnd, 'live haste does not move the channel end');
    advanceTo(c, expectedEnd - 0.001);
    assert.equal(c.channel?.skill, 'fists');
    assert.equal(normalFists(c).length, 4, 'the final normal pulse has not happened early');
    advanceTo(c, expectedEnd);
    times(normalFists(c).map(h => h.time), [0, interval, 2 * interval, 3 * interval, expectedEnd],
      'normal pulses keep their cast-time haste');
    assert.equal(c.hits.filter(h => h.skill === 'fists' && h.tier).length, 1);
    assert.equal(c.channel, null);
    assert.equal(c.clippedFists, 0);
  });
}

// FoF keeps cast-time haste/end, but reevaluates Jade's tick-time modifier after each scheduled tick.
for (const jade of ['jade', 'greatJade', 'avatar']) {
  test(`FoF dynamically loses ${jade} after the next scheduled tick and finishes its fixed end without a clip`, () => {
    const c = session();
    c.setBuff(jade, 0.1);
    near(c.haste(), HASTE * 1.1, 'one Jade haste contribution at cast');
    castNow(c, 'fists');
    near(c.channel.end, 1.528, 'four initial 0.382s intervals fix the channel end');

    advanceTo(c, 0.1);
    assert.equal(c.buffLeft(jade), 0);
    near(c.haste(), HASTE, 'live haste loses Jade');
    near(c.channel.end, 1.528, 'Jade expiration does not extend FoF');
    advanceTo(c, 0.381);
    assert.equal(normalFists(c).length, 1);
    advanceTo(c, 0.382);
    times(normalFists(c).map(h => h.time), [0, 0.382], 'the already scheduled tick is not moved');
    advanceTo(c, 1.145);
    assert.equal(normalFists(c).length, 2, 'the next interval grows to 0.764s using snapshotted haste');
    advanceTo(c, 1.146);
    times(normalFists(c).map(h => h.time), [0, 0.382, 1.146], 'post-expiration normal pulses');
    advanceTo(c, 1.527);
    assert.equal(c.channel?.skill, 'fists');
    advanceTo(c, 1.528);
    times(normalFists(c).map(h => h.time), [0, 0.382, 1.146, 1.528], 'shortened final interval at fixed end');
    assert.equal(c.hits.filter(h => h.skill === 'fists' && h.tier).length, 1);
    assert.equal(c.channel, null);
    assert.equal(c.summary().clippedFists, 0, 'fewer than five normal pulses is not itself a clip');
    assert.equal(c.events.filter(e => e.type === 'clippedFists').length, 0);
    advanceTo(c, 3);
    assert.equal(normalFists(c).length, 4, 'no stale pulse fires after the fixed end');
  });
}

for (const [critMode, crits] of [['none', 0], ['single', 1], ['double', 2]]) {
  test(`Dawn and the sun hit resolve at the exact cast timestamp (${critMode})`, () => {
    const c = session({ critMode });
    advanceTo(c, 2);
    c.cooldowns.fists = 24;
    const cast = castNow(c, 'sun');
    const hits = c.hits.filter(h => ['sun', 'dawn'].includes(h.skill));
    assert.deepEqual(hits.map(h => h.skill), ['sun', 'dawn']);
    times(hits.map(h => h.time), [cast.time, cast.time], 'sun and Dawn settle together');
    const result = c.events.findLast(e => e.type === 'sunResult');
    assert.ok(result);
    assert.equal(result.dawn, true);
    assert.equal(result.crits, crits);
    assert.equal(result.time, cast.time);
    assert.equal(result.castTime, cast.time);
    assert.equal(result.state.time, cast.time);
    near(c.remaining('fists'), 24 / HASTE - 4 * crits, 'both crit reductions settle without advancing time');
    near(result.state.cooldowns.fists, c.remaining('fists'), 'result snapshot includes both reductions');
    assert.equal(c.chi, 5, 'Dawn grants its chi immediately');
    advanceTo(c, cast.time + 0.5);
    assert.equal(c.hits.filter(h => h.skill === 'dawn').length, 1, 'no delayed duplicate Dawn');
  });
}

for (const outcome of [
  { mainCrit: false, dawnTriggered: false },
  { mainCrit: true, dawnTriggered: false },
  { mainCrit: false, dawnTriggered: true, dawnCrit: false },
  { mainCrit: true, dawnTriggered: true, dawnCrit: false },
  { mainCrit: false, dawnTriggered: true, dawnCrit: true },
  { mainCrit: true, dawnTriggered: true, dawnCrit: true },
]) {
  test(`atomic sun result and hits expose the observed crit components ${JSON.stringify(outcome)}`, () => {
    const c = session({ critMode: 'double', sunOutcomes: [outcome] });
    c.cooldowns.fists = 24;
    const cast = castNow(c, 'sun');
    const result = c.events.findLast(e => e.type === 'sunResult');
    const crits = Number(outcome.mainCrit) + Number(outcome.dawnTriggered && outcome.dawnCrit);
    assert.equal(result.mainCrit, outcome.mainCrit);
    assert.equal(result.dawnTriggered, outcome.dawnTriggered);
    assert.equal(result.dawnCrit, outcome.dawnTriggered ? outcome.dawnCrit : null);
    assert.equal(result.crits, crits);
    assert.equal(result.dawn, outcome.dawnTriggered);
    assert.equal(result.castId, cast.castId);
    near(result.fistsBefore, 24 / HASTE, 'pre-hit cooldown');
    near(result.fistsAfter, 24 / HASTE - 4 * crits, 'post-hit cooldown');
    near(result.reductionSeconds, 4 * crits, 'actual wall-second reduction');
    assert.equal(result.ready, false);
    assert.deepEqual(result.state, c.snapshot(), 'snapshot includes the complete WDP trigger settlement');
    assert.ok(result.state.buffs.dragonReady > 0);
    const hits = c.hits.filter(h => h.castId === cast.castId);
    assert.deepEqual(hits.map(h => h.spell), outcome.dawnTriggered ? ['sun', 'dawn'] : ['sun']);
    assert.deepEqual(hits.map(h => h.crit), outcome.dawnTriggered ? [outcome.mainCrit, outcome.dawnCrit] : [outcome.mainCrit]);
    assert.ok(hits.every(h => h.time === cast.time));
  });
}

test('sun result reports actual clamped recovery-scaled reduction and cooldown readiness', () => {
  const c = session({ critMode: 'double' });
  c.setBuff('greatJade', 6);
  c.cooldowns.fists = 3.2725;
  castNow(c, 'sun');
  const result = c.events.findLast(e => e.type === 'sunResult');
  near(result.fistsBefore, 1, 'one wall-second before both crits');
  assert.equal(result.fistsAfter, 0);
  near(result.reductionSeconds, 1, 'reduction is capped at the remaining cooldown');
  assert.equal(result.ready, true);
  assert.equal(result.state.buffs.dragonReady, 0, 'no ready window is invented once FoF is already ready');
});

test('sun outcomes are consumed only by execution, restore their cursor, and then fall back to critMode', () => {
  const c = session({ critMode: 'none', sunOutcomes: [{ mainCrit: true, dawnTriggered: false }] });
  c.cast('palm'); c.advance(0.2);
  assert.equal(c.cast('sun').ok, false);
  c.advance(0.6);
  assert.equal(c.cast('sun').queued, true);
  assert.equal(c.events.filter(e => e.type === 'sunResult').length, 0);
  const restored = Combat.fromState(c.saveState({ history: false }));
  for (const branch of [c, restored]) {
    branch.advance(0.2);
    const first = branch.events.findLast(e => e.type === 'sunResult');
    assert.equal(first.mainCrit, true);
    assert.equal(first.dawnTriggered, false);
    branch.advance(1);
    branch.cooldowns.sun = 0;
    branch.cast('sun');
    const second = branch.events.findLast(e => e.type === 'sunResult');
    assert.equal(second.mainCrit, false);
    assert.equal(second.dawnTriggered, true);
    assert.equal(second.dawnCrit, false);
  }
  assert.deepEqual(c.snapshot(), restored.snapshot());
  assert.equal(c.randomState, restored.randomState);
});

test('future sun outcomes do not affect earlier policy decisions, observed results or RNG', () => {
  const first = { mainCrit: false, dawnTriggered: true, dawnCrit: true };
  const a = session({ sunOutcomes: [first, { mainCrit: true, dawnTriggered: false }] });
  const b = session({ sunOutcomes: [first, { mainCrit: false, dawnTriggered: true, dawnCrit: false }] });
  assert.deepEqual(referenceDecision(a), referenceDecision(b));
  assert.equal(a.randomState, 1026);
  for (const c of [a, b]) { c.cooldowns.fists = 24; c.cast('sun'); }
  assert.deepEqual(a.events, b.events);
  assert.deepEqual(a.hits, b.hits);
  assert.deepEqual(a.recommend(), b.recommend());
  assert.equal(a.randomState, b.randomState);
});

test('wind uses the sun input but starts only its own ten-second hasted cooldown and never unlocks WDP', () => {
  const c = session();
  c.cooldowns.fists = 24;
  c.setBuff('wind', 15);
  const wind = castNow(c, 'sun');
  assert.equal(wind.skill, 'sun');
  assert.equal(wind.spell, 'wind');
  assert.equal(c.hits.find(h => h.castId === wind.castId && h.skill === 'sun').spell, 'wind');
  assert.equal(c.previousAction, 'wind');
  assert.equal(c.lastSkill, 'wind');
  near(c.cooldowns.wind, 10, 'independent wind cooldown work');
  near(c.remaining('wind'), 10 / HASTE, 'wind cooldown is hasted');
  assert.equal(c.cooldowns.sun, 0, 'wind does not start the sun cooldown');
  assert.equal(c.buffLeft('dragonReady'), 0, 'wind is not a WDP trigger');
  assert.equal(c.available('dragon', true).ok, false);

  advanceTo(c, 1);
  assert.equal(c.available('sun').ok, true, 'ordinary sun remains usable while wind cools down');
  const sun = castNow(c, 'sun');
  assert.equal(sun.skill, 'sun');
  assert.equal(sun.spell, 'sun');
  near(c.cooldowns.sun, 10, 'ordinary sun starts its own cooldown');
  near(c.cooldowns.wind, 10 - HASTE, 'ordinary sun does not reset wind');
  assert.ok(c.buffLeft('dragonReady') > 0, 'ordinary sun still unlocks WDP with fists on cooldown');
});

test('wind ignores an existing sun cooldown, while a new wind proc cannot bypass its own cooldown', () => {
  const c = session();
  c.cooldowns.sun = 9;
  c.setBuff('wind', 15);
  assert.equal(c.available('sun').ok, true, 'the replacement uses wind readiness, not sun readiness');
  castNow(c, 'sun');
  near(c.cooldowns.sun, 9, 'wind neither restarts nor clears an existing sun cooldown');
  near(c.cooldowns.wind, 10, 'wind starts its own cooldown');

  advanceTo(c, 1);
  c.cooldowns.sun = 0;
  c.setBuff('wind', 15);
  assert.equal(c.available('sun').ok, false, 'ready sun cannot bypass an active wind cooldown');
  assert.equal(c.cast('sun').ok, false, 'a new proc is not a wind cooldown reset');
  advanceTo(c, 10 / HASTE - 0.001);
  assert.equal(c.available('sun').ok, false);
  advanceTo(c, 10 / HASTE);
  assert.equal(c.available('sun').ok, true, 'wind becomes legal at its independent hasted ready time');
});

for (const targets of [1, 5]) {
  test(`policy distinguishes wind action from the shared sun input (${targets} targets)`, () => {
    const c = session({ targets });
    advanceTo(c, 5);
    c.energy = 0;
    c.cooldowns.tiger = 50;
    c.cooldowns.fists = 20;
    c.cooldowns.dragon = 20;
    c.cooldowns.sun = 9;
    c.setBuff('wind', 15);
    const decision = referenceDecision(c);
    assert.equal(decision.skill, 'sun', 'policy returns the physical replacement slot');
    assert.equal(decision.action, 'wind', 'policy retains the internal wind action identity');
    assert.equal(decision.rule, targets === 1 ? 'st-wind' : 'aoe-wind');
    const cast = castNow(c, decision.skill);
    assert.equal(cast.spell, 'wind');
    assert.equal(cast.decision.action, 'wind');

    advanceTo(c, 6);
    c.cooldowns.sun = 0;
    c.setBuff('wind', 15);
    const blocked = referenceDecision(c);
    assert.notEqual(blocked.action, 'wind', 'policy must respect the independent wind cooldown');
    assert.notEqual(blocked.action, 'sun', 'the wind proc hides ordinary sun until consumed or expired');
  });
}

test('WDP ready survives natural sun readiness for exactly 1.5 / cast-time haste seconds', () => {
  const c = dragonWindow();
  const sunReadyAt = 4 + 10 / HASTE;
  const grace = 1.5 / HASTE;
  near(c.buffLeft('dragonReady'), 10 / HASTE + grace, 'ready duration includes the hasted grace');
  advanceTo(c, sunReadyAt);
  near(c.remaining('sun'), 0, 'sun naturally becomes ready');
  assert.ok(c.remaining('fists') > 0);
  near(c.buffLeft('dragonReady'), grace, 'ready buff remains when one core cooldown reaches zero');
  assert.equal(c.available('dragon').ok, true);
  advanceTo(c, sunReadyAt + grace - 0.001);
  assert.equal(c.available('dragon').ok, true, 'WDP remains usable just before grace expires');
  advanceTo(c, sunReadyAt + grace);
  assert.equal(c.buffLeft('dragonReady'), 0);
  assert.equal(c.available('dragon').ok, false, 'WDP is unavailable at the exact expiration boundary');
});

test('WDP can actually execute during the grace after sun naturally becomes ready', () => {
  const c = dragonWindow();
  advanceTo(c, 4 + 10 / HASTE + 0.5 / HASTE);
  assert.equal(c.remaining('sun'), 0);
  assert.equal(castNow(c, 'dragon').spell, 'dragon');
  assert.ok(c.buffLeft('jade') > 0);
});

for (const reset of ['zenith', 'blackout']) {
  test(`WDP ready is not erased or refreshed when ${reset} resets sun`, () => {
    const c = dragonWindow();
    const expiresAt = c.time + c.buffLeft('dragonReady');
    advanceTo(c, 5);
    if (reset === 'blackout') {
      c.combo = 1;
      c.setBuff('combo', 15);
      c.random = () => 0;
    }
    castNow(c, reset);
    assert.equal(c.remaining('sun'), 0, 'the selected mechanism really resets sun');
    near(c.buffLeft('dragonReady'), expiresAt - c.time, 'reset preserves the existing ready duration');
    assert.equal(c.available('dragon', true).ok, true, 'sun reset is not an immediate WDP lockout');
    advanceTo(c, expiresAt - 0.001);
    assert.equal(c.available('dragon').ok, true, 'the original window survives the reset and haste changes');
    advanceTo(c, expiresAt);
    assert.equal(c.buffLeft('dragonReady'), 0, 'reset does not refresh the existing window');
    assert.equal(c.available('dragon').ok, false);
  });
}

test('white tiger coexists with SCK without replacing its channel or clipping FoF', () => {
  const c = session({ targets: 5 });
  c.cooldowns.fists = 24;
  castNow(c, 'crane');
  const channelId = c.channel.id;
  const end = c.channel.end;
  advanceTo(c, 1);
  castNow(c, 'tiger');
  assert.equal(c.channel?.id, channelId, 'white tiger preserves the SCK channel');
  near(c.channel.end, end, 'white tiger does not move SCK expiration');
  assert.ok(c.buffLeft('tiger') > 0);
  assert.equal(c.events.filter(e => e.type === 'channelEnd').length, 0);
  advanceTo(c, end);
  assert.equal(c.channel, null);
  advanceTo(c, 1.5);
  assert.equal(c.hits.filter(h => h.skill === 'crane').length, 4);
  near(c.remaining('fists'), 24 / HASTE - 1.5 - 2.5, 'white tiger preserves delayed SCK CDR');
  assert.equal(c.clippedFists, 0);
});

test('wind in the shared sun slot interrupts SCK but preserves ground hits and delayed CDR', () => {
  const c = session({ targets: 5 });
  c.cooldowns.fists = 24;
  castNow(c, 'crane');
  advanceTo(c, 1);
  assert.equal(c.channel?.skill, 'crane');
  c.setBuff('wind', 15);
  const wind = castNow(c, 'sun');
  assert.equal(wind.skill, 'sun');
  assert.equal(wind.spell, 'wind');
  assert.equal(c.channel, null, 'coexistence must check resolved wind, not the sun input identity');
  assert.equal(c.events.filter(e => e.type === 'channelEnd').length, 1);
  assert.equal(c.buffLeft('dragonReady'), 0);
  advanceTo(c, 1.5);
  assert.equal(c.hits.filter(h => h.skill === 'crane').length, 4);
  near(c.remaining('fists'), 24 / HASTE - 1.5 - 2.5, 'wind interruption preserves delayed SCK CDR');
  assert.equal(c.summary().clippedFists, 0);
  assert.equal(c.events.filter(e => e.type === 'clippedFists').length, 0);
});
