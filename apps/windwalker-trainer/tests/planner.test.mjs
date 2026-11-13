import test from 'node:test';
import assert from 'node:assert/strict';
import { Worker } from 'node:worker_threads';
import { once } from 'node:events';
import { Combat } from '../dist/combat.js';
import { createPlan } from '../dist/planner.js';
import { SCENARIOS, buildScenario } from '../dist/scenarios.js';
import { advanceReference } from '../dist/reference.js';
import { ACTION_SLOTS, slotAction } from '../dist/actionbar.js';
import { handlePlannerMessage } from '../dist/planner-worker.js';

test('planning forks the actual current state and leaves its parent unchanged', () => {
  const combat = new Combat({ initialChi: 6, duration: 45 });
  assert.ok(combat.cast('fists').ok);
  combat.advance(0.5);
  const before = combat.saveState();
  const plan = createPlan(combat);
  assert.deepEqual(combat.saveState(), before);
  assert.equal(plan.decision.action, 'wait');
  assert.equal(plan.sequence[0].time, 0.5);
  assert.ok(plan.sequence.every(action => action.time >= combat.time));
  assert.ok(plan.sequence.every(action => action.time <= combat.time + plan.horizon));
  assert.ok(plan.alternatives[0].mean > 0, 'pending current-channel damage survives the fork');
});

test('scenario presets build detached combats at legal crit and resource checkpoints', () => {
  assert.deepEqual(SCENARIOS.map(scenario => scenario.id),
    ['burst-single', 'burst-aoe', 'crit-branch', 'resource', 'sustain', 'dungeon-waves']);
  for (const id of ['crit-branch', 'resource']) {
    const combat = buildScenario(id);
    assert.ok(combat.time > 0);
    assert.ok(combat.casts.length > 0);
    assert.ok(combat.attempts.every(attempt => attempt.status === 'executed'));
    assert.equal(combat.clippedFists, 0);
    assert.ok(combat.pending.every(event => typeof event.type === 'string'));
    assert.ok(Number.isFinite(createPlan(combat).alternatives[0].mean));
  }
});

test('sample streams are deterministic, independent of hidden live RNG and options.seed', () => {
  const combat = buildScenario('crit-branch');
  const sibling = Combat.fromState(combat.saveState());
  sibling.randomState = 7;
  sibling.options.seed = 0xabcdef;
  const settings = { mode: 'search', horizon: 8, samples: 4 };
  const before = combat.saveState();
  const siblingBefore = sibling.saveState();
  combat.random = () => { throw new Error('The live random stream must never be read'); };
  const plan = createPlan(combat, settings);
  assert.deepEqual(createPlan(combat, settings), plan);
  assert.deepEqual(createPlan(sibling, settings), plan);
  assert.deepEqual(combat.saveState(), before);
  assert.deepEqual(sibling.saveState(), siblingBefore);
  assert.equal(new Set(plan.sampling.seeds).size, 4);
  assert.ok(plan.sampling.seeds.every(seed => seed > 0));
  sibling.energy -= 1;
  assert.notEqual(createPlan(sibling, settings).sampling.observedHash, plan.sampling.observedHash);
});

test('APL rolls the current compact state forward exactly as the existing reference does', () => {
  const combat = new Combat({ duration: 45, bloodlust: true });
  advanceReference(combat, 17.2);
  const state = combat.saveState({ history: false });
  const plan = createPlan(combat, { samples: 4, maxActions: 12 });
  const damages = [];
  let first;
  for (const seed of plan.sampling.seeds) {
    const branch = Combat.fromState(state);
    branch.randomState = seed;
    branch.options.seed = seed;
    advanceReference(branch, plan.evaluationHorizon);
    damages.push(branch.damage - state.damage);
    first ??= branch;
  }
  assert.equal(plan.alternatives.length, 1);
  assert.equal(plan.alternatives[0].baseline, true);
  assert.ok(Math.abs(plan.alternatives[0].mean -
    damages.reduce((sum, damage) => sum + damage, 0) / damages.length) < 1e-6);
  const expected = [...first.casts, ...first.controls]
    .filter(action => action.time < state.time + plan.horizon - 1e-7)
    .sort((a, b) => a.time - b.time || Number(b.skill === 'cancel') - Number(a.skill === 'cancel'))
    .map(({ time, skill, spell }) => ({ time, skill, spell }));
  const actual = plan.sequence.filter(action => action.skill)
    .map(({ time, skill, spell }) => ({ time, skill, spell }));
  assert.deepEqual(actual, expected.slice(0, actual.length));
  assert.ok(actual.length > 0);
  assert.ok(actual.every(action => action.time >= 17.2));
  assert.equal(plan.evaluationHorizon, 14);
});

