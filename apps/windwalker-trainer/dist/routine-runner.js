import {
  buildRoutineGraph,
  rebaseRoutineGraphAtSun,
  routineReference,
  routineStateSummary,
} from "./routine-graph.js";

const EPS = 1e-7;
const copy = (value) => structuredClone(value);

function sunBasisKey(combat) {
  const state = combat.saveState({ history: false });
  // Cache physical state, never the hidden stream or its seed.
  delete state.randomState;
  delete state.options.seed;
  state.windows = copy(combat.windows);
  return JSON.stringify(state);
}

/** Owns only serializable teaching state. Combat belongs to the calling session. */
export class RoutineRunner {
  constructor(combat, { id = "route-1", maxActions = 8, horizon = 14 } = {}) {
    this.rootId = id;
    this.options = { maxActions, horizon };
    this.generation = 1;
    this.adaptationSerial = 0;
    this.graph = buildRoutineGraph(combat, { id, ...this.options });
    this.selectedBranchId = null;
    this.history = [];
    this.archives = [];
    this.segment = "prefix";
    this.index = 0;
    this.timeOffset = 0;
    this.lastActionId = Math.max(
      combat.actionSerial ?? 0,
      ...[...combat.casts, ...combat.controls].map((a) => a.actionId ?? 0),
    );
    this.pendingForkCastId = null;
    this.sunRebaseKey = null;
    this.prepared = null;
    this.syncCursor();
  }

  nodes() {
    return this.segment === "prefix"
      ? this.graph.prefix
      : (this.graph.fork?.branches.find((b) => b.id === this.selectedBranchId)
          ?.nodes ?? []);
  }

  syncCursor() {
    this.cursorNodeId = this.nodes()[this.index]?.id ?? null;
  }

  skipWaits(time) {
    let node = this.nodes()[this.index];
    while (
      node?.kind === "wait" &&
      time >= node.time + node.duration + this.timeOffset - EPS
    ) {
      this.index++;
      node = this.nodes()[this.index];
    }
    this.syncCursor();
  }

  archive(status, combat, reason) {
    this.archives.push(
      copy({
        graphId: this.graph.id,
        graph: this.graph,
        status,
        reason,
        time: combat.time,
        cursorNodeId: this.cursorNodeId,
        selectedBranchId: this.selectedBranchId,
        history: this.history.filter((row) => row.graphId === this.graph.id),
      }),
    );
  }

  startNext(combat) {
    this.generation++;
    this.graph = buildRoutineGraph(combat, {
      id: `${this.rootId}:${this.generation}`,
      ...this.options,
    });
    this.segment = "prefix";
    this.index = 0;
    this.timeOffset = 0;
    this.selectedBranchId = null;
    this.pendingForkCastId = null;
    this.sunRebaseKey = null;
    this.prepared = null;
    this.syncCursor();
  }

  finishIfNeeded(combat) {
    if (this.pendingForkCastId != null) return;
    const empty = !this.graph.prefix.length;
    const node = this.nodes()[this.index];
    const awaitingTarget =
      node?.kind === "wait" && node.reference?.blocker === "no-target";
    if ((empty || awaitingTarget) && routineReference(combat).skill) {
      this.archive(
        "completed",
        combat,
        empty ? "reference-available" : "target-return",
      );
      this.startNext(combat);
      return;
    }
    if (this.cursorNodeId) return;
    if (empty) return;
    this.archive("completed", combat, "segment-complete");
    this.startNext(combat);
  }

  handoffSun(combat, reference = routineReference(combat), skill) {
    if (skill != null && skill !== "sun") return;
    const node = this.nodes()[this.index];
    if (
      this.segment !== "branch" ||
      node?.skill !== "sun" ||
      !node.unresolved ||
      reference.skill !== "sun"
    )
      return;
    const parent = {
      graphId: this.graph.id,
      branchId: this.selectedBranchId,
      nodeId: node.id,
    };
    this.archive("completed", combat, "next-sun-fork");
    const archived = this.archives.at(-1);
    this.startNext(combat);
    this.graph.parent = parent;
    // The old terminal Sun is a handoff marker, not an executed action.
    archived.handoff = {
      graphId: this.graph.id,
      nodeId: this.cursorNodeId,
      executed: false,
    };
  }

