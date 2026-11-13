import test from "node:test";
import assert from "node:assert/strict";
import { TrainingSession } from "../dist/session.js";

test("natural five-target proc changes expose every next Sun fork before input", () => {
  const s = new TrainingSession({
    scenario: "burst-aoe",
    options: {
      targets: 5,
      bloodlust: true,
      seed: 1026,
      inputMode: "protected",
      protectCrane: true,
    },
  });
  s.start();
  let suns = 0;
  for (let i = 0; i < 4000 && !s.finished; i++) {
    const d = s.combat.recommend();
    if (d.skill === "sun") {
      const graph = s.routine.graph;
      const nodes =
        s.routine.segment === "prefix"
          ? graph.prefix
          : graph.fork.branches.find((b) => b.id === s.routine.selectedBranchId)
              .nodes;
      assert.equal(
        nodes.find((n) => n.id === s.routine.cursorNodeId)?.skill,
        "sun",
        `stale cursor at ${s.combat.time}`,
      );
      assert.equal(
        s.routine.selectedBranchId,
        null,
        `previous selection still shown at ${s.combat.time}`,
      );
      assert.equal(graph.fork.status, "unresolved");
      suns++;
    }
    if (d.skill === "cancel") s.cancel();
    else if (d.skill) {
      const slot =
        d.skill === "conduit"
          ? "tiger"
          : d.skill === "stomp"
            ? "zenith"
            : d.skill;
      assert.equal(s.act(slot).ok, true);
    } else
      s.tick(
        Math.min(0.1, d.wait || 0.05, s.combat.nextBoundary() - s.combat.time),
      );
  }
  assert.ok(suns >= 5);
  assert.equal(s.finished, true);
});

const session = (options = {}) =>
  new TrainingSession({
    scenario: "burst-single",
    options: {
      bloodlust: false,
      inputMode: "protected",
      protectCrane: true,
      ...options,
    },
  });

test("a session owns both physical state and a stable prepared routine", () => {
  const s = session();
  assert.equal(s.running, false);
  assert.ok(s.routine.graph.id);
  const graph = structuredClone(s.routine.graph);
  s.tick(0.5);
  assert.equal(s.combat.time, 0);
  assert.deepEqual(s.routine.graph, graph);
});

test("rejected inputs never complete a route node or create retry checkpoints", () => {
  const s = session();
  s.start();
  const count = s.checkpoints.length;
  const cursor = s.routine.cursorNodeId;
  assert.equal(s.act("dragon").ok, false);
  assert.equal(s.checkpoints.length, count);
  assert.equal(s.routine.cursorNodeId, cursor);
  assert.equal(s.inputRecords.at(-1).status, "rejected");
});

test("a queued input advances only on execution and preserves its original identity", () => {
  const s = session();
  s.start();
  s.act("palm", { key: "2" });
  s.tick(0.8);
  const history = s.routine.history.length;
  const result = s.act("fists", { key: "F" });
  assert.equal(result.queued, true);
  assert.equal(s.routine.history.length, history);
  s.tick(0.2);
  assert.equal(s.combat.casts.at(-1).skill, "fists");
  assert.equal(s.inputRecords.at(-1).attemptId, result.attemptId);
  assert.equal(s.inputRecords.at(-1).status, "executed");
  assert.equal(s.routine.history.length, history + 1);
  s.tick(0.05);
  assert.equal(s.routine.history.length, history + 1);
});

test("retry atomically restores the route, active channel and input prefix", () => {
  const s = session();
  s.start();
  s.act("palm");
  s.tick(1);
  s.act("fists");
  s.tick(0.4);
  const physical = s.combat.saveState();
  const teaching = s.routine.saveState();
  s.cancel({ source: "keyboard", key: "X" });
  const checkpoint = s.checkpoints.at(-1);
  assert.equal(s.combat.clippedFists, 1);
  s.retry(checkpoint.id);
  assert.deepEqual(s.combat.saveState(), physical);
  assert.deepEqual(s.routine.saveState(), teaching);
  assert.equal(s.paused, true);
  assert.equal(
    s.inputRecords.some((r) => r.skill === "cancel"),
    false,
  );
});

test("same-timestamp control retry restores the second channel and prior controls", () => {
  const s = session();
  s.start();
  s.act("palm");
  s.tick(1);
  s.act("crane");
  s.tick(1);
  s.cancel();
  s.act("fists");
  s.cancel();
  const id = s.checkpoints.at(-1).id;
  s.retry(id);
  assert.equal(s.combat.channel.skill, "fists");
  assert.deepEqual(
    s.inputRecords.map((r) => r.skill),
    ["palm", "crane", "cancel", "fists"],
  );
  assert.deepEqual(
    s.combat.controls.map((c) => c.before.channel.skill),
    ["crane"],
  );
});

