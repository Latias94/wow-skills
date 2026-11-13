import test from "node:test";
import assert from "node:assert/strict";
import { Combat } from "../dist/combat.js";
import { buildScenario } from "../dist/scenarios.js";
import { RoutineRunner } from "../dist/routine-runner.js";

function readySun(outcome = {}) {
  const c = new Combat({ initialChi: 4, duration: 60, sunOutcomes: [outcome] });
  c.advance(5);
  c.energy = 60;
  Object.assign(c.cooldowns, { fists: 18, tiger: 80, conduit: 80, dragon: 8 });
  c.zenithRecharge = [90, 180];
  return c;
}

function current(runner) {
  return [
    ...runner.graph.prefix,
    ...(runner.graph.fork?.branches.flatMap((b) => b.nodes) ?? []),
  ].find((n) => n.id === runner.cursorNodeId);
}

test("beforeAction exposes a detached reference anchored to the stable node", () => {
  const c = readySun();
  const runner = new RoutineRunner(c, { id: "lesson" });
  const before = c.saveState();
  const context = runner.beforeAction(c);
  assert.equal(context.graphId, "lesson");
  assert.equal(context.nodeId, runner.cursorNodeId);
  assert.equal(context.expected.skill, "sun");
  assert.equal(context.reference.skill, "sun");
  context.expected.skill = "changed";
  assert.equal(current(runner).skill, "sun");
  assert.deepEqual(c.saveState(), before);
});

test("all six actual results select the exact branch, including main-only versus Dawn-only crit", () => {
  for (const mainCrit of [false, true]) {
    for (const dawnCrit of [null, false, true]) {
      const outcome = { mainCrit, dawnTriggered: dawnCrit !== null, dawnCrit };
      const c = readySun(outcome);
      const runner = new RoutineRunner(c);
      const original = structuredClone(runner.graph);
      const expected = original.fork.branches.find(
        (b) =>
          b.outcome.mainCrit === mainCrit &&
          b.outcome.dawnTriggered === outcome.dawnTriggered &&
          b.outcome.dawnCrit === dawnCrit,
      );
      runner.beforeAction(c);
      const result = c.cast("sun");
      runner.observe(c);
      assert.equal(runner.selectedBranchId, expected.id);
      assert.equal(runner.graph.id, original.id);
      assert.deepEqual(runner.graph.prefix, original.prefix);
      assert.equal(
        runner.graph.fork.branches.find((b) => b.id === expected.id).status,
        "observed-selected",
      );
      assert.ok(
        runner.graph.fork.branches
          .filter((b) => b.id !== expected.id)
          .every((b) => b.status === "observed-not-selected"),
      );
      assert.equal(runner.history[0].castId, result.castId);
      assert.equal(runner.history[0].branchId, expected.id);
      assert.equal(runner.history[0].status, "matched");
      assertSunSummary(
        runner.graph.fork.branches.find((b) => b.id === expected.id).summary,
        c.events.find(
          (e) => e.type === "sunResult" && e.castId === result.castId,
        ).state,
      );
    }
  }
});

test("queued and rejected attempts do not advance, and their executed cast advances exactly once", () => {
  const c = new Combat({ initialChi: 2 });
  const runner = new RoutineRunner(c);
  runner.beforeAction(c);
  c.cast("palm");
  runner.observe(c);
  c.advance(0.8);
  runner.beforeAction(c);
  const nodeId = runner.cursorNodeId;
  const length = runner.history.length;
  assert.equal(c.cast("tiger").status, "queued");
  assert.equal(c.cast("dragon").status, "rejected");
  runner.observe(c);
  assert.equal(runner.cursorNodeId, nodeId);
  assert.equal(runner.history.length, length);
  c.advance(0.2);
  runner.observe(c);
  assert.equal(runner.history.length, length + 1);
  assert.equal(runner.history.at(-1).status, "matched");
  assert.equal(runner.history.at(-1).castId, c.casts.at(-1).castId);
  runner.observe(c);
  assert.equal(runner.history.length, length + 1);
});

