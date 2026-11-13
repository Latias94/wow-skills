import test from 'node:test';
import assert from 'node:assert/strict';
import { Combat } from '../dist/combat.js';
import { ACTION_SLOTS, slotAction, slotSpell } from '../dist/actionbar.js';

test('eight action slots use the requested default keyboard layout', () => {
  assert.deepEqual(Object.fromEntries(Object.entries(ACTION_SLOTS).map(([id, slot]) => [id, slot.key])),
    { sun: '1', palm: '2', blackout: '3', tiger: '4', zenith: '5', crane: 'E', fists: 'F', dragon: 'G' });
});

test('bloodlust lasts forty seconds, changes haste and channel time, but not melee GCD', () => {
  const a = new Combat({ initialChi: 6 });
  const b = new Combat({ initialChi: 6, bloodlust: true });
  assert.equal(b.buffLeft('bloodlust'), 40);
  assert.ok(Math.abs(b.haste() / a.haste() - 1.3) < 0.0001);
  a.cast('fists'); b.cast('fists');
  assert.equal(b.gcdEnd, 1);
  assert.ok(b.channel.end < a.channel.end);
  b.advance(40);
  assert.equal(b.buffLeft('bloodlust'), 0);
});

test('casts preserve pre-action state for branch-aware reference review', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('fists'); c.advance(4); c.cast('crane');
  const cast = c.casts.at(-1);
  assert.equal(cast.before.rhythm, 6);
  assert.equal(cast.before.chi, 4);
  assert.ok(cast.before.cooldowns.fists > 0);
  assert.equal(c.rhythm, 0);
});

test('wind replaces the sun icon/action identity, never the blackout slot', () => {
  const c = new Combat({ initialChi: 6 });
  c.setBuff('wind', 15);
  assert.equal(slotSpell(c, 'sun'), 'wind');
  assert.equal(slotSpell(c, 'blackout'), 'blackout');
  c.cast(slotAction(c, 'sun'));
  assert.equal(slotSpell(c, 'sun'), 'sun');
  assert.equal(c.casts.at(-1).spell, 'wind');
});

test('one tiger slot becomes conduit and one zenith slot consumes the two manual stomps', () => {
  const c = new Combat();
  assert.equal(slotAction(c, 'tiger'), 'tiger');
  c.cast(slotAction(c, 'tiger')); c.advance(1);
  assert.equal(slotAction(c, 'tiger'), 'conduit');
  c.cast(slotAction(c, 'zenith'));
  assert.equal(slotAction(c, 'zenith'), 'stomp');
  c.cast(slotAction(c, 'tiger'));
  assert.equal(slotAction(c, 'tiger'), 'conduit');
  c.advance(0.75); c.cast(slotAction(c, 'zenith'));
  c.advance(1); c.cast(slotAction(c, 'zenith'));
  assert.equal(slotAction(c, 'zenith'), 'zenith');
  assert.equal(c.channel.skill, 'conduit');
  c.advance(4);
  assert.equal(slotAction(c, 'tiger'), 'tiger');
});

test('an ordinary attack interrupts conduit, granting great jade before its damage', () => {
  const c = new Combat();
  c.cast('tiger'); c.advance(1); c.cast('conduit'); c.advance(0.75);
  c.cast('palm');
  assert.equal(c.channel, null);
  assert.equal(c.buffLeft('greatJade'), 6);
  assert.equal(c.hits.at(-1).jade, true);
});

test('tiger palm spends energy, generates chi, and respects the fixed GCD', () => {
  const c = new Combat({ seed: 7 });
  assert.equal(c.cast('palm').ok, true);
  assert.equal(c.chi, 4);
  assert.ok(c.energy < 150);
  assert.equal(c.cast('sun').ok, false);
  c.advance(1);
  assert.equal(c.cast('sun').ok, true);
});

test('fists produces five normal hits plus the immediate tier hit', () => {
  const c = new Combat({ seed: 11, initialChi: 6 });
  c.cast('fists');
  assert.equal(c.rhythm, 2);
  c.advance(5);
  const hits = c.hits.filter(e => e.skill === 'fists');
  assert.equal(hits.length, 6);
  assert.equal(c.rhythm, 6);
});

test('whirling dragon requires both core cooldowns to be running', () => {
  const c = new Combat({ initialChi: 6 });
  assert.equal(c.cast('dragon').ok, false);
  c.cast('fists');
  c.advance(4);
  c.cast('sun');
  c.advance(1);
  assert.equal(c.cast('dragon').ok, true);
  assert.ok(c.buffLeft('jade') > 5.9);
});

test('large jade replaces small jade, but not the independent zenith jade', () => {
  const c = new Combat();
  c.cast('tiger');
  c.advance(1);
  c.cast('zenith');
  c.setBuff('jade', 6);
  c.cast('conduit');
  c.cancel();
  assert.equal(c.buffLeft('jade'), 0);
  assert.equal(c.buffLeft('greatJade'), 6);
  assert.ok(c.buffLeft('avatar') > 0);
});

