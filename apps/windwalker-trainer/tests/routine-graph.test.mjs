import test from "node:test";
import assert from "node:assert/strict";
import { Combat } from "../dist/combat.js";
import { ACTION_SLOTS, slotAction } from "../dist/actionbar.js";
import { buildScenario } from "../dist/scenarios.js";
import {
  buildRoutineGraph,
  rebaseRoutineGraphAtSun,
} from "../dist/routine-graph.js";

function readySun() {
  const c = new Combat({ initialChi: 4, duration: 60 });
  c.advance(5);
  c.energy = 60;
  Object.assign(c.cooldowns, { fists: 18, tiger: 80, conduit: 80, dragon: 8 });
  c.zenithRecharge = [90, 180];
  return c;
}

function execute(c, node) {
  c.advance(Math.max(0, node.time - c.time));
  if (node.kind === "wait") {
    c.advance(node.duration);
    return;
  }
  if (node.kind === "cancel") {
    assert.ok(c.cancel());
    return;
  }
  assert.equal(slotAction(c, node.slot), node.skill);
  assert.ok(
    c.available(node.skill).ok,
    `${node.skill} must be legal at ${c.time}`,
  );
  assert.equal(c.cast(node.skill).status, "executed");
}

test("the graph is detached, deterministic and independent of the hidden live RNG", () => {
  const c = buildScenario("burst-single");
  const sibling = Combat.fromState(c.saveState());
  sibling.randomState = 7;
  sibling.options.seed = 42;
  const before = c.saveState();
  c.random = () => {
    throw new Error("Live RNG must not be read");
  };
  const graph = buildRoutineGraph(c);
  assert.deepEqual(buildRoutineGraph(c), graph);
  assert.deepEqual(buildRoutineGraph(sibling), graph);
  assert.deepEqual(c.saveState(), before);
  assert.deepEqual(structuredClone(graph), graph);
  graph.prefix[0].spell = "changed";
  assert.notEqual(buildRoutineGraph(c).prefix[0].spell, "changed");
});

test("the shared prefix includes exactly the first physical Sun and six distinct outcomes follow it", () => {
  const c = buildScenario("burst-single");
  const graph = buildRoutineGraph(c);
  assert.ok(graph.fork);
  assert.equal(graph.prefix.at(-1).skill, "sun");
  assert.equal(graph.prefix.filter((n) => n.skill === "sun").length, 1);
  assert.equal(graph.fork.triggerNodeId, graph.prefix.at(-1).id);
  assert.equal(graph.fork.branches.length, 6);
  const outcomes = graph.fork.branches.map((b) => b.outcome);
  assert.equal(
    new Set(
      outcomes.map((o) => `${o.mainCrit}:${o.dawnTriggered}:${o.dawnCrit}`),
    ).size,
    6,
  );
  for (const mainCrit of [false, true]) {
    assert.ok(
      outcomes.some((o) => o.mainCrit === mainCrit && !o.dawnTriggered),
    );
    assert.ok(
      outcomes.some(
        (o) =>
          o.mainCrit === mainCrit && o.dawnTriggered && o.dawnCrit === false,
      ),
    );
    assert.ok(
      outcomes.some(
        (o) =>
          o.mainCrit === mainCrit && o.dawnTriggered && o.dawnCrit === true,
      ),
    );
  }
  const ids = [
    ...graph.prefix,
    ...graph.fork.branches.flatMap((b) => b.nodes),
  ].map((n) => n.id);
  assert.equal(new Set(ids).size, ids.length);
});

test("every branch comes from the exact pre-Sun parent and forces only that result", () => {
  const c = readySun();
  c.options.sunOutcomes = [
    { mainCrit: true },
    { mainCrit: false, dawnTriggered: false },
  ];
  const before = c.saveState();
  const graph = buildRoutineGraph(c);
  for (const branch of graph.fork.branches) {
    const expected = Combat.fromState(before);
    expected.randomState = graph.displaySeed;
    expected.options.sunOutcomes[expected.sunCount] = { ...branch.outcome };
    expected.cast("sun");
    assert.equal(branch.summary.chi, expected.chi);
    assert.equal(branch.summary.fists, expected.remaining("fists"));
    assert.equal(
      branch.summary.jadeLeft,
      Math.max(
        ...["jade", "greatJade", "avatar"].map((name) =>
          expected.buffLeft(name),
        ),
      ),
    );
    assert.ok(branch.nodes.every((n) => n.time >= expected.time));
    assert.ok(branch.nodes.every((n) => n.conditional));
  }
  assert.deepEqual(c.saveState(), before);
});