test("same-time controls and casts consume actionId order rather than array or timestamp order", () => {
  const c = new Combat({ initialChi: 6 });
  const runner = new RoutineRunner(c);
  c.cast("crane");
  c.advance(1);
  c.cancel();
  c.cast("fists");
  c.cancel();
  runner.observe(c);
  const actions = [...c.casts, ...c.controls].sort(
    (a, b) => a.actionId - b.actionId,
  );
  assert.deepEqual(
    runner.history
      .filter((row) => row.actionId != null)
      .map((row) => row.actionId),
    actions.map((a) => a.actionId),
  );
  assert.deepEqual(
    runner.history
      .filter((row) => row.actionId != null)
      .map((row) => row.castId),
    actions.map((a) => a.castId ?? null),
  );
  assert.ok(runner.history.some((row) => row.status === "deviation"));
});

test("the selected graph remains visible through its fillers and hands off before the next Sun", () => {
  const c = readySun({ mainCrit: true, dawnTriggered: true, dawnCrit: false });
  const runner = new RoutineRunner(c);
  const graphId = runner.graph.id;
  c.cast("sun");
  runner.observe(c);
  const branch = runner.graph.fork.branches.find(
    (b) => b.id === runner.selectedBranchId,
  );
  for (const node of branch.nodes) {
    if (node.unresolved && node.skill === "sun") {
      runner.beforeAction(c, { skill: "sun" });
      assert.notEqual(runner.graph.id, graphId);
      assert.equal(runner.graph.fork.status, "unresolved");
      break;
    }
    assert.equal(runner.graph.id, graphId);
    c.advance(Math.max(0, node.time - c.time));
    if (node.kind === "wait") c.advance(node.duration);
    else if (node.kind === "cancel") c.cancel();
    else c.cast(node.skill);
    runner.observe(c);
  }
  assert.notEqual(runner.graph.id, graphId);
  assert.ok(
    runner.archives.some(
      (a) =>
        a.graph.id === graphId &&
        a.status === "completed" &&
        a.selectedBranchId,
    ),
  );
});

function assertSunSummary(summary, state) {
  assert.equal(summary.time, state.time);
  assert.equal(summary.chi, state.chi);
  assert.equal(summary.energy, state.energy);
  assert.equal(summary.fists, state.cooldowns.fists);
  assert.equal(summary.sun, state.cooldowns.sun);
  for (const name of ["jade", "greatJade", "avatar"])
    assert.equal(summary[name], state.buffs[name]);
  assert.equal(
    summary.jadeLeft,
    Math.max(
      ...["jade", "greatJade", "avatar"].map((name) => state.buffs[name]),
    ),
  );
  assert.deepEqual(summary.activeWindows, state.activeWindows);
  for (const name of ["rhythm", "combo", "dance"])
    assert.equal(summary[name], state[name]);
}