  selectObservedBranch(combat) {
    if (this.pendingForkCastId == null) return;
    const result = combat.events.find(
      (e) => e.type === "sunResult" && e.castId === this.pendingForkCastId,
    );
    if (!result) return;
    const branch = this.graph.fork.branches.find(
      (b) =>
        b.outcome.mainCrit === result.mainCrit &&
        b.outcome.dawnTriggered === result.dawnTriggered &&
        (!result.dawnTriggered || b.outcome.dawnCrit === result.dawnCrit),
    );
    if (!branch) return;
    this.selectedBranchId = branch.id;
    this.graph.fork.status = "observed-selected";
    this.graph.fork.selectedBranchId = branch.id;
    this.graph.fork.observed = copy(result);
    branch.predictedSummary = copy(branch.summary);
    branch.summary = routineStateSummary(result.state);
    branch.summarySource = "observed";
    for (const b of this.graph.fork.branches)
      b.status =
        b.id === branch.id ? "observed-selected" : "observed-not-selected";
    const row = this.history.findLast(
      (h) => h.graphId === this.graph.id && h.castId === this.pendingForkCastId,
    );
    if (row) row.branchId = branch.id;
    this.pendingForkCastId = null;
    this.sunRebaseKey = null;
    this.segment = "branch";
    this.index = 0;
    this.syncCursor();
  }

  adapt(combat, reference) {
    const old = this.nodes()[this.index] ?? null;
    this.archive("adapted", combat, "observed-reference-changed");
    this.history.push({
      actionId: null,
      castId: null,
      nodeId: old?.id ?? null,
      graphId: this.graph.id,
      status: "adapted",
      reason: "observed-reference-changed",
      time: combat.time,
      branchId: this.selectedBranchId,
      expected: copy(old),
      reference: copy(reference),
    });
    const fresh = buildRoutineGraph(combat, {
      id: `${this.graph.id}:adapt-${++this.adaptationSerial}`,
      ...this.options,
    });
    this.sunRebaseKey = null;
    this.timeOffset = 0;
    if (this.segment === "branch") {
      const branch = this.graph.fork.branches.find(
        (b) => b.id === this.selectedBranchId,
      );
      const boundary = fresh.prefix.findIndex(
        (n) => n.skill === "sun" || n.skill === "blackout",
      );
      const tail =
        boundary >= 0 ? fresh.prefix.slice(0, boundary + 1) : fresh.prefix;
      if (boundary >= 0) tail.at(-1).unresolved = true;
      branch.nodes = [...branch.nodes.slice(0, this.index), ...tail];
      branch.stopReason =
        boundary >= 0
          ? tail.at(-1).skill === "sun"
            ? "next-sun"
            : "blackout-proc"
          : fresh.stopReason;
    } else {
      this.graph.prefix = [
        ...this.graph.prefix.slice(0, this.index),
        ...fresh.prefix,
      ];
      this.graph.fork = fresh.fork;
    }
    for (const phase of fresh.phases) {
      const target = this.graph.phases.find((p) => p.id === phase.id);
      for (const window of phase.windows)
        if (!target.windows.some((w) => w.id === window.id))
          target.windows.push(window);
    }
    this.syncCursor();
  }

