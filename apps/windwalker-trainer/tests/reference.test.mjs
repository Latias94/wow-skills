import test from 'node:test';
import assert from 'node:assert/strict';
import { Combat } from '../dist/combat.js';
import { referenceDecision, POLICY } from '../dist/policy.js';
import { buildReference, advanceReference } from '../dist/reference.js';
import { reviewRoutine } from '../dist/routines.js';

test('fixed-build reference uses the SimC opener, then white tiger, without consuming RNG', () => {
  const c = new Combat();
  const rng = c.randomState;
  assert.equal(referenceDecision(c).skill, 'palm');
  assert.equal(c.randomState, rng);
  c.cast('palm'); c.advance(1);
  assert.equal(referenceDecision(c).skill, 'tiger');
  assert.equal(POLICY.revision, '73a372b76188c703e48729caded3258cdc5b726b');
});

test('the reference protects an incomplete fists channel and reports a wait reason', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('fists'); c.advance(1);
  const d = referenceDecision(c);
  assert.equal(d.skill, null);
  assert.equal(d.blocker, 'fists-channel');
  assert.ok(d.wait > 2);
});

test('ready fists has priority over an ordinary filler inside great jade', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('fists');
  c.advance(2); c.setBuff('greatJade', 6); c.cooldowns.fists = 0;
  assert.equal(referenceDecision(c).skill, 'fists');
});

test('the reference does not compare an impossible fists against chi-starved input', () => {
  const c = new Combat({ initialChi: 0 });
  c.time = 5; c.setBuff('greatJade', 6);
  const d = referenceDecision(c);
  assert.notEqual(d.skill, 'fists');
  assert.equal(d.skill, 'palm');
});

test('single-target wind and multi-target tier crane retain their distinct source rules', () => {
  for (const targets of [1, 5]) {
    const c = new Combat({ initialChi: 6, targets });
    c.time = 5; c.cooldowns.tiger = 50; c.cooldowns.fists = 20; c.cooldowns.dragon = 20;
    c.rhythm = 6; c.setBuff('rhythm', 20); c.setBuff('wind', 15);
    const d = referenceDecision(c);
    assert.equal(d.skill, targets === 1 ? 'sun' : 'crane');
    assert.ok(d.line > 250);
  }
});

test('a generated reference is a replay of legal actions and deterministically covers all crit branches', () => {
  for (const critMode of ['none', 'single', 'double']) {
    const options = { seed: 1026, duration: 45, critMode };
    const a = buildReference(options);
    const b = buildReference(options);
    assert.deepEqual(a.casts, b.casts);
    assert.ok(a.casts.filter(c => c.skill === 'fists').length >= 3);
    assert.equal(a.invalidActions, 0);
    assert.ok(a.casts.every(c => c.decision?.line || c.skill === 'cancel'));
  }
});

test('fists readiness and earliest recommended use exclude the preceding GCD', () => {
  const c = new Combat({ initialChi: 6, critMode: 'double' });
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('fists'); c.advance(2);
  c.setBuff('greatJade', 6); c.cooldowns.fists = 5;
  c.cast('sun');
  c.advance(1);
  const opportunity = c.fistsOpportunities.at(-1);
  assert.ok(opportunity.cooldownReadyAt < 4);
  assert.ok(opportunity.legalAt >= 4 - 0.0001);
  assert.ok(opportunity.referenceAt >= 4 - 0.0001);
  c.advance(1); c.cast('fists');
  assert.ok(Math.abs(opportunity.delay - 1) < 0.001);
});

test('SCK has a real haste-scaled channel distinct from its four ground pulses', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('crane');
  assert.equal(c.channel.skill, 'crane');
  assert.ok(Math.abs(c.channel.end - 1.26) < 0.001);
  c.advance(0.8);
  assert.equal(c.hits.filter(h => h.skill === 'crane').length, 4);
  assert.equal(c.channel.skill, 'crane');
});

test('coexisting skill does not erase SCK channel or its delayed ground hits', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('crane'); c.advance(1); c.cast('palm');
  assert.equal(c.channel?.skill, 'crane');
  c.advance(1);
  assert.equal(c.channel, null);
  assert.equal(c.hits.filter(h => h.skill === 'crane').length, 4);
});

test('zero-GCD zenith waits for the white tiger GCD without use_off_gcd', () => {
  const c = new Combat({ initialChi: 4 });
  c.cast('tiger');
  assert.ok(c.gcdEnd > c.time);
  assert.equal(c.available('zenith').ok, true, 'explicit raw input still permits zero-GCD zenith');
  assert.equal(referenceDecision(c).skill, null);
  assert.equal(referenceDecision(c).blocker, 'gcd');
  c.advance(c.gcdEnd - c.time);
  assert.equal(referenceDecision(c).skill, 'zenith');
});

test('the policy waits for a nonzero conduit tick rather than cancelling immediately', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('tiger'); c.advance(1); c.cast('conduit');
  assert.notEqual(referenceDecision(c).skill, 'cancel');
  c.advance(1 / c.haste());
  assert.equal(referenceDecision(c).skill, 'cancel');
});

test('conduit cancellation observes only the last tick, not a later resource change', () => {
  const c = new Combat({ initialChi: 2, bloodlust: true });
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('conduit');
  c.advance(1 / c.haste());
  assert.notEqual(referenceDecision(c).skill, 'cancel');
  c.gainChi(2);
  assert.notEqual(referenceDecision(c).skill, 'cancel');
  c.advance(1 / c.haste());
  assert.equal(referenceDecision(c).skill, 'cancel');
});