test('scoring includes four seconds of continuation while the displayed sequence stops at the horizon', () => {
  const combat = buildScenario('burst-aoe', { duration: 60 });
  const plan = createPlan(combat, { horizon: 8, samples: 1, maxActions: 12 });
  assert.equal(plan.evaluationHorizon, 12);
  assert.equal(plan.tail, 4);
  const branch = Combat.fromState(combat.saveState({ history: false }));
  branch.randomState = plan.sampling.seeds[0];
  branch.options.seed = plan.sampling.seeds[0];
  advanceReference(branch, 8);
  const beforeTail = branch.damage - combat.damage;
  advanceReference(branch, 4);
  assert.ok(plan.alternatives[0].mean > beforeTail);
  assert.ok(Math.abs(plan.alternatives[0].mean - (branch.damage - combat.damage)) < 1e-6);
  assert.ok(plan.sequence.every(action => action.time < 8));
});

test('search always retains the baseline and exposes local model comparison with uncertainty', () => {
  const combat = buildScenario('burst-single');
  const plan = createPlan(combat, { mode: 'search', samples: 1, maxActions: 3 });
  assert.equal(plan.method, 'search');
  assert.equal(plan.uncertain, true, 'one sample cannot establish confidence');
  assert.ok(plan.sequence.length <= 3);
  assert.ok(plan.alternatives.some(candidate => candidate.baseline));
  assert.ok(plan.alternatives.some(candidate => candidate.id === 'wait'));
  assert.ok(plan.alternatives.length <= 8, 'first-action search stays bounded');
  const legalInputs = new Set(Object.keys(ACTION_SLOTS).map(slot => slotAction(combat, slot)));
  for (const candidate of plan.alternatives) {
    if (candidate.skill) {
      assert.ok(legalInputs.has(candidate.skill));
      assert.ok(combat.available(candidate.skill).ok);
    }
    assert.equal(candidate.unit, 'core-model-damage');
    assert.ok(Number.isFinite(candidate.mean) && Number.isFinite(candidate.spread));
    assert.equal(candidate.samples, 1);
  }
  assert.match(plan.scope, /不保证全局最优/);
  assert.ok(plan.sequence.slice(1).every(action => action.conditional));
});

test('physical replacement slots cannot introduce hidden tiger, zenith or a separate wind input', () => {
  const combat = new Combat({ initialChi: 6 });
  combat.cast('tiger'); combat.advance(1); combat.cast('zenith');
  const plan = createPlan(combat, { mode: 'search', samples: 1 });
  const candidates = plan.alternatives.map(candidate => candidate.skill);
  assert.ok(!candidates.includes('tiger'));
  assert.ok(!candidates.includes('zenith'));
  assert.ok(!candidates.includes('wind'));
  assert.ok(candidates.includes('stomp'));
});

test('wind is represented as a sun input and an actual wind spell', () => {
  const combat = new Combat({ initialChi: 6 });
  combat.advance(5);
  combat.setBuff('wind', 15);
  const plan = createPlan(combat, { mode: 'search', samples: 1 });
  const candidate = plan.alternatives.find(candidate => candidate.skill === 'sun');
  assert.equal(candidate.action, 'wind');
  if (plan.decision.skill === 'sun') {
    assert.equal(plan.decision.action, 'wind');
    assert.equal(plan.sequence[0].skill, 'sun');
    assert.equal(plan.sequence[0].spell, 'wind');
  }
});

test('protected fists waits without suggesting a clip or a cancel', () => {
  const combat = new Combat({ initialChi: 6, inputMode: 'protected' });
  combat.cast('fists'); combat.advance(0.3);
  const before = combat.saveState();
  const plan = createPlan(combat, { mode: 'search', samples: 1 });
  assert.equal(plan.decision.action, 'wait');
  assert.ok(plan.alternatives.every(candidate => candidate.skill === null));
  assert.ok(plan.sequence.filter(action => action.skill)
    .every(action => action.time >= combat.channel.end - 1e-7));
  assert.deepEqual(combat.saveState(), before);
});

test('indistinguishable candidates retain the baseline and explicitly report uncertainty', () => {
  const combat = new Combat({ initialChi: 6, inputMode: 'protected' });
  combat.cast('fists'); combat.advance(0.3);
  const plan = createPlan(combat, { mode: 'search', samples: 4 });
  assert.equal(plan.alternatives.length, 2);
  assert.equal(plan.alternatives[0].mean, plan.alternatives[1].mean);
  assert.equal(plan.uncertain, true);
  assert.equal(plan.decision.action, 'wait');
  assert.equal(plan.decision.rule, 'protect-fists');
});