test("a delayed first Sun rebases all outcomes from actual full state without changing prefix identities or evidence", () => {
  const c = buildScenario("burst-single");
  const runner = new RoutineRunner(c);
  const graphId = runner.graph.id;
  const prefixIds = runner.graph.prefix.map((n) => n.id);
  const branchIds = runner.graph.fork.branches.map((b) => b.id);
  for (let i = 0; i < 200 && current(runner)?.skill !== "sun"; i++) {
    const reference = c.recommend();
    if (!reference.skill)
      c.advance(Math.min(reference.wait || 0.05, c.nextBoundary() - c.time));
    else {
      runner.beforeAction(c, { skill: reference.skill });
      if (reference.skill === "cancel") c.cancel();
      else assert.equal(c.cast(reference.skill).status, "executed");
    }
    runner.observe(c);
  }
  assert.equal(current(runner).skill, "sun");
  const completed = structuredClone(runner.graph.prefix.slice(0, runner.index));
  const history = structuredClone(runner.history);
  c.advance(0.3);
  c.chi = 3;
  c.energy = 60;
  c.rhythm = 2;
  c.setBuff("rhythm", 20);
  c.zenithCrit = 0.17;
  assert.equal(c.recommend().skill, "sun");
  const before = c.saveState();
  const context = runner.beforeAction(c, { skill: "sun" });
  assert.equal(context.graphId, graphId);
  assert.equal(context.expected.time, c.time);
  assert.deepEqual(
    runner.graph.prefix.map((n) => n.id),
    prefixIds,
  );
  assert.deepEqual(runner.graph.prefix.slice(0, runner.index), completed);
  assert.deepEqual(
    runner.graph.fork.branches.map((b) => b.id),
    branchIds,
  );
  assert.deepEqual(runner.history.slice(0, history.length), history);
  assert.deepEqual(c.saveState(), before);
  for (const branch of runner.graph.fork.branches) {
    const actual = Combat.fromState(before);
    actual.options.sunOutcomes[actual.sunCount] = structuredClone(
      branch.outcome,
    );
    const result = actual.cast("sun");
    const observed = actual.events.find(
      (e) => e.type === "sunResult" && e.castId === result.castId,
    );
    // Dance is a separate unresolved roll; the six enumerated outcomes constrain Sun and Dawn only.
    assertSunSummary(
      { ...branch.summary, dance: observed.state.dance },
      observed.state,
    );
  }
  const snapshot = structuredClone(runner.graph);
  runner.beforeAction(c, { skill: "sun" });
  assert.deepEqual(runner.graph, snapshot);
  c.options.sunOutcomes[c.sunCount] = {
    mainCrit: false,
    dawnTriggered: true,
    dawnCrit: true,
  };
  runner.beforeAction(c, { skill: "sun" });
  const result = c.cast("sun");
  runner.observe(c);
  const observed = c.events.find(
    (e) => e.type === "sunResult" && e.castId === result.castId,
  );
  assertSunSummary(
    runner.graph.fork.branches.find((b) => b.id === runner.selectedBranchId)
      .summary,
    observed.state,
  );
});

test("timer observations and a different action hint do not rebase an unexecuted Sun every frame", () => {
  const c = readySun();
  const runner = new RoutineRunner(c);
  const original = structuredClone(runner.graph);
  for (let i = 0; i < 3; i++) {
    c.advance(0.05);
    runner.observe(c);
  }
  runner.beforeAction(c, { skill: "palm" });
  assert.deepEqual(runner.graph, original);
  runner.beforeAction(c, { skill: "sun" });
  assert.equal(runner.graph.fork.rebasedAt, c.time);
  assert.equal(runner.graph.prefix[0].time, c.time);
});

test("same-time chi and buff changes invalidate a prepared Sun basis while an unchanged call is cached", () => {
  const c = readySun();
  const runner = new RoutineRunner(c);
  runner.beforeAction(c, { skill: "sun" });
  const fork = runner.graph.fork;
  runner.beforeAction(c, { skill: "sun" });
  assert.equal(runner.graph.fork, fork);
  c.chi = 3;
  c.setBuff("greatJade", 6);
  runner.beforeAction(c, { skill: "sun" });
  assert.notEqual(runner.graph.fork, fork);
  assert.deepEqual(
    runner.graph.fork.branches.map((b) => b.id),
    fork.branches.map((b) => b.id),
  );
  const selected = runner.graph.fork.branches.find(
    (b) => !b.outcome.mainCrit && !b.outcome.dawnTriggered,
  );
  assert.equal(selected.summary.chi, 1);
  assert.equal(selected.summary.greatJade, 6);
});

