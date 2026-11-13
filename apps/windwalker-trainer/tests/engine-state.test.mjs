import test from 'node:test';
import assert from 'node:assert/strict';

test('a protected SCK channel delays earliest legal FoF beyond its GCD', () => {
  const c = new Combat({ initialChi: 6, inputMode: 'protected', protectCrane: true });
  c.cast('fists'); c.advance(3.4);
  c.chi = 6;
  c.cooldowns.fists = 0.5 * c.haste();
  c.cast('crane');
  c.advance(1.1);
  assert.equal(c.remaining('fists'), 0);
  assert.equal(c.available('fists').ok, false);
  const opportunity = c.fistsOpportunities.at(-1);
  assert.equal(opportunity.legalAt, null);
  c.advance(0.3);
  assert.ok(opportunity.legalAt > opportunity.cooldownReadyAt);
});
import { Combat } from '../dist/combat.js';
import { CALIBRATION } from '../dist/calibration.js';

test('save and restore during FoF preserves captured haste, combo, exact ticks and independent state', () => {
  const parent = new Combat({ initialChi: 6 });
  parent.cast('fists');
  parent.advance(4);
  parent.cooldowns.fists = 0;
  parent.setBuff('jade', 0.1);
  parent.cast('fists');
  parent.advance(0.2);
  assert.equal(parent.activeCombo, false);
  const state = structuredClone(parent.saveState());
  const branch = Combat.fromState(state);
  assert.deepEqual(branch.saveState(), state);
  const untouched = parent.saveState();
  branch.setBuff('bloodlust', 40);
  branch.advance(2);
  assert.deepEqual(parent.saveState(), untouched, 'branch advancement must leave its parent unchanged');
  parent.setBuff('bloodlust', 40);
  parent.advance(2);
  assert.deepEqual(branch.saveState(), parent.saveState());
  const ticks = branch.hits.filter(h => h.skill === 'fists' && h.time >= 4 && !h.tier);
  assert.deepEqual(ticks.map(h => Number(h.time.toFixed(3))), [4, 4.382, 5.146, 5.528]);
  assert.ok(ticks.every(h => Math.abs(h.amount / (h.crit ? 2.1 : 1) - 13456.999469868893) < 1e-8),
    'all ticks retain the repeated-cast combo modifier independently of their crit rolls');
  branch.options.targets = 5;
  assert.equal(parent.options.targets, 1);
  assert.equal(state.options.targets, 1, 'restoration must also detach the saved input');
});

test('SCK restoration retains captured tier and combo after a coexisting action and explicit cancellation', () => {
  const parent = new Combat({ initialChi: 6, targets: 5 });
  parent.cast('crane');
  parent.advance(2);
  parent.rhythm = 4;
  parent.setBuff('rhythm', 20);
  parent.cooldowns.fists = 24;
  parent.cast('crane');
  parent.advance(0.1);
  const branch = Combat.fromState(structuredClone(parent.saveState()));
  for (const c of [parent, branch]) {
    c.cancel();
    c.advance(0.9);
    c.cast('palm');
    c.advance(0.5);
  }
  assert.deepEqual(branch.saveState(), parent.saveState());
  const hits = branch.hits.filter(h => h.skill === 'crane' && h.time >= 2);
  assert.equal(hits.length, 4);
  const expected = CALIBRATION.damage.crane.reference * 1.8 * 5 / (1 + CALIBRATION.stats.mastery_pct);
  assert.ok(hits.every(h => Math.abs(h.amount / (h.crit ? 2.1 : 1) - expected) < 1e-8));
  assert.ok(Math.abs(branch.remaining('fists') - (24 / 1.19 - 4)) < 1e-8);
});