test('crane protection and coexistence use the same legality and effects as the engine', () => {
  for (const protectCrane of [false, true]) {
    const combat = new Combat({ initialChi: 6, protectCrane });
    combat.cast('crane'); combat.advance(1);
    const plan = createPlan(combat, { mode: 'search', samples: 1 });
    const fists = plan.alternatives.find(candidate => candidate.skill === 'fists');
    assert.equal(Boolean(fists), !protectCrane);
    const sun = plan.alternatives.find(candidate => candidate.skill === 'sun');
    assert.ok(sun, 'ordinary sun is a legal coexisting action');
    const replay = Combat.fromState(combat.saveState({ history: false }));
    const channel = structuredClone(replay.channel);
    replay.cast('sun');
    assert.deepEqual(replay.channel, channel);
    assert.ok(replay.pending.some(event => event.type === 'craneExpire'));
  }
});

test('cancel is a candidate only for conduit, whose stomp keeps the active channel', () => {
  const combat = new Combat({ initialChi: 2, bloodlust: true });
  combat.cast('tiger'); combat.advance(1); combat.cast('zenith'); combat.cast('conduit');
  combat.advance(0.75);
  const plan = createPlan(combat, { mode: 'search', samples: 1 });
  assert.ok(plan.alternatives.some(candidate => candidate.skill === 'cancel'));
  assert.ok(plan.alternatives.some(candidate => candidate.skill === 'stomp'));
  const branch = Combat.fromState(combat.saveState({ history: false }));
  const channelId = branch.channel.id;
  branch.cast('stomp');
  assert.equal(branch.channel.id, channelId);
  branch.cancel();
  assert.ok(branch.buffLeft('greatJade') > 0);
  assert.equal(combat.channel.id, channelId);
  for (const id of ['burst-single', 'resource']) {
    const other = createPlan(buildScenario(id), { mode: 'search', samples: 1 });
    assert.ok(!other.alternatives.some(candidate => candidate.skill === 'cancel'));
  }
});

test('queued inputs survive the fork without changing or consuming the live queue', () => {
  const combat = new Combat({ initialChi: 0 });
  combat.cast('palm'); combat.advance(0.8);
  assert.equal(combat.cast('fists').queued, true);
  const before = combat.saveState();
  const plan = createPlan(combat, { samples: 1 });
  assert.ok(plan.sequence.some(action => action.skill === 'fists' && Math.abs(action.time - 1) < 1e-7));
  assert.deepEqual(combat.saveState(), before);
});

test('declared single sun outcome is visible to the branch without forcing subsequent sun casts', () => {
  const declared = [{ mainCrit: true, dawnTriggered: true, dawnCrit: false }];
  const combat = buildScenario('crit-branch', { sunOutcomes: declared });
  const plan = createPlan(combat, { samples: 4 });
  assert.equal(combat.sunCount, 0);
  assert.equal(plan.decision.skill, 'sun');
  for (const seed of plan.sampling.seeds) {
    const branch = Combat.fromState(combat.saveState({ history: false }));
    branch.randomState = seed;
    branch.cast('sun');
    const result = branch.events.find(event => event.type === 'sunResult');
    assert.equal(result.mainCrit, true);
    assert.equal(result.dawnTriggered, true);
    assert.equal(result.dawnCrit, false);
    assert.equal(branch.sunCount, 1);
    assert.equal(branch.options.sunOutcomes[1], undefined);
    assert.equal(branch.options.critMode, 'random');
  }
  assert.equal(combat.sunCount, 0);
  assert.deepEqual(declared, [{ mainCrit: true, dawnTriggered: true, dawnCrit: false }]);
});

test('public dungeon events change live targets and attackability at the declared checkpoints', () => {
  const combat = buildScenario('dungeon-waves');
  assert.equal(combat.options.targets, 5);
  combat.advance(18);
  assert.equal(combat.options.targets, 1);
  combat.advance(7);
  assert.equal(combat.attackable, false);
  const before = combat.saveState();
  const plan = createPlan(combat, { samples: 1, maxActions: 12 });
  assert.equal(plan.decision.action, 'wait');
  assert.equal(plan.decision.blocker, 'no-target');
  assert.ok(plan.sequence.some(action => action.skill && action.time >= 30));
  assert.ok(plan.sequence.filter(action => action.skill).every(action => action.time >= 30));
  assert.deepEqual(combat.saveState(), before);
  combat.advance(5);
  assert.equal(combat.options.targets, 5);
  assert.equal(combat.attackable, true);
});

test('planning during a permanent untargetable window scores no imaginary target damage', () => {
  const combat = new Combat({ initialChi: 6, encounterEvents: [{ at: 0.2, attackable: false }] });
  combat.cast('crane'); combat.advance(0.2);
  const plan = createPlan(combat, { samples: 1 });
  assert.equal(plan.alternatives[0].mean, 0);
  assert.equal(plan.decision.action, 'wait');
  assert.ok(plan.sequence.every(action => action.skill === null));
});