test('automatic replay is independent of browser frame size and covers bloodlust/target branches', () => {
  for (const targets of [1, 5]) for (const bloodlust of [false, true]) {
    const options = { targets, bloodlust, critMode: 'double', duration: 45 };
    const baseline = buildReference(options);
    const c = new Combat(options);
    for (let i = 0; c.time < options.duration - 1e-7; i++) advanceReference(c, i % 2 ? 0.033 : 0.017);
    const sequence = casts => casts.map(cast => [Number(cast.time.toFixed(6)), cast.spell]);
    assert.deepEqual(sequence(c.casts), sequence(baseline.casts));
    assert.equal(baseline.invalidActions, 0);
    assert.equal(c.clippedFists, 0);
  }
});

test('an unspent opportunity remains in the review, with chi starvation distinct from recommendation', () => {
  const c = new Combat({ initialChi: 2 });
  c.cast('fists'); c.advance(4); c.cooldowns.fists = 0; c.chi = 0;
  c.advance(0);
  let o = c.fistsOpportunities.at(-1);
  assert.equal(o.legalAt, null);
  assert.equal(o.referenceAt, null);
  assert.ok(o.blockers.includes('缺真气'));
  c.setBuff('greatJade', 6); c.setBuff('avatar', 4);
  c.zenithRecharge = [90];
  c.energy = 60;
  c.gainChi(2); c.advance(0);
  o = reviewRoutine(c).opportunities.at(-1);
  assert.equal(o.actualAt, null);
  assert.equal(o.status, 'unspent');
  assert.equal(o.sinceFirstReference, 0);
});

test('floating residuals at a conduit tick are treated as a ready cooldown', () => {
  const c = new Combat({ initialChi: 6, targets: 5, bloodlust: true });
  c.time = 5; c.setBuff('jade', 6); c.setBuff('conduitReady', 60);
  c.cooldowns.sun = 5; c.cooldowns.fists = 1.75;
  c.cast('conduit'); c.advance(c.channel.nextTick - c.time);
  assert.equal(c.available('fists', true).ok, true);
  assert.equal(referenceDecision(c).skill, 'cancel');
});

test('a full-recharge threshold inside a GCD waits for its frame-independent end before zenith', () => {
  const setup = () => {
    const c = new Combat({ targets: 2, duration: 120 });
    c.cast('zenith'); c.advance(19.5); c.cast('tiger'); c.advance(40); c.cast('palm');
    return c;
  };
  const a = setup(), b = setup();
  advanceReference(a, 1.1);
  for (let i = 0; i < 66; i++) advanceReference(b, 1 / 60);
  const nextZenith = c => c.casts.filter(cast => cast.skill === 'zenith')[1].time;
  assert.ok(Math.abs(nextZenith(a) - nextZenith(b)) < 1e-7);
  assert.ok(Math.abs(nextZenith(a) - 60.5) < 1e-7);
});

test('the tail conduit condition precedes zenith and does not require zenith to be active', () => {
  const c = new Combat({ duration: 300, initialChi: 6 });
  c.time = 296; c.cast('tiger'); c.advance(1);
  const d = referenceDecision(c);
  assert.equal(d.skill, 'conduit');
  assert.equal(d.line, 232);
});

test('a cooldown finishing at the training bell is not recorded as a legal missed cast', () => {
  const c = new Combat({ duration: 5, initialChi: 6 });
  c.cast('fists'); c.cooldowns.fists = 5 * c.haste(); c.advance(5);
  const o = c.fistsOpportunities.at(-1);
  assert.equal(o.cooldownReadyAt, 5);
  assert.equal(o.legalAt, null);
  assert.equal(o.referenceAt, null);
  assert.ok(o.blockers.includes('本轮结束'));
});

test('an untargetable cooldown opportunity stays blocked until a target returns', () => {
  const c = new Combat({ initialChi: 6, duration: 6, encounterEvents: [
    { at: 0.5, attackable: false }, { at: 5, attackable: true },
  ] });
  c.cast('fists'); c.cooldowns.fists = 4 * c.haste(); c.advance(4);
  const opportunity = c.fistsOpportunities.at(-1);
  assert.equal(opportunity.cooldownReadyAt, 4);
  assert.equal(opportunity.legalAt, null);
  assert.equal(opportunity.referenceAt, null);
  assert.ok(opportunity.blockers.includes('没有可攻击目标'));
  c.advance(1);
  assert.equal(opportunity.legalAt, 5);
});

test('reference replay applies encounter events at the same boundary across browser frame sizes', () => {
  const options = { duration: 8, initialChi: 6, critMode: 'single', inputMode: 'protected', encounterEvents: [
    { at: 0, attackable: false }, { at: 0.8, attackable: true, targets: 3, bloodlust: true },
    { at: 3, attackable: false }, { at: 4, attackable: true, targets: 1, bloodlust: false },
  ] };
  const baseline = buildReference(options);
  const c = new Combat(options);
  while (c.time < options.duration - 1e-7) advanceReference(c, 0.017);
  const sequence = casts => casts.map(cast => [Number(cast.time.toFixed(6)), cast.spell]);
  assert.deepEqual(sequence(c.casts), sequence(baseline.casts));
  assert.equal(baseline.invalidActions, 0);
  assert.ok(c.casts.every(cast => cast.time >= 0.8 && (cast.time < 3 || cast.time >= 4)));
  assert.ok(c.hits.every(hit => hit.time < 3 || hit.time >= 4));
  assert.deepEqual(c.events.filter(e => e.type === 'scenario').map(e => e.time), [0, 0.8, 3, 4]);
});