test('Conduit restoration preserves latched cancellation and manual-stomp coexistence', () => {
  const parent = new Combat({ initialChi: 2, bloodlust: true });
  parent.cast('tiger'); parent.advance(1); parent.cast('zenith'); parent.cast('conduit');
  parent.advance(0.75); parent.cast('stomp'); parent.advance(0.1);
  const branch = Combat.fromState(structuredClone(parent.saveState()));
  for (const c of [parent, branch]) {
    c.advance(0.7);
    c.cancel({ source: 'keyboard', key: 'X' });
    c.advance(3);
  }
  assert.deepEqual(branch.saveState(), parent.saveState());
  assert.ok(branch.buffLeft('greatJade') > 0);
  assert.equal(branch.pending.length, 0);
});

test('history-free forks retain business state and pending work without retaining old review records', () => {
  const parent = new Combat({ initialChi: 6, targets: 5 });
  parent.setBuff('jade', 0.1);
  parent.cast('fists'); parent.advance(4);
  parent.cast('zenith'); parent.cast('crane'); parent.advance(0.2);
  const untouched = parent.saveState();
  const state = structuredClone(parent.saveState({ history: false }));
  for (const key of ['hits', 'events', 'casts', 'controls', 'fistsOpportunities']) assert.deepEqual(state[key], []);
  assert.deepEqual(state.cooldowns, parent.cooldowns, 'raw work, not projected remaining seconds, is stored');
  const branch = Combat.fromState(state);
  assert.deepEqual(branch.snapshot(), parent.snapshot());
  assert.deepEqual(branch.summary(), parent.summary(), 'aggregate damage and counters survive history omission');
  branch.advance(1.5);
  assert.deepEqual(parent.saveState(), untouched);
  parent.advance(1.5);
  assert.deepEqual(branch.snapshot(), parent.snapshot());
  assert.equal(branch.damage, parent.damage);
  assert.equal(branch.randomState, parent.randomState);
});

test('restoring WDP pending hits keeps cast identity and permits independent random sampling', () => {
  const parent = new Combat({ initialChi: 6 });
  parent.setBuff('dragonReady', 4); parent.cast('dragon'); parent.advance(0.1);
  const state = parent.saveState();
  const branch = Combat.fromState(state);
  const sibling = Combat.fromState(state);
  sibling.randomState = 7;
  branch.advance(1);
  assert.deepEqual(parent.saveState(), state);
  parent.advance(1);
  assert.deepEqual(branch.saveState(), parent.saveState());
  assert.deepEqual(sibling.saveState().pending, state.pending);
  assert.notEqual(sibling.randomState, state.randomState);
  assert.ok(branch.hits.every(h => h.castId === branch.casts[0].castId && h.spell === 'dragon'));
});

test('encounter events update active targets and suppress untargetable ground hits across a compact fork', () => {
  const parent = new Combat({ initialChi: 6, encounterEvents: [
    { at: 0.3, targets: 3 },
    { at: 0.5, attackable: false },
    { at: 1.1, attackable: true, targets: 2, bloodlust: true },
    { at: 1.3, bloodlust: false },
  ] });
  parent.cooldowns.fists = 24;
  parent.cast('crane'); parent.advance(0.5);
  assert.equal(parent.attackable, false);
  assert.equal(parent.options.targets, 3);
  assert.equal(parent.recommend().blocker, 'no-target');
  const state = structuredClone(parent.saveState({ history: false }));
  const branch = Combat.fromState(state);
  const beforeDamage = branch.damage;
  for (const c of [parent, branch]) c.advance(0.3);
  assert.equal(branch.damage, beforeDamage, 'pending SCK tick has no target');
  assert.deepEqual(parent.hits.filter(h => h.skill === 'crane').map(h => h.targets), [1, 1, 3]);
  for (const c of [parent, branch]) {
    c.advance(0.3);
    assert.equal(c.attackable, true);
    assert.equal(c.options.targets, 2);
    assert.equal(c.buffLeft('bloodlust'), 40);
    c.advance(0.2);
    assert.equal(c.buffLeft('bloodlust'), 0);
    const beforeExpiry = c.remaining('fists');
    c.advance(0.2);
    assert.ok(Math.abs(c.remaining('fists') - (beforeExpiry - 1.2)) < 1e-8,
      'SCK expiry reduces FoF by one wall-second for the two active targets');
  }
  assert.deepEqual(parent.snapshot(), branch.snapshot());
  assert.equal(parent.damage, branch.damage);
  assert.equal(parent.randomState, branch.randomState);
  assert.deepEqual(branch.events.filter(e => e.type === 'scenario').map(e => e.time), [1.1, 1.3]);
  assert.equal(state.options.targets, 3, 'applying branch scenarios does not mutate saved options');
  const beforeExpiry = parent.remaining('fists');
  parent.advance(0.1);
  assert.ok(Math.abs(parent.remaining('fists') - (beforeExpiry - 0.1)) < 1e-8,
    'SCK ground expiry does not apply duplicate CDR after the target changes');
});