test('scenario option overrides and nested arrays never mutate presets or caller input', () => {
  const before = structuredClone(SCENARIOS);
  const options = { targets: 3, duration: 70, inputMode: 'protected',
    encounterEvents: [{ at: 2, targets: 2 }], sunOutcomes: [{ mainCrit: false, dawnTriggered: false }] };
  const combat = buildScenario('dungeon-waves', options);
  assert.equal(combat.options.targets, 3);
  assert.equal(combat.options.duration, 70);
  assert.equal(combat.options.inputMode, 'protected');
  combat.advance(2);
  assert.equal(combat.options.targets, 2);
  combat.options.encounterEvents[0].targets = 99;
  combat.options.sunOutcomes[0].mainCrit = true;
  assert.equal(options.encounterEvents[0].targets, 2);
  assert.equal(options.sunOutcomes[0].mainCrit, false);
  assert.deepEqual(SCENARIOS, before);
  assert.equal(buildScenario('sustain').options.duration, 120);
  assert.throws(() => buildScenario('missing'), /Unknown scenario/);
});

test('each preset preview replays legal physical inputs on its first independent sample', () => {
  for (const { id } of SCENARIOS) {
    const combat = buildScenario(id);
    const plan = createPlan(combat, { mode: 'search', samples: 1, maxActions: 12 });
    const replay = Combat.fromState(combat.saveState({ history: false }));
    replay.randomState = plan.sampling.seeds[0];
    replay.options.seed = plan.sampling.seeds[0];
    for (const action of plan.sequence) {
      replay.advance(Math.max(0, action.time - replay.time));
      if (!action.skill) continue;
      if (action.skill === 'cancel') {
        assert.equal(replay.channel?.skill, 'conduit', id);
        assert.ok(replay.cancel());
      } else {
        assert.ok(Object.keys(ACTION_SLOTS).some(slot => slotAction(replay, slot) === action.skill), id);
        assert.ok(replay.available(action.skill).ok, `${id}: ${action.skill} at ${action.time}`);
        const result = replay.cast(action.skill);
        assert.ok(result.ok && !result.queued, `${id}: ${action.skill} executes immediately`);
        assert.equal(replay.casts.at(-1).spell, action.spell);
      }
    }
    assert.equal(replay.clippedFists, 0);
  }
});

test('an ended session has no future casts and never scores beyond the declared encounter', () => {
  const combat = new Combat({ duration: 1 });
  combat.advance(1);
  const plan = createPlan(combat, { mode: 'search', samples: 1 });
  assert.equal(plan.decision.skill, null);
  assert.equal(plan.decision.wait, 0);
  assert.equal(plan.evaluationHorizon, 0);
  assert.equal(plan.uncertain, false);
  assert.equal(plan.alternatives.length, 1);
  assert.equal(plan.alternatives[0].mean, 0);
  assert.ok(plan.sequence.every(action => action.skill === null));
});

test('worker handler preserves revision, detaches state and reports recoverable errors', () => {
  const state = buildScenario('resource').saveState({ history: false });
  const before = structuredClone(state);
  const message = handlePlannerMessage({ revision: 19, state, settings: { samples: 1 } });
  assert.equal(message.revision, 19);
  assert.equal(message.method, 'apl');
  assert.ok(message.decision && message.sequence);
  assert.deepEqual(state, before);
  const error = handlePlannerMessage({ revision: 20, state: null });
  assert.equal(error.revision, 20);
  assert.equal(typeof error.error, 'string');
});

test('module worker responds asynchronously with the same revision so a caller can discard stale plans', async () => {
  const moduleURL = new URL('../dist/planner-worker.js', import.meta.url).href;
  const bootstrap = `
    import { parentPort } from 'node:worker_threads';
    globalThis.WorkerGlobalScope = { [Symbol.hasInstance]: () => true };
    globalThis.addEventListener = (type, callback) => parentPort.on(type, data => callback({ data }));
    globalThis.postMessage = message => parentPort.postMessage(message);
    await import(${JSON.stringify(moduleURL)});
  `;
  const worker = new Worker(new URL(`data:text/javascript,${encodeURIComponent(bootstrap)}`));
  try {
    const state = buildScenario('burst-single').saveState({ history: false });
    const responses = [];
    worker.on('message', result => responses.push(result));
    worker.postMessage({ revision: 1, state, settings: { samples: 1 } });
    const first = (await once(worker, 'message'))[0];
    assert.equal(first.revision, 1);
    worker.postMessage({ revision: 2, state, settings: { mode: 'search', samples: 1 } });
    const second = (await once(worker, 'message'))[0];
    assert.equal(second.revision, 2);
    assert.equal(second.method, 'search');
    const latestRevision = 2;
    assert.deepEqual(responses.filter(result => result.revision === latestRevision).map(result => result.revision), [2]);
  } finally {
    await worker.terminate();
  }
});