test("all six generated continuations replay legally and stop at the next unresolved Sun or Blackout", () => {
  const c = buildScenario("crit-branch");
  const graph = buildRoutineGraph(c, { maxActions: 12, horizon: 20 });
  for (const branch of graph.fork.branches) {
    const replay = Combat.fromState(c.saveState());
    replay.randomState = graph.displaySeed;
    for (const node of graph.prefix.slice(0, -1)) execute(replay, node);
    replay.options.sunOutcomes[replay.sunCount] = { ...branch.outcome };
    execute(replay, graph.prefix.at(-1));
    for (const [index, node] of branch.nodes.entries()) {
      if (node.skill === "sun" || node.skill === "blackout") {
        assert.equal(index, branch.nodes.length - 1);
        assert.equal(node.unresolved, true);
      }
      execute(replay, node);
    }
  }
  assert.match(graph.scope, /固定|展示/);
  assert.match(graph.scope, /不保证|非全局/);
});

test("wind retains the physical Sun input and replacement slots stay executable", () => {
  const c = readySun();
  c.setBuff("wind", 15);
  const graph = buildRoutineGraph(c);
  assert.equal(graph.prefix[0].skill, "sun");
  assert.equal(graph.prefix[0].spell, "wind");
  assert.equal(graph.prefix[0].slot, "sun");
  const opener = buildRoutineGraph(buildScenario("burst-single"), {
    maxActions: 12,
    horizon: 20,
  });
  const nodes = [
    ...opener.prefix,
    ...opener.fork.branches.flatMap((b) => b.nodes),
  ];
  assert.ok(
    nodes.every(
      (n) => !n.skill || n.kind === "cancel" || n.slot in ACTION_SLOTS,
    ),
  );
  assert.ok(
    nodes.filter((n) => n.skill === "conduit").every((n) => n.slot === "tiger"),
  );
  assert.ok(
    nodes.filter((n) => n.skill === "stomp").every((n) => n.slot === "zenith"),
  );
});

test("a bounded prefix without Sun has no fork and coalesces resource waits", () => {
  const c = new Combat({ duration: 60, initialChi: 0 });
  c.attackable = false;
  const graph = buildRoutineGraph(c);
  assert.equal(graph.fork, null);
  assert.equal(graph.prefix.length, 1);
  assert.equal(graph.prefix[0].kind, "wait");
  assert.equal(graph.prefix[0].duration, 14);
  assert.equal(buildRoutineGraph(new Combat(), { maxActions: 1 }).fork, null);
});

test("protected FoF is represented by a wait through its final pulse", () => {
  const c = new Combat({ initialChi: 6, inputMode: "protected" });
  c.cast("fists");
  c.advance(0.2);
  const end = c.channel.end;
  const graph = buildRoutineGraph(c);
  assert.equal(graph.prefix[0].kind, "wait");
  assert.ok(
    Math.abs(graph.prefix[0].time + graph.prefix[0].duration - end) < 1e-7,
  );
  assert.ok(
    graph.prefix
      .filter((n) => n.kind !== "wait")
      .every((n) => n.time >= end - 1e-7),
  );
  assert.ok(
    graph.prefix.every(
      (n) => n.kind !== "cancel" || n.channelSkill !== "fists",
    ),
  );
});