test('a time-zero untargetable scenario rejects attacks and queue attempts while buffs remain explicit', () => {
  const c = new Combat({ encounterEvents: [{ at: 0, attackable: false }, { at: 0.8, attackable: true }] });
  assert.equal(c.attackable, false);
  assert.equal(c.recommend().blocker, 'no-target');
  assert.equal(c.cast('palm').status, 'rejected');
  assert.equal(c.cast('tiger').status, 'executed');
  c.advance(0.7);
  assert.equal(c.cast('palm').status, 'rejected', 'unattackable input never queues for a future target');
  assert.equal(c.queue, null);
  c.advance(0.1);
  assert.equal(c.cast('palm').status, 'queued');
  c.advance(0.1);
  assert.equal(c.casts.at(-1).skill, 'palm');
  assert.equal(c.hits.at(-1).targets, 1);
});

test('queue admission accounts for a target becoming untargetable before the GCD ends', () => {
  const c = new Combat({ encounterEvents: [{ at: 0.9, attackable: false }] });
  c.cast('blackout'); c.advance(0.8);
  assert.equal(c.cast('palm').ok, false);
  assert.equal(c.queue, null);
  assert.equal(c.attackable, true, 'projection must not apply the future event to the parent');
  assert.equal(c.options.targets, 1);
});

for (const skill of ['fists', 'crane', 'conduit']) {
  test(`compact ${skill} fork retains channel timing, future damage, counters and independent options`, () => {
    const parent = new Combat({ initialChi: 6 });
    if (skill === 'conduit') {
      parent.cast('tiger'); parent.advance(1);
    }
    parent.cast(skill); parent.advance(0.3);
    const state = structuredClone(parent.saveState({ history: false }));
    const branch = Combat.fromState(state);
    assert.equal(branch.channel.skill, skill);
    assert.deepEqual(branch.attempts, []);
    assert.deepEqual(branch.summary(), parent.summary());
    const untouched = parent.saveState();
    branch.advance(4);
    assert.deepEqual(parent.saveState(), untouched);
    parent.advance(4);
    assert.deepEqual(branch.summary(), parent.summary());
    assert.deepEqual(branch.snapshot(), parent.snapshot());
    assert.equal(branch.randomState, parent.randomState);
    assert.deepEqual(branch.pending, parent.pending);
    assert.deepEqual(branch.hits, parent.hits.filter(h => h.time > state.time));
  });
}

test('restored queue is revalidated at execution and retains its attempt id when a prerequisite changes', () => {
  const parent = new Combat();
  parent.cast('palm'); parent.advance(0.8);
  const queued = parent.cast('fists');
  assert.equal(queued.status, 'queued');
  const branch = Combat.fromState(parent.saveState({ history: false }));
  branch.chi = 0;
  branch.advance(0.2);
  assert.equal(branch.queue, null);
  assert.equal(branch.casts.length, 0);
  assert.equal(branch.attempts.at(-1).status, 'rejected');
  assert.equal(branch.attempts.at(-1).attemptId, queued.attemptId);
  assert.equal(parent.queue, 'fists');
  parent.advance(0.2);
  assert.equal(parent.casts.at(-1).skill, 'fists');
});
