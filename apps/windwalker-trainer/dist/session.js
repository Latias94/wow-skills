import { buildScenario } from "./scenarios.js";
import { Combat } from "./combat.js";
import { ACTION_SLOTS, slotAction } from "./actionbar.js";
import { referenceDecision } from "./policy.js";
import { RoutineRunner } from "./routine-runner.js";

const EPS = 1e-7;

export class TrainingSession {
  constructor({ scenario = "burst-single", options = {} } = {}) {
    this.generation = 0;
    this.prepare(scenario, options);
  }

  prepare(scenario = this.scenario, options = this.options) {
    this.scenario = scenario;
    this.options = structuredClone(options);
    this.combat = buildScenario(scenario, options);
    this.routine = new RoutineRunner(this.combat);
    this.running = false;
    this.paused = false;
    this.finished = false;
    this.demonstration = false;
    this.roundStart = this.combat.time;
    this.origin = { scenario, preparedAt: this.combat.time };
    this.checkpoints = [];
    this.checkpointSerial = 0;
    this.inputRecords = [];
    this.generation++;
    this.invalidatePlan();
    this.remember("开始节点");
  }

  start({
    demo = false,
    scenario = this.scenario,
    options = this.options,
  } = {}) {
    this.prepare(scenario, options);
    this.running = true;
    this.demonstration = demo;
  }

  setPaused(value) {
    if (this.running) this.paused = Boolean(value);
  }

  finish() {
    this.running = false;
    this.paused = false;
    this.finished = true;
  }

  remember(label) {
    const checkpoint = {
      id: ++this.checkpointSerial,
      label,
      time: this.combat.time,
      state: this.combat.saveState(),
      routine: this.routine.saveState(),
      inputRecords: structuredClone(this.inputRecords),
    };
    this.checkpoints.push(checkpoint);
    if (this.checkpoints.length > 100) this.checkpoints.shift();
    return checkpoint;
  }

  retry(id) {
    const checkpoint = this.checkpoints.find((c) => c.id === id);
    if (!checkpoint) return null;
    this.combat = Combat.fromState(checkpoint.state);
    this.routine = RoutineRunner.fromState(checkpoint.routine);
    this.inputRecords = structuredClone(checkpoint.inputRecords);
    this.checkpoints = this.checkpoints.filter((c) => c.id <= checkpoint.id);
    this.running = true;
    this.paused = true;
    this.finished = false;
    this.demonstration = false;
    this.origin = {
      ...this.origin,
      retriedFrom: { id, time: checkpoint.time, label: checkpoint.label },
    };
    this.generation++;
    this.invalidatePlan();
    return checkpoint;
  }

  act(slot, input = {}) {
    if (!this.running || this.paused || this.demonstration)
      return {
        ok: false,
        reason: this.paused
          ? "已暂停，按空格继续。"
          : this.demonstration
            ? "当前是参考演示。"
            : "请先开始练习。",
      };
    if (!ACTION_SLOTS[slot]) return { ok: false, reason: "没有这个技能槽位。" };
    return this.execute(
      slotAction(this.combat, slot),
      { ...input, slot },
      slot,
    );
  }

  execute(skill, input, slot = null) {
    const before = this.combat.snapshot();
    const expected = referenceDecision(this.combat);
    // Keep the checkpoint before both the teaching transition and physical input.
    const checkpoint = this.remember(skill === "cancel" ? "主动断条" : skill);
    const accepted = { ...input, checkpointId: checkpoint.id };
    const annotation = this.routine.beforeAction(this.combat, { skill });
    const result =
      skill === "cancel"
        ? { ok: this.combat.cancel(accepted), status: "executed" }
        : this.combat.cast(skill, accepted);
    if (!result.ok) {
      this.checkpoints = this.checkpoints.filter((c) => c.id !== checkpoint.id);
      this.routine = RoutineRunner.fromState(checkpoint.routine);
    }
    const cast = result.castId
      ? this.combat.casts.find((c) => c.castId === result.castId)
      : null;
    if (result.queued)
      for (const record of this.inputRecords) {
        if (record.status === "queued") {
          record.status = "replaced";
          record.reason = "被后一次合法队列输入替换";
        }
      }
    this.inputRecords.push({
      time: before.time,
      slot,
      skill,
      spell: cast?.spell || (skill === "sun" && before.wind ? "wind" : skill),
      input: accepted,
      status: result.status || (result.ok ? "executed" : "rejected"),
      reason: result.reason,
      attemptId: result.attemptId,
      castId: result.castId,
      expected,
      checkpointId: result.ok ? checkpoint.id : null,
      graphId: annotation?.graphId,
      nodeId: annotation?.nodeId,
    });
    if (this.inputRecords.length > 2000) this.inputRecords.shift();
    this.routine.observe(this.combat);
    this.invalidatePlan();
    return { ...result, checkpointId: result.ok ? checkpoint.id : null };
  }

  cancel(input = {}) {
    if (!this.running || this.paused || this.demonstration) return false;
    if (!this.combat.channel) return false;
    return this.execute("cancel", { source: "explicit", key: "X", ...input })
      .ok;
  }