test('zenith has two charges, resets sun, and lasts twenty seconds', () => {
  const c = new Combat();
  c.cast('sun');
  c.advance(1);
  assert.ok(c.remaining('sun') > 0);
  c.cast('zenith');
  assert.equal(c.remaining('sun'), 0);
  assert.equal(c.buffLeft('zenith'), 20);
  assert.equal(c.charges('zenith'), 1);
});

test('forced sun branches advance unbuffed cooldown by four wall seconds per crit', () => {
  const a = new Combat({ critMode: 'none', seed: 42, initialChi: 6 });
  const b = new Combat({ critMode: 'double', seed: 42, initialChi: 6 });
  for (const c of [a, b]) { c.cast('fists'); c.advance(4); c.cast('sun'); c.advance(0.4); }
  assert.ok(Math.abs((a.remaining('fists') - b.remaining('fists')) - 8) < 0.0001);
  assert.equal(b.events.filter(e => e.type === 'sunResult').at(-1).crits, 2);
});

test('current talents use two chi for fists, 55 energy for palm, and thirty-second unhasted dragon', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('palm');
  assert.equal(c.energy, 95);
  c.advance(1);
  c.cast('fists');
  assert.equal(c.chi, 4);
  c.advance(4);
  c.cast('sun'); c.advance(1); c.cast('dragon');
  assert.ok(Math.abs(c.remaining('dragon') - 30 / 1.75) < 0.001);
});

test('recovery rate converts reductions once, not through haste a second time', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('fists'); c.advance(4); c.setBuff('jade', 6);
  const before = c.remaining('fists');
  c.reduce('fists', 4);
  assert.ok(Math.abs(before - c.remaining('fists') - 4 / 1.75) < 0.0001);
});

test('white tiger and conduit use their own spell GCD, and zenith never grants obsidian chi', () => {
  const c = new Combat();
  c.cast('tiger');
  assert.ok(Math.abs(c.gcdEnd - 1 / 1.19) < 0.0001);
  c.advance(1); c.cast('zenith'); c.advance(1);
  const chi = c.chi;
  c.cast('blackout');
  assert.equal(c.chi, chi);
});

test('unspent manual stomps prevent a second zenith; consuming them permits it after the lock', () => {
  const c = new Combat();
  c.cast('zenith'); c.advance(16);
  assert.equal(c.cast('zenith').ok, false);
  c.cast('stomp'); c.advance(1); c.cast('stomp'); c.advance(1);
  assert.equal(c.cast('zenith').ok, true);
});

test('jade accelerates cooldown work, without changing the fixed one-second melee GCD', () => {
  const a = new Combat({ seed: 1, initialChi: 6 });
  const b = new Combat({ seed: 1, initialChi: 6 });
  b.setBuff('jade', 6);
  a.cast('fists'); b.cast('fists');
  assert.equal(a.gcdEnd, 1);
  assert.equal(b.gcdEnd, 1);
  assert.ok(b.channel.end < a.channel.end);
  a.advance(0.5); b.advance(0.5);
  assert.ok(b.cooldowns.fists < a.cooldowns.fists);
});

test('spinning crane consumes tier on cast and retains its ground hits after the next GCD', () => {
  const c = new Combat({ seed: 2 });
  c.rhythm = 6;
  c.cast('crane');
  assert.equal(c.rhythm, 0);
  c.advance(1);
  c.cast('palm');
  c.advance(1);
  assert.equal(c.hits.filter(e => e.skill === 'crane').length, 4);
});

test('clipping fists records incomplete normal pulses rather than granting a full channel', () => {
  const c = new Combat({ seed: 19, initialChi: 6 });
  c.cast('fists'); c.advance(1); c.cast('palm'); c.advance(4);
  assert.ok(c.hits.filter(e => e.skill === 'fists').length < 6);
  assert.ok(c.summary().clippedFists > 0);
});

test('protected inputs reject other skills during FoF without queueing or clipping', () => {
  const c = new Combat({ inputMode: 'protected', initialChi: 6 });
  c.cast('fists');
  c.advance(0.8);
  const pending = structuredClone(c.pending);
  const palm = c.cast('palm', { source: 'keyboard', key: '2' });
  assert.equal(palm.ok, false);
  assert.equal(palm.status, 'rejected');
  assert.equal(c.queue, null);
  assert.deepEqual(c.pending, pending);
  c.advance(0.2);
  const nextPending = structuredClone(c.pending);
  for (const skill of ['sun', 'zenith', 'crane']) assert.equal(c.cast(skill).ok, false);
  assert.deepEqual(c.pending, nextPending);
  c.advance(3);
  assert.equal(c.clippedFists, 0);
  assert.equal(c.hits.filter(h => h.skill === 'fists').length, 6);
  assert.deepEqual(c.attempts.map(a => a.status), ['executed', 'rejected', 'rejected', 'rejected', 'rejected']);
});