test("the next Sun has six previews before casting and keeps its new graph selected after execution", () => {
  const c = buildScenario("burst-single");
  const runner = new RoutineRunner(c);
  const oldId = runner.graph.id;
  for (
    let i = 0;
    i < 250 && !runner.archives.some((a) => a.reason === "next-sun-fork");
    i++
  ) {
    const { reference } = runner.beforeAction(c);
    if (runner.archives.some((a) => a.reason === "next-sun-fork")) break;
    if (reference.skill === "cancel") c.cancel();
    else if (reference.skill) c.cast(reference.skill);
    else c.advance(Math.min(reference.wait || 0.05, c.nextBoundary() - c.time));
    runner.observe(c);
  }
  const archived = runner.archives.find((a) => a.reason === "next-sun-fork");
  assert.ok(archived);
  assert.equal(archived.graph.id, oldId);
  assert.ok(archived.selectedBranchId);
  assert.equal(archived.graph.fork.status, "observed-selected");
  assert.equal(runner.selectedBranchId, null);
  assert.notEqual(runner.graph.id, oldId);
  assert.equal(runner.graph.fork.branches.length, 6);
  assert.equal(current(runner).skill, "sun");
  assert.equal(archived.handoff.graphId, runner.graph.id);
  assert.equal(archived.handoff.nodeId, runner.cursorNodeId);
  assert.equal(
    archived.history.some(
      (row) => row.nodeId === archived.cursorNodeId && row.actionId != null,
    ),
    false,
  );
  const newId = runner.graph.id;
  const restored = RoutineRunner.fromState(structuredClone(runner.saveState()));
  c.advance(0.1);
  c.energy = 60;
  c.chi = 3;
  runner.beforeAction(c, { skill: "sun" });
  restored.beforeAction(c, { skill: "sun" });
  c.cast("sun");
  runner.observe(c);
  restored.observe(c);
  assert.equal(runner.graph.id, newId);
  assert.ok(runner.selectedBranchId);
  assert.deepEqual(restored.saveState(), runner.saveState());
  const observed = c.events.findLast((e) => e.type === "sunResult");
  assertSunSummary(
    runner.graph.fork.branches.find((b) => b.id === runner.selectedBranchId)
      .summary,
    observed.state,
  );
});

test("timer progression exposes the next Sun fork before the player presses its key", () => {
  const c = buildScenario("burst-single");
  const runner = new RoutineRunner(c);
  let readyAtNextSun = false;
  for (let i = 0; i < 400 && c.time < 20; i++) {
    const reference = c.recommend();
    const node = current(runner);
    if (reference.skill === "sun" && runner.history.some((h) => h.branchId)) {
      runner.observe(c);
      readyAtNextSun = true;
      break;
    }
    runner.beforeAction(c, { skill: reference.skill });
    if (reference.skill === "cancel") c.cancel();
    else if (reference.skill) c.cast(reference.skill);
    else c.advance(Math.min(reference.wait || 0.05, c.nextBoundary() - c.time));
    runner.observe(c);
  }
  assert.equal(readyAtNextSun, true);
  assert.equal(current(runner).skill, "sun");
  assert.equal(runner.selectedBranchId, null);
  assert.equal(runner.graph.fork.status, "unresolved");
  assert.equal(runner.graph.fork.branches.length, 6);
  assert.ok(runner.archives.some((a) => a.reason === "next-sun-fork"));
});

test("an explicitly dequeued Sun is rebased at execution and consumes the original attempt only once", () => {
  const c = readySun({ mainCrit: true, dawnTriggered: false });
  c.gcdEnd = c.time + 0.2;
  const runner = new RoutineRunner(c);
  runner.beforeAction(c);
  const queued = c.cast("sun", { source: "keyboard", key: "1" });
  assert.equal(queued.status, "queued");
  runner.observe(c);
  const { queue, queueInput, queueAttemptId } = c;
  c.queue = null;
  c.queueInput = null;
  c.queueAttemptId = null;
  c.advance(0.2);
  c.chi = 3;
  const context = runner.beforeAction(c);
  assert.equal(context.expected.skill, "sun");
  assert.equal(runner.graph.fork.rebasedAt, c.time);
  assert.equal(runner.graph.fork.branches.length, 6);
  const executed = c.cast(queue, queueInput, queueAttemptId);
  runner.observe(c);
  runner.observe(c);
  assert.equal(executed.attemptId, queued.attemptId);
  assert.equal(
    runner.history.filter((row) => row.castId === executed.castId).length,
    1,
  );
  assertSunSummary(
    runner.graph.fork.branches.find((b) => b.id === runner.selectedBranchId)
      .summary,
    c.events.find((e) => e.type === "sunResult" && e.castId === executed.castId)
      .state,
  );
});