test("pause prevents elapsed time and the reference demonstration uses the same routine observer", () => {
  const s = session();
  s.start({ demo: true });
  s.tick(3);
  assert.ok(s.combat.casts.length >= 3);
  assert.ok(s.routine.history.length >= 3);
  s.setPaused(true);
  const state = s.combat.saveState();
  s.tick(1);
  assert.deepEqual(s.combat.saveState(), state);
  assert.equal(s.act("palm").ok, false);
});

test("all six observed sun outcomes choose their declared graph edge", () => {
  for (const mainCrit of [false, true])
    for (const dawn of ["absent", "normal", "critical"]) {
      const outcome = {
        mainCrit,
        dawnTriggered: dawn !== "absent",
        dawnCrit: dawn === "critical",
      };
      const s = new TrainingSession({
        scenario: "crit-branch",
        options: {
          inputMode: "protected",
          protectCrane: true,
          sunOutcomes: [outcome],
        },
      });
      s.start();
      const graphId = s.routine.graph.id;
      const result = s.act("sun", { key: "1" });
      assert.equal(result.ok, true);
      assert.equal(s.routine.graph.id, graphId);
      assert.ok(s.routine.selectedBranchId);
      const branch = s.routine.graph.fork.branches.find(
        (b) => b.id === s.routine.selectedBranchId,
      );
      assert.equal(branch.outcome.mainCrit, mainCrit);
      assert.equal(branch.outcome.dawnTriggered, dawn !== "absent");
      if (dawn !== "absent")
        assert.equal(branch.outcome.dawnCrit, dawn === "critical");
    }
});

test("new sessions and retry change the async generation identity", () => {
  const s = session();
  const initial = s.generation;
  s.start();
  assert.ok(s.generation > initial);
  const beforeRetry = s.generation;
  s.retry(s.checkpoints[0].id);
  assert.ok(s.generation > beforeRetry);
});

test("schema four exports preserve route evidence and the restorable teaching state", () => {
  const s = session();
  s.start();
  s.act("palm");
  const data = s.export();
  assert.equal(data.schema, 4);
  assert.deepEqual(data.state, s.combat.saveState());
  assert.deepEqual(data.routine, s.routine.saveState());
  assert.ok(data.routeReview.length > 0);
  assert.equal(
    data.inputRecords[0].checkpointId,
    s.combat.casts[0].input.checkpointId,
  );
  structuredClone(data);
});

test("late asynchronous results cannot rewrite a new or restored teaching state", () => {
  const s = session();
  const messages = [];
  const errors = [];
  const worker = {
    postMessage(message) {
      messages.push(message);
    },
  };
  s.connectPlanner(
    worker,
    () => ({ mode: "search" }),
    (error) => {
      if (error) errors.push(error);
    },
  );
  const first = messages[0];
  s.start();
  const graph = s.routine.saveState();
  worker.onmessage({
    data: { revision: first.revision, decision: { skill: "dragon" } },
  });
  assert.equal(s.plan, undefined);
  assert.deepEqual(s.routine.saveState(), graph);
  const second = messages.at(-1);
  worker.onmessage({
    data: { revision: second.revision, decision: { skill: "palm" } },
  });
  assert.equal(s.plan.decision.skill, "palm");
  s.retry(s.checkpoints[0].id);
  const restored = s.routine.saveState();
  worker.onmessage({
    data: { revision: second.revision, error: "stale error" },
  });
  assert.equal(s.workerFailed, false);
  assert.deepEqual(errors, []);
  assert.equal(s.planEpoch, -1);
  assert.deepEqual(s.routine.saveState(), restored);
});

test("a later accepted queue replaces pending input without advancing the route twice", () => {
  const s = session();
  s.start();
  s.act("palm");
  s.tick(0.8);
  s.act("fists");
  s.act("tiger");
  assert.equal(s.inputRecords.at(-2).status, "replaced");
  s.tick(0.2);
  assert.equal(s.combat.casts.at(-1).skill, "tiger");
  assert.equal(s.inputRecords.at(-1).status, "executed");
  assert.equal(s.routine.history.filter((h) => h.actionId != null).length, 2);
});

test("retry restores a queued input record before its undone replacement and reconciles execution", () => {
  const s = session();
  s.start();
  s.act("palm");
  s.tick(0.8);
  const original = s.act("fists");
  const replacement = s.act("tiger");
  assert.equal(s.inputRecords.at(-2).status, "replaced");
  s.retry(replacement.checkpointId);
  assert.equal(s.combat.queue, "fists");
  assert.equal(s.inputRecords.at(-1).status, "queued");
  s.setPaused(false);
  s.tick(0.2);
  const record = s.inputRecords.at(-1);
  assert.equal(record.status, "executed");
  assert.equal(record.attemptId, original.attemptId);
  assert.equal(record.castId, s.combat.casts.at(-1).castId);
});