test('protectCrane rejects FoF before queue admission while ordinary sun can coexist', () => {
  const c = new Combat({ inputMode: 'protected', protectCrane: true, initialChi: 6, critMode: 'none' });
  c.cast('crane'); c.advance(0.8);
  assert.equal(c.cast('fists').ok, false);
  assert.equal(c.queue, null);
  c.advance(0.2);
  const channelId = c.channel.id;
  assert.equal(c.cast('sun').ok, true);
  assert.equal(c.channel.id, channelId);
  assert.equal(c.clippedFists, 0);
});

test('an unavailable conduit cannot replace a valid queued palm and attempts retain both outcomes', () => {
  const c = new Combat();
  c.cast('blackout'); c.advance(0.8);
  const palm = c.cast('palm', { source: 'keyboard', key: '2' });
  assert.equal(palm.queued, true);
  const conduit = c.cast('conduit', { source: 'keyboard', key: '4' });
  assert.equal(conduit.ok, false);
  assert.equal(c.queue, 'palm');
  c.advance(0.2);
  assert.equal(c.casts.at(-1).skill, 'palm');
  assert.deepEqual(c.attempts.map(a => a.status), ['executed', 'queued', 'rejected', 'executed']);
  const execution = c.attempts.at(-1);
  assert.equal(execution.attemptId, palm.attemptId);
  assert.equal(execution.castId, c.casts.at(-1).castId);
  assert.equal(execution.input.at, 0.8);
});

test('queue rejects cooldowns and chi that remain unavailable at execution but accepts energy regenerated by then', () => {
  const blocked = new Combat({ initialChi: 0 });
  blocked.cast('palm'); blocked.advance(0.8);
  blocked.chi = 0;
  assert.equal(blocked.cast('fists').ok, false);
  assert.equal(blocked.queue, null);
  blocked.chi = 6; blocked.cooldowns.fists = 24;
  assert.equal(blocked.cast('fists').ok, false);
  assert.equal(blocked.queue, null);

  const energy = new Combat();
  energy.cast('blackout'); energy.advance(0.8); energy.energy = 53;
  assert.equal(energy.cast('palm').queued, true);
  energy.advance(0.2);
  assert.equal(energy.casts.at(-1).skill, 'palm');
  assert.equal(energy.casts.at(-1).time, 1);
});

test('fixed seed reproduces hit results across independently constructed sessions', () => {
  const run = () => {
    const c = new Combat({ seed: 9, initialChi: 6 });
    c.cast('fists'); c.advance(4); c.cast('sun'); c.advance(1);
    return c.hits;
  };
  assert.deepEqual(run(), run());
});

test('manual stomp can coexist with conduit without ending the channel', () => {
  const c = new Combat();
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('conduit'); c.advance(0.75);
  c.cast('stomp');
  assert.equal(c.channel.skill, 'conduit');
  assert.equal(c.buffLeft('greatJade'), 0);
  c.advance(4);
  assert.equal(c.hits.filter(h => h.skill === 'conduit').length, 5);
});

test('off-GCD zenith preserves an accepted queued attack', () => {
  const c = new Combat();
  c.cast('palm'); c.advance(0.8);
  assert.equal(c.cast('fists').queued, true);
  c.cast('zenith'); c.advance(0.2);
  assert.equal(c.casts.at(-1).skill, 'fists');
});

test('a queued skill is rechecked when its cooldown expires at the GCD boundary', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('fists'); c.advance(19.2); c.cast('palm'); c.advance(0.8);
  assert.equal(c.cast('fists').queued, true);
  c.advance(0.2);
  assert.equal(c.casts.at(-1).skill, 'fists');
});

test('zenith and its automatic stomp participate in combo identity', () => {
  const c = new Combat();
  c.cast('palm'); c.advance(1); c.cast('zenith'); c.cast('palm');
  assert.equal(c.summary().comboBreaks, 0);
  const b = new Combat(); b.cast('zenith'); b.cast('stomp');
  assert.equal(b.summary().comboBreaks, 1);
});

test('a long first gap does not accumulate uncapped dance bad-luck protection', () => {
  const c = new Combat({ duration: 120, seed: 2048 });
  c.advance(100); c.cast('blackout');
  assert.equal(c.dance, 0);
});

test('zenith charges regenerate serially at ninety and one hundred eighty seconds', () => {
  const c = new Combat({ duration: 200 });
  c.cast('zenith'); c.advance(20); c.cast('zenith');
  assert.equal(c.charges('zenith'), 0);
  c.advance(70);
  assert.equal(c.charges('zenith'), 1);
  c.advance(90);
  assert.equal(c.charges('zenith'), 2);
});

test('elapsed time is capped at session duration and no damage lands after the bell', () => {
  const c = new Combat({ duration: 5, initialChi: 6 });
  c.cast('fists'); c.advance(4); c.cast('sun'); c.advance(20);
  assert.equal(c.time, 5);
  const damage = c.damage;
  c.advance(20);
  assert.equal(c.damage, damage);
  assert.equal(c.cast('palm').ok, false);
});