test("physical Sun resolving to Wind matches and retains the observed spell", () => {
  const c = readySun();
  c.setBuff("wind", 15);
  const runner = new RoutineRunner(c);
  assert.equal(runner.beforeAction(c).expected.spell, "wind");
  c.cast("sun");
  runner.observe(c);
  assert.equal(runner.history[0].status, "matched");
  assert.equal(runner.history[0].skill, "sun");
  assert.equal(runner.history[0].spell, "wind");
});

test("a different executed action retains the old graph and deviation evidence after recovery", () => {
  const c = readySun();
  const runner = new RoutineRunner(c);
  const old = structuredClone(runner.graph);
  const expectedId = runner.cursorNodeId;
  runner.beforeAction(c, { skill: "palm" });
  c.cast("palm");
  runner.observe(c);
  assert.notEqual(runner.graph.id, old.id);
  assert.equal(runner.history[0].status, "deviation");
  assert.equal(runner.history[0].graphId, old.id);
  assert.equal(runner.history[0].nodeId, expectedId);
  assert.equal(runner.history[0].expected.skill, "sun");
  assert.deepEqual(runner.archives[0].graph, old);
  runner.beforeAction(c);
  runner.observe(c);
  assert.equal(runner.history[0].status, "deviation");
});

test("a live reference change explicitly adapts only the unfinished tail and saves its old prediction", () => {
  const c = readySun();
  const runner = new RoutineRunner(c);
  const old = structuredClone(runner.graph);
  c.cooldowns.fists = 0;
  const context = runner.beforeAction(c);
  assert.equal(context.reference.skill, "fists");
  assert.equal(context.expected.skill, "fists");
  assert.equal(runner.history.at(-1).status, "adapted");
  assert.deepEqual(runner.archives[0].graph, old);
  const entries = runner.history.length;
  runner.beforeAction(c);
  assert.equal(runner.history.length, entries);
  c.cast("fists");
  runner.observe(c);
  assert.equal(runner.history.at(-1).status, "matched");
});

test("adaptation after selecting a branch preserves its original prefix and outcome highlighting", () => {
  const c = readySun({ mainCrit: false, dawnTriggered: false });
  const runner = new RoutineRunner(c);
  c.cast("sun");
  runner.observe(c);
  const id = runner.graph.id;
  const prefix = structuredClone(runner.graph.prefix);
  const branchId = runner.selectedBranchId;
  c.advance(1);
  c.cooldowns.fists = 0;
  c.chi = 6;
  const context = runner.beforeAction(c);
  assert.equal(context.expected.skill, "fists");
  assert.equal(runner.graph.id, id);
  assert.equal(runner.selectedBranchId, branchId);
  assert.deepEqual(runner.graph.prefix, prefix);
  assert.ok(runner.archives.some((a) => a.status === "adapted"));
});

test("an adapted selected tail also stops before sampling a new Blackout proc", () => {
  const c = readySun({ mainCrit: false, dawnTriggered: false });
  const runner = new RoutineRunner(c);
  c.cast("sun");
  runner.observe(c);
  c.advance(1);
  c.combo = 2;
  c.setBuff("combo", 15);
  const context = runner.beforeAction(c);
  assert.equal(context.reference.skill, "blackout");
  const tail = runner.graph.fork.branches
    .find((b) => b.id === runner.selectedBranchId)
    .nodes.slice(runner.index);
  assert.equal(tail.length, 1);
  assert.equal(tail[0].skill, "blackout");
  assert.equal(tail[0].unresolved, true);
});