test("phase labels retain separate identities for successive windows of the same type", () => {
  const c = new Combat({ initialChi: 6, duration: 120 });
  c.cast("zenith");
  c.advance(20);
  c.cast("zenith");
  c.setBuff("jade", 6);
  c.advance(6);
  c.setBuff("jade", 6);
  const graph = buildRoutineGraph(c);
  assert.deepEqual(
    graph.phases.map((p) => p.id),
    ["first-zenith", "small-jade", "great-jade", "second-zenith", "sustain"],
  );
  assert.ok(graph.phases.every((p) => p.name && p.label));
  const small = graph.phases.find((p) => p.id === "small-jade");
  assert.ok(small.windows.length >= 2);
  assert.equal(
    new Set(small.windows.map((w) => w.id)).size,
    small.windows.length,
  );
  assert.equal(graph.prefix[0].phase, "small-jade");
  assert.equal(
    graph.prefix[0].phaseWindowId,
    c.windows.findLast((w) => w.name === "jade").id,
  );
});

test("completed sessions produce an empty route without inventing a legal action", () => {
  const c = new Combat({ duration: 1 });
  c.advance(1);
  const graph = buildRoutineGraph(c);
  assert.deepEqual(graph.prefix, []);
  assert.equal(graph.fork, null);
});

test("window-opening nodes belong to the newly opened phase and reference an existing phase instance", () => {
  const graph = buildRoutineGraph(buildScenario("burst-single"));
  const zenith = graph.prefix.find((n) => n.skill === "zenith");
  assert.equal(zenith.phase, "first-zenith");
  const windows = graph.phases.flatMap((p) => p.windows);
  for (const node of [
    ...graph.prefix,
    ...graph.fork.branches.flatMap((b) => b.nodes),
  ]) {
    if (node.phaseWindowId != null) {
      assert.ok(
        windows.some(
          (w) =>
            w.instanceId === node.phaseInstanceId &&
            w.windowId === node.phaseWindowId,
        ),
        `${node.id} must reference a known window instance`,
      );
    }
  }
  assert.ok(
    graph.fork.branches.every(
      (b) => b.nodes.find((n) => n.skill === "dragon")?.phase === "small-jade",
    ),
  );
});

test("Sun rebase is pure, retains stable identities and uses current cooldown work, resources and windows", () => {
  const c = readySun();
  const graph = buildRoutineGraph(c, { id: "stable" });
  const original = structuredClone(graph);
  c.advance(0.2);
  c.chi = 3;
  c.rhythm = 2;
  c.setBuff("greatJade", 6);
  c.setBuff("wind", 15);
  const before = c.saveState();
  c.random = () => {
    throw new Error("Sun rebase must not read live RNG");
  };
  const rebased = rebaseRoutineGraphAtSun(c, graph);
  assert.deepEqual(graph, original);
  assert.deepEqual(c.saveState(), before);
  assert.equal(rebased.id, graph.id);
  assert.equal(rebased.createdAt, graph.createdAt);
  assert.deepEqual(
    rebased.prefix.map((n) => n.id),
    graph.prefix.map((n) => n.id),
  );
  assert.deepEqual(
    rebased.fork.branches.map((b) => b.id),
    graph.fork.branches.map((b) => b.id),
  );
  assert.equal(rebased.fork.id, graph.fork.id);
  assert.equal(rebased.fork.triggerNodeId, graph.fork.triggerNodeId);
  assert.equal(rebased.prefix.at(-1).time, c.time);
  assert.equal(rebased.prefix.at(-1).spell, "wind");
  assert.equal(rebased.prefix.at(-1).phase, "great-jade");
  for (const branch of rebased.fork.branches) {
    const replay = Combat.fromState(before);
    replay.options.sunOutcomes[replay.sunCount] = structuredClone(
      branch.outcome,
    );
    replay.cast("sun");
    const state = replay.events.findLast((e) => e.type === "sunResult").state;
    assert.equal(branch.summary.chi, state.chi);
    assert.equal(branch.summary.fists, state.cooldowns.fists);
    assert.equal(branch.summary.greatJade, state.buffs.greatJade);
    assert.deepEqual(branch.summary.activeWindows, state.activeWindows);
  }
  const windows = rebased.phases.flatMap((p) => p.windows);
  for (const node of [
    ...rebased.prefix,
    ...rebased.fork.branches.flatMap((b) => b.nodes),
  ]) {
    if (node.phaseWindowId != null)
      assert.ok(windows.some((w) => w.instanceId === node.phaseInstanceId));
  }
});