  beforeAction(combat, { skill } = {}) {
    this.observe(combat);
    const reference = routineReference(combat);
    const expected = this.nodes()[this.index] ?? null;
    const different =
      expected &&
      (reference.skill
        ? expected.kind === "wait" ||
          expected.skill !== reference.skill ||
          expected.spell !== reference.spell
        : expected.kind !== "wait");
    if (different && this.pendingForkCastId == null)
      this.adapt(combat, reference);
    this.handoffSun(combat, reference, skill);
    const node = this.nodes()[this.index];
    if (
      (skill === undefined || skill === "sun") &&
      reference.skill === "sun" &&
      node?.skill === "sun" &&
      this.segment === "prefix" &&
      this.graph.fork?.status === "unresolved"
    ) {
      const key = sunBasisKey(combat);
      if (key !== this.sunRebaseKey) {
        this.graph = rebaseRoutineGraphAtSun(combat, this.graph);
        this.sunRebaseKey = key;
        this.timeOffset = 0;
        this.syncCursor();
      }
    }
    this.prepared = copy({
      graphId: this.graph.id,
      nodeId: this.cursorNodeId,
      expected: this.nodes()[this.index] ?? null,
      reference,
    });
    return copy(this.prepared);
  }

  /** Returns newly recorded observations; queued/rejected attempts are not actions. */
  observe(combat) {
    const historyStart = this.history.length;
    const actions = [...combat.casts, ...combat.controls]
      .filter((a) => a.actionId > this.lastActionId)
      .sort((a, b) => a.actionId - b.actionId);
    let deviated = false;
    this.selectObservedBranch(combat);
    for (const action of actions) {
      this.skipWaits(action.time);
      const node = this.nodes()[this.index] ?? null;
      const matched =
        !deviated &&
        node &&
        node.kind !== "wait" &&
        node.skill === action.skill &&
        node.spell === (action.spell ?? action.skill);
      const record = {
        actionId: action.actionId,
        castId: action.castId ?? null,
        nodeId: node?.id ?? null,
        graphId: this.graph.id,
        status: matched ? "matched" : "deviation",
        reason: matched
          ? "expected-action-executed"
          : deviated
            ? "action-after-deviation"
            : "different-action-executed",
        time: action.time,
        skill: action.skill,
        spell: action.spell ?? action.skill,
        expected: copy(node),
        reference: copy(this.prepared?.reference ?? null),
        ...(this.selectedBranchId ? { branchId: this.selectedBranchId } : {}),
      };
      this.history.push(record);
      this.lastActionId = action.actionId;
      this.prepared = null;
      if (!matched) {
        deviated = true;
        continue;
      }
      this.index++;
      this.timeOffset = action.time - node.time;
      this.syncCursor();
      if (node.id === this.graph.fork?.triggerNodeId) {
        this.pendingForkCastId = action.castId;
        this.selectObservedBranch(combat);
      }
    }
    if (deviated) {
      this.archive("deviation", combat, "different-action-executed");
      this.startNext(combat);
    } else {
      this.skipWaits(combat.time);
      this.finishIfNeeded(combat);
      // Once the selected segment reaches another executable Sun, reveal its
      // next fork before input. Do not replace a just-observed Sun selection.
      if (!actions.length) {
        const reference = routineReference(combat);
        const node = this.nodes()[this.index];
        if (
          reference.skill === "sun" &&
          node &&
          node.skill !== "sun" &&
          this.pendingForkCastId == null
        ) {
          this.adapt(combat, reference);
        }
        this.handoffSun(combat, reference);
      }
    }
    return copy(this.history.slice(historyStart));
  }

  saveState() {
    return copy({
      version: 1,
      rootId: this.rootId,
      options: this.options,
      generation: this.generation,
      adaptationSerial: this.adaptationSerial,
      graph: this.graph,
      selectedBranchId: this.selectedBranchId,
      cursorNodeId: this.cursorNodeId,
      history: this.history,
      archives: this.archives,
      segment: this.segment,
      index: this.index,
      timeOffset: this.timeOffset,
      lastActionId: this.lastActionId,
      pendingForkCastId: this.pendingForkCastId,
      sunRebaseKey: this.sunRebaseKey,
      prepared: this.prepared,
    });
  }

  static fromState(state) {
    if (state?.version !== 1)
      throw new TypeError("Unsupported routine runner state");
    const { version, ...data } = copy(state);
    const runner = Object.assign(
      Object.create(RoutineRunner.prototype),
      { sunRebaseKey: null },
      data,
    );
    runner.syncCursor();
    return runner;
  }
}