  observe() {
    for (const record of this.inputRecords) {
      if (record.status !== "queued") continue;
      const executed = this.combat.attempts.find(
        (a) => a.attemptId === record.attemptId && a.status === "executed",
      );
      const rejected = this.combat.attempts.findLast(
        (a) => a.attemptId === record.attemptId && a.status === "rejected",
      );
      if (executed) {
        record.status = "executed";
        record.castId = executed.castId;
        record.spell = executed.spell;
      } else if (rejected) {
        record.status = "rejected";
        record.reason = rejected.reason;
      }
    }
    this.routine.observe(this.combat);
    for (const record of this.inputRecords) {
      if (!record.castId) continue;
      const entry = this.routine.history.find(
        (h) => h.castId === record.castId && h.actionId != null,
      );
      if (entry) {
        record.nodeId = entry.nodeId;
        record.graphId = entry.graphId;
      }
    }
  }

  tick(seconds) {
    if (!this.running || this.paused) return;
    const end = Math.min(
      this.combat.options.duration,
      this.combat.time + Math.max(0, seconds),
    );
    const signature = `${this.combat.actionSerial}:${this.combat.events.length}:${this.combat.options.targets}:${this.combat.attackable}`;
    let iterations = 0;
    while (this.combat.time < end - EPS) {
      if (++iterations > 30000)
        throw new Error("Session exceeded its reference scheduling budget");
      const c = this.combat;
      if (this.demonstration) {
        const d = referenceDecision(c);
        if (d.skill) {
          this.execute(d.skill, { source: "reference", decision: d });
          continue;
        }
      }
      const boundary = c.nextBoundary() - c.time;
      const elapsed = Math.min(end - c.time, boundary > EPS ? boundary : 0.001);
      // The session observes the exact execution state before the accepted queue
      // fires. Queue validation and the original attempt identity stay in Combat.
      const queued =
        c.queue && c.gcdEnd <= c.time + elapsed + EPS
          ? { skill: c.queue, input: c.queueInput, attemptId: c.queueAttemptId }
          : null;
      if (queued) {
        c.queue = null;
        c.queueInput = null;
        c.queueAttemptId = null;
      }
      c.advance(elapsed);
      if (queued) {
        this.routine.observe(c);
        this.routine.beforeAction(c, { skill: queued.skill });
        c.cast(queued.skill, queued.input, queued.attemptId);
      }
      this.observe();
    }
    if (this.combat.time >= this.combat.options.duration - EPS) this.finish();
    const after = `${this.combat.actionSerial}:${this.combat.events.length}:${this.combat.options.targets}:${this.combat.attackable}`;
    if (signature !== after) this.invalidatePlan();
    else this.requestPlan();
  }

  connectPlanner(worker, settings, onChange = () => {}) {
    this.worker = worker;
    this.plannerSettings = settings;
    this.onPlannerChange = onChange;
    this.workerFailed = false;
    this.workerBusy = false;
    worker.onmessage = ({ data }) => {
      this.workerBusy = false;
      const pending = this.pendingRequest;
      const accepted =
        data.revision === pending?.revision &&
        pending.generation === this.generation &&
        pending.epoch === this.epoch &&
        this.combat.time - pending.time < 0.65;
      if (accepted) {
        if (data.error) this.workerFailed = true;
        else {
          this.plan = data;
          this.planTime = pending.time;
          this.planEpoch = this.epoch;
        }
      }
      this.onPlannerChange(accepted ? data.error : undefined);
      if (this.queuedPlan) {
        this.queuedPlan = false;
        this.requestPlan(true);
      }
    };
    worker.onerror = () => {
      this.workerFailed = true;
      this.workerBusy = false;
      this.onPlannerChange("候选计算未能启动；分支拳谱与即时参考仍可使用。");
    };
    this.requestPlan(true);
  }

  invalidatePlan() {
    this.epoch = (this.epoch ?? 0) + 1;
    this.planEpoch = -1;
    this.requestPlan(true);
  }

  requestPlan(force = false) {
    if (!this.worker || this.workerFailed) return;
    const now = performance.now();
    if (!force && now - (this.lastPlanRequest ?? -Infinity) < 600) return;
    if (this.workerBusy) {
      this.queuedPlan = true;
      return;
    }
    this.workerBusy = true;
    this.lastPlanRequest = now;
    this.requestRevision = (this.requestRevision ?? 0) + 1;
    this.pendingRequest = {
      revision: this.requestRevision,
      generation: this.generation,
      epoch: this.epoch,
      time: this.combat.time,
    };
    this.worker.postMessage({
      revision: this.requestRevision,
      state: this.combat.saveState({ history: false }),
      settings: this.plannerSettings(),
    });
  }

  export() {
    return {
      schema: 4,
      exportedAt: new Date().toISOString(),
      model: "windwalker-dojo-04-branch-routine",
      scenario: this.scenario,
      demonstration: this.demonstration,
      sessionOrigin: structuredClone(this.origin),
      roundStart: this.roundStart,
      state: this.combat.saveState(),
      routine: this.routine.saveState(),
      summary: this.combat.summary(),
      inputRecords: structuredClone(this.inputRecords),
      routeReview: structuredClone(this.routine.history),
      planner: this.plan
        ? {
            ...this.plan,
            at: this.planTime,
            stale: this.planEpoch !== this.epoch,
          }
        : null,
    };
  }
}