test("runner and Combat restore atomically with queues, branch selection and consumption cursor", () => {
  const c = readySun({ mainCrit: true, dawnTriggered: true, dawnCrit: true });
  const runner = new RoutineRunner(c, { id: "checkpoint" });
  runner.beforeAction(c);
  c.cast("sun");
  runner.observe(c);
  c.advance(0.8);
  const next = runner.graph.fork.branches
    .find((b) => b.id === runner.selectedBranchId)
    .nodes.find((n) => n.kind !== "wait");
  assert.equal(c.cast(next.skill).status, "queued");
  const combatState = c.saveState();
  const runnerState = structuredClone(runner.saveState());
  const restoredCombat = Combat.fromState(combatState);
  const restored = RoutineRunner.fromState(runnerState);
  assert.deepEqual(restored.saveState(), runnerState);
  c.advance(0.2);
  restoredCombat.advance(0.2);
  runner.observe(c);
  restored.observe(restoredCombat);
  assert.deepEqual(restored.saveState(), runner.saveState());
  assert.deepEqual(restoredCombat.saveState(), c.saveState());
  restored.history[0].reason = "changed";
  assert.notEqual(restored.history[0].reason, runner.history[0].reason);
});

test("ordinary timer ticks keep graph/node identity while protected FoF remains active", () => {
  const c = new Combat({ initialChi: 6, inputMode: "protected" });
  c.cast("fists");
  const runner = new RoutineRunner(c);
  const graph = structuredClone(runner.graph);
  const cursor = runner.cursorNodeId;
  c.advance(0.1);
  runner.observe(c);
  runner.beforeAction(c);
  assert.deepEqual(runner.graph, graph);
  assert.equal(runner.cursorNodeId, cursor);
  assert.deepEqual(runner.history, []);
});

test("an empty route resumes once a legal reference returns without rebuilding on blocked ticks", () => {
  const c = readySun();
  c.attackable = false;
  const initial = new RoutineRunner(c);
  const state = initial.saveState();
  state.graph.prefix = [];
  state.graph.fork = null;
  state.index = 0;
  state.cursorNodeId = null;
  const runner = RoutineRunner.fromState(state);
  const stalled = runner.graph;
  for (let i = 0; i < 3; i++) {
    c.advance(0.05);
    runner.observe(c);
    assert.equal(runner.graph, stalled);
  }
  c.attackable = true;
  c.gcdEnd = c.time + 0.2;
  runner.observe(c);
  assert.equal(runner.graph, stalled);
  c.advance(0.2);
  runner.observe(c);
  assert.notEqual(runner.graph.id, stalled.id);
  assert.equal(current(runner).skill, c.recommend().skill);
  assert.equal(runner.archives.length, 1);
  assert.equal(runner.archives[0].reason, "reference-available");
  const resumed = runner.graph;
  runner.observe(c);
  assert.equal(runner.graph, resumed);
  const context = runner.beforeAction(c);
  c.cast(context.reference.skill);
  runner.observe(c);
  assert.ok(runner.history.every((row) => row.status === "matched"));
});

test("a no-target wait resumes immediately when a target unexpectedly returns before its horizon", () => {
  const c = readySun();
  c.attackable = false;
  const runner = new RoutineRunner(c);
  const waiting = runner.graph;
  assert.equal(current(runner).reference.blocker, "no-target");
  c.advance(0.1);
  runner.observe(c);
  assert.equal(runner.graph, waiting);
  c.attackable = true;
  runner.observe(c);
  assert.notEqual(runner.graph.id, waiting.id);
  assert.equal(current(runner).skill, c.recommend().skill);
  assert.equal(runner.archives[0].reason, "target-return");
  const graph = runner.graph;
  c.advance(0.05);
  runner.observe(c);
  assert.equal(runner.graph, graph);
  assert.equal(runner.history.length, 0);
});

