import test from 'node:test';
import assert from 'node:assert/strict';
import { Combat } from '../dist/combat.js';
import { reviewRoutine } from '../dist/routines.js';
import { RoutineRunner } from '../dist/routine-runner.js';
import { critFeedback } from '../dist/feedback.js';

test('explicit SCK cancellation describes preserved ground work, not clipped fists', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('crane'); c.advance(0.1); c.cancel({ source: 'keyboard', key: 'X' });
  const row = reviewRoutine(c).rows.find(row => row.skill === 'cancel');
  assert.equal(row.status, 'neutral');
  assert.match(row.note, /独立伤害脉冲和延迟减冷却仍保留/);
  assert.doesNotMatch(row.note, /取消怒雷/);
});

test('review uses the targets observed before a cast when later waves change them', () => {
  const c = new Combat({ initialChi: 6, targets: 5 });
  c.rhythm = 4;
  c.cast('sun');
  c.options.targets = 1;
  const row = reviewRoutine(c).rows.find(row => row.skill === 'sun');
  assert.match(row.note, /群体套装由旭日消费/);
});

test('historical single-target Wind review survives later target changes', () => {
  const c = new Combat({ initialChi: 6, targets: 1 });
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('fists'); c.advance(2);
  c.setBuff('wind', 10); c.cast('sun');
  const before = reviewRoutine(c).rows.at(-1);
  assert.match(before.note, /疾风/);
  c.options.targets = 5;
  assert.deepEqual(reviewRoutine(c).rows.at(-1), before);
});

test('same-timestamp cancellations and casts retain their execution order after restore', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('crane'); c.advance(1); c.cancel();
  c.cast('fists'); c.cancel();
  const restored = Combat.fromState(c.saveState());
  assert.deepEqual(reviewRoutine(restored).rows.map(row => row.skill), ['crane', 'cancel', 'fists', 'cancel']);
  assert.equal(new Set([...restored.casts, ...restored.controls].map(row => row.actionId)).size, 4);
});

test('the routine begins at the observed opener and advances only after execution', () => {
  const c = new Combat();
  const runner = new RoutineRunner(c);
  assert.equal(runner.graph.prefix.find(n => n.id === runner.cursorNodeId).skill, 'palm');
  runner.beforeAction(c); c.cast('palm'); runner.observe(c);
  assert.equal(runner.history[0].status, 'matched');
});

test('critical result feedback does not pretend that double crit guarantees ready fists', () => {
  const c = new Combat({ initialChi: 6, critMode: 'double' });
  c.cast('fists'); c.advance(4); c.cast('sun');
  const feedback = critFeedback(c.events.find(e => e.type === 'sunResult'));
  assert.equal(feedback.label, '双暴');
  assert.equal(feedback.ready, false);
});

test('review distinguishes an actual clip from a legal filler or reference deviation', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('tiger'); c.advance(1); c.cast('zenith'); c.cast('fists');
  c.advance(1); c.cast('palm');
  const r = reviewRoutine(c);
  assert.ok(r.findings.some(f => f.kind === 'error' && /断条/.test(f.title)));
  assert.ok(r.rows.some(row => row.skill === 'palm'));
  assert.ok(!r.findings.some(f => /不符合固定顺序/.test(f.title)));
});

test('single-target wind can consume tier without being labeled a missing crane error', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('fists'); c.advance(4); c.setBuff('wind', 15); c.cast('sun');
  const r = reviewRoutine(c);
  assert.ok(r.rows.findLast(row => row.skill === 'sun').note.includes('疾风'));
  assert.ok(!r.findings.some(f => f.kind === 'error' && /神鹤/.test(f.title)));
});

test('a second Zenith and later Jade instance cannot complete a missed historical window', () => {
  const c = new Combat();
  c.cast('zenith');
  const firstWindow = c.windows.find(w => w.name === 'avatar');
  c.advance(20); c.cast('zenith'); c.cast('fists');
  const cast = c.casts.at(-1);
  assert.equal(cast.atStart.activeWindows.includes(firstWindow.id), false);
  const review = reviewRoutine(c);
  assert.ok(review.findings.some(f => f.time === firstWindow.start && /青龙段/.test(f.title)));
});

test('fists that interrupts conduit is reviewed as a great-jade start', () => {
  const c = new Combat({ initialChi: 6 });
  c.cast('tiger'); c.advance(1); c.cast('conduit'); c.advance(0.75); c.cast('fists');
  const r = reviewRoutine(c);
  assert.match(r.rows.at(-1).note, /青龙内/);
  assert.equal(c.casts.at(-1).before.buffs.greatJade, 0);
  assert.equal(c.casts.at(-1).atStart.buffs.greatJade, 6);
});

test('explicit X cancellation keeps its own input and before/after snapshots in review', () => {
  const c = new Combat();
  c.cast('tiger'); c.advance(1); c.cast('conduit'); c.advance(0.75);
  c.cancel({ source: 'keyboard', key: 'X' });
  const row = reviewRoutine(c).rows.find(row => row.skill === 'cancel');
  assert.equal(row.input.key, 'X');
  assert.equal(row.before.channel.skill, 'conduit');
  assert.equal(row.after.buffs.greatJade, 6);
});

test('queued attacks retain the original input key rather than a later binding', () => {
  const c = new Combat();
  c.cast('palm', { source: 'keyboard', key: '2', slot: 'palm' });
  c.advance(0.8);
  c.cast('fists', { source: 'keyboard', key: 'F', slot: 'fists' });
  c.advance(0.2);
  assert.equal(c.casts[0].input.key, '2');
  assert.equal(c.casts.at(-1).input.key, 'F');
});