test("public dungeon waves resume from an empty no-target route at the actual 30-second return", () => {
  const c = buildScenario("dungeon-waves");
  c.advance(25);
  assert.equal(c.attackable, false);
  const state = new RoutineRunner(c).saveState();
  state.graph.prefix = [];
  state.graph.fork = null;
  state.index = 0;
  state.cursorNodeId = null;
  const runner = RoutineRunner.fromState(state);
  const empty = runner.graph;
  c.advance(4.9);
  runner.observe(c);
  assert.equal(runner.graph, empty);
  c.advance(0.1);
  runner.observe(c);
  assert.equal(c.time, 30);
  assert.equal(c.attackable, true);
  assert.equal(c.options.targets, 5);
  assert.notEqual(runner.graph.id, empty.id);
  assert.equal(current(runner).skill, c.recommend().skill);
  assert.equal(runner.history.length, 0);
  assert.equal(runner.archives.length, 1);
});

test("an empty ended session remains stable on repeated timer observations", () => {
  const c = new Combat({ duration: 1 });
  c.advance(1);
  const runner = new RoutineRunner(c);
  const graph = runner.graph;
  for (let i = 0; i < 3; i++) runner.observe(c);
  assert.equal(runner.graph, graph);
  assert.equal(runner.generation, 1);
  assert.equal(runner.archives.length, 0);
});

test("a delayed matching input anchors its following wait to the actual execution without rewriting the route", () => {
  const c = new Combat();
  const runner = new RoutineRunner(c);
  const graphId = runner.graph.id;
  const nodes = structuredClone(runner.graph.prefix);
  c.advance(0.4);
  runner.beforeAction(c);
  c.cast("palm");
  runner.observe(c);
  c.advance(0.7);
  runner.observe(c);
  assert.equal(current(runner).kind, "wait");
  const context = runner.beforeAction(c);
  assert.equal(context.expected.kind, "wait");
  assert.equal(runner.graph.id, graphId);
  assert.deepEqual(runner.graph.prefix, nodes);
  assert.ok(runner.history.every((row) => row.status === "matched"));
});

test("a branch ending in FoF keeps its observed selection until the last channel pulse", () => {
  const c = readySun({ mainCrit: true, dawnTriggered: true, dawnCrit: true });
  c.cooldowns.fists = 6;
  const runner = new RoutineRunner(c, { maxActions: 1 });
  const graphId = runner.graph.id;
  c.cast("sun");
  runner.observe(c);
  const branchId = runner.selectedBranchId;
  c.advance(1);
  runner.beforeAction(c);
  assert.equal(c.cast("fists").status, "executed");
  runner.observe(c);
  assert.equal(runner.graph.id, graphId);
  assert.equal(runner.selectedBranchId, branchId);
  const end = c.channel.end;
  c.advance(end - c.time - 0.01);
  runner.observe(c);
  assert.equal(runner.graph.id, graphId);
  c.advance(0.01);
  runner.observe(c);
  assert.notEqual(runner.graph.id, graphId);
});

test("real Combat reference practice preserves executed action identity through the opener", () => {
  const c = buildScenario("burst-single");
  const runner = new RoutineRunner(c);
  for (let i = 0; i < 180 && c.time < 12; i++) {
    const { reference } = runner.beforeAction(c);
    if (reference.skill === "cancel") c.cancel();
    else if (reference.skill)
      assert.equal(c.cast(reference.skill).status, "executed");
    else
      c.advance(
        Math.min(
          reference.wait || 0.05,
          c.nextBoundary() - c.time,
          12 - c.time,
        ),
      );
    runner.observe(c);
  }
  assert.ok(c.time > 8);
  assert.equal(c.clippedFists, 0);
  const records = runner.history.filter((row) => row.actionId != null);
  assert.equal(records.length, c.casts.length + c.controls.length);
  assert.equal(
    new Set(records.map((row) => row.actionId)).size,
    records.length,
  );
  assert.ok(records.every((row) => row.status === "matched"));
  assert.ok(runner.history.some((row) => row.branchId));
});
