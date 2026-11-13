import { Combat } from "./combat.js";
import { ACTION_SLOTS, slotAction } from "./actionbar.js";
import { referenceDecision } from "./policy.js";

const EPS = 1e-7;
const DISPLAY_SEED = 0x6d2b79f5;
const PHASES = [
  ["first-zenith", "首乾元"],
  ["small-jade", "小青龙"],
  ["great-jade", "大青龙"],
  ["second-zenith", "二乾元"],
  ["sustain", "持续循环"],
];
const SCOPE =
  "固定种子仅用于展示当前构筑的有界 APL 参考；后续随机动作均为条件预览，" +
  "在下一次旭日或幻灭触发节点停止，不保证全局最优，也不将单次采样称为最佳分支。";

const bounded = (n, fallback, min, max) =>
  Number.isFinite(n) ? Math.max(min, Math.min(max, n)) : fallback;

function phaseFor(c, namespace, windowOwners = new Map(), preferred = null) {
  const active = (name) =>
    c.windows.findLast(
      (w) => w.name === name && w.start <= c.time + EPS && w.end > c.time + EPS,
    );
  const zeniths = c.windows.filter((w) => w.name === "zenith");
  const zenith = active("zenith");
  const window =
    (preferred && active(preferred)) ||
    active("greatJade") ||
    active("jade") ||
    zenith;
  const phase =
    window?.name === "greatJade"
      ? "great-jade"
      : window?.name === "jade"
        ? "small-jade"
        : zenith
          ? zeniths.indexOf(zenith) === 0
            ? "first-zenith"
            : "second-zenith"
          : "sustain";
  return {
    phase,
    phaseWindowId: window?.id ?? null,
    phaseInstanceId: window
      ? (windowOwners.get(window.id) ?? `${namespace}:window-${window.id}`)
      : `${namespace}:sustain`,
    windowIds: c.windows
      .filter((w) => w.start <= c.time + EPS && w.end > c.time + EPS)
      .map((w) => w.id),
  };
}

function addWindows(
  phases,
  c,
  namespace,
  inherited = new Set(),
  windowOwners = new Map(),
) {
  for (const w of c.windows) {
    if (inherited.has(w.id)) continue;
    const phase =
      w.name === "jade"
        ? "small-jade"
        : w.name === "greatJade"
          ? "great-jade"
          : w.name === "zenith"
            ? c.windows.filter((x) => x.name === "zenith").indexOf(w) === 0
              ? "first-zenith"
              : "second-zenith"
            : null;
    if (!phase) continue;
    const entry = phases.find((p) => p.id === phase);
    const id = windowOwners.get(w.id) ?? `${namespace}:window-${w.id}`;
    const existing = entry.windows.find((x) => x.id === id);
    const value = { ...w, id, windowId: w.id, instanceId: id };
    if (existing) Object.assign(existing, value);
    else entry.windows.push(value);
  }
}

/** A legal, synchronous policy projection; never consults a random stream. */
export function routineReference(combat) {
  const d = referenceDecision(combat);
  const slot =
    Object.keys(ACTION_SLOTS).find(
      (key) => slotAction(combat, key) === d.skill,
    ) ?? null;
  const legal =
    d.skill === "cancel"
      ? combat.channel?.skill === "conduit"
      : d.skill && slot && combat.available(d.skill).ok;
  if (legal)
    return {
      ...d,
      spell: d.skill === "sun" && combat.buffLeft("wind") ? "wind" : d.skill,
      slot,
    };
  const remaining = Math.max(0, combat.options.duration - combat.time);
  const boundary = combat.nextBoundary() - combat.time;
  const wait = Math.min(
    remaining,
    boundary > EPS ? boundary : Infinity,
    d.wait > EPS ? d.wait : 0.05,
  );
  return {
    ...d,
    skill: null,
    spell: null,
    slot: null,
    action: "wait",
    wait,
    blocker: d.skill ? "physical-input" : (d.blocker ?? d.rule),
  };
}

function perform(c, skill) {
  if (skill === "cancel") {
    if (!c.cancel({ source: "routine-preview" }))
      throw new Error("Routine preview cannot cancel an absent channel");
  } else {
    const result = c.cast(skill, { source: "routine-preview" });
    if (result.status !== "executed")
      throw new Error(
        `Routine preview attempted an unavailable action: ${skill}`,
      );
  }
}

/** Projects either a preview or an authoritative sunResult snapshot identically. */
export function routineStateSummary(state) {
  return {
    time: state.time,
    chi: state.chi,
    energy: state.energy,
    fists: state.cooldowns.fists,
    sun: state.cooldowns[state.wind > EPS ? "wind" : "sun"],
    jadeLeft: Math.max(
      ...["jade", "greatJade", "avatar"].map((name) => state.buffs[name]),
    ),
    jade: state.buffs.jade,
    greatJade: state.buffs.greatJade,
    avatar: state.buffs.avatar,
    activeWindows: [...state.activeWindows],
    rhythm: state.rhythm,
    combo: state.combo,
    dance: state.dance,
  };
}

const summary = (c) => routineStateSummary(c.snapshot());

function segment(
  c,
  { namespace, end, maxActions, branching = false, windowOwners = new Map() },
) {
  const nodes = [];
  let actions = 0;
  let conditional = branching;
  let iterations = 0;
  while (c.time < end - EPS && actions < maxActions) {
    if (++iterations > 4096)
      throw new Error("Routine preview exceeded its bounded segment budget");
    const d = routineReference(c);
    const phase = phaseFor(c, namespace, windowOwners);
    if (!d.skill) {
      const duration = Math.min(end - c.time, d.wait);
      if (!(duration > EPS)) break;
      const previous = nodes.at(-1);
      if (previous?.kind === "wait")
        previous.duration = c.time + duration - previous.time;
      else
        nodes.push({
          id: `${namespace}:node-${nodes.length + 1}`,
          kind: "wait",
          skill: null,
          spell: null,
          slot: null,
          time: c.time,
          duration,
          ...phase,
          conditional,
          reference: d,
          reason: d.text,
        });
      c.advance(duration);
      continue;
    }
    const channelSkill = c.channel?.skill ?? null;
    const node = {
      id: `${namespace}:node-${nodes.length + 1}`,
      kind:
        d.skill === "cancel"
          ? "cancel"
          : ["fists", "crane", "conduit"].includes(d.skill)
            ? "channel"
            : "cast",
      skill: d.skill,
      spell: d.spell,
      slot: d.slot,
      time: c.time,
      ...phase,
      conditional,
      reference: d,
      reason: d.text,
    };
    if (d.skill === "cancel") node.channelSkill = channelSkill;
    nodes.push(node);
    actions++;
    if (d.skill === "sun" || (branching && d.skill === "blackout")) {
      if (branching) node.unresolved = true;
      return {
        nodes,
        trigger: branching ? null : node,
        stopReason: d.skill === "sun" ? "next-sun" : "blackout-proc",
      };
    }
    perform(c, d.skill);
    const opensWindow =
      d.skill === "zenith"
        ? "zenith"
        : d.skill === "dragon"
          ? "jade"
          : d.skill === "cancel" && channelSkill === "conduit"
            ? "greatJade"
            : null;
    if (opensWindow)
      Object.assign(node, phaseFor(c, namespace, windowOwners, opensWindow));
    if (node.kind === "channel")
      node.duration = Math.max(0, (c.channel?.end ?? c.time) - c.time);
    if (["palm", "fists", "crane", "blackout"].includes(d.skill))
      conditional = true;
  }
  if (
    actions >= maxActions &&
    ["fists", "crane"].includes(c.channel?.skill) &&
    nodes.at(-1)?.kind === "channel"
  ) {
    const duration = Math.min(end, c.channel.end) - c.time;
    if (duration > EPS) {
      nodes.push({
        id: `${namespace}:node-${nodes.length + 1}`,
        kind: "wait",
        skill: null,
        spell: null,
        slot: null,
        time: c.time,
        duration,
        ...phaseFor(c, namespace, windowOwners),
        conditional,
        channelSkill: c.channel.skill,
        reason: "等待当前通道完成。",
      });
      c.advance(duration);
    }
  }
  return {
    nodes,
    trigger: null,
    stopReason: actions >= maxActions ? "action-limit" : "horizon",
  };
}

function previewCombat(combat) {
  const c = Combat.fromState(combat.saveState());
  c.randomState = DISPLAY_SEED;
  c.options.seed = DISPLAY_SEED;
  // Accepted input remains owned by the session; previews never execute it invisibly.
  c.queue = null;
  c.queueInput = null;
  c.queueAttemptId = null;
  return c;
}

function sunFork(
  c,
  { id, triggerNodeId, maxActions, horizon, phases, windowOwners },
) {
  const state = c.saveState();
  const inherited = new Set(c.windows.map((w) => w.id));
  const fork = { id, triggerNodeId, status: "unresolved", branches: [] };
  for (const mainCrit of [false, true]) {
    for (const dawnCrit of [null, false, true]) {
      const outcome = { mainCrit, dawnTriggered: dawnCrit !== null, dawnCrit };
      const key = `${mainCrit ? "main-crit" : "main-normal"}-${dawnCrit === null ? "no-dawn" : dawnCrit ? "dawn-crit" : "dawn-normal"}`;
      const branchId = `${id}:${key}`;
      const branch = Combat.fromState(state);
      // Only the next Sun is constrained. Later declared outcomes remain intact.
      branch.options.sunOutcomes[branch.sunCount] = { ...outcome };
      perform(branch, "sun");
      const afterSun = summary(branch);
      const continuation = segment(branch, {
        namespace: branchId,
        end: Math.min(branch.options.duration, branch.time + horizon),
        maxActions,
        branching: true,
        windowOwners,
      });
      addWindows(phases, branch, branchId, inherited);
      fork.branches.push({
        id: branchId,
        outcome,
        label: `${mainCrit ? "主段暴击" : "主段不暴"} · ${dawnCrit === null ? "无晨晖" : dawnCrit ? "晨晖暴击" : "晨晖普通"}`,
        status: "unresolved",
        nodes: continuation.nodes,
        summary: afterSun,
        tailSummary: summary(branch),
        stopReason: continuation.stopReason,
      });
    }
  }
  return fork;
}

/** Pure data. maxActions and horizon bound each expanded segment, excluding waits. */
export function buildRoutineGraph(
  combat,
  { id = "route-1", maxActions = 8, horizon = 14 } = {},
) {
  maxActions = Math.floor(bounded(maxActions, 8, 1, 24));
  horizon = bounded(horizon, 14, 0.05, 30);
  const c = previewCombat(combat);
  const phases = PHASES.map(([phase, label]) => ({
    id: phase,
    name: label,
    label,
    windows: [],
  }));
  const prefix = segment(c, {
    namespace: `${id}:prefix`,
    end: Math.min(c.options.duration, c.time + horizon),
    maxActions,
  });
  addWindows(phases, c, `${id}:prefix`);
  const graph = {
    id,
    createdAt: combat.time,
    prefix: prefix.nodes,
    fork: null,
    phases,
    scope: SCOPE,
    displaySeed: DISPLAY_SEED,
    maxActions,
    horizon,
    stopReason: prefix.stopReason,
  };
  if (prefix.trigger)
    graph.fork = sunFork(c, {
      id: `${id}:sun-fork`,
      triggerNodeId: prefix.trigger.id,
      maxActions,
      horizon,
      phases,
      windowOwners: new Map(
        c.windows.map((w) => [w.id, `${id}:prefix:window-${w.id}`]),
      ),
    });
  return graph;
}

/** Refreshes an unresolved Sun from actual state without replaying its completed prefix. */
export function rebaseRoutineGraphAtSun(combat, graph) {
  const reference = routineReference(combat);
  const trigger = graph.prefix.find((n) => n.id === graph.fork?.triggerNodeId);
  if (
    reference.skill !== "sun" ||
    trigger?.skill !== "sun" ||
    graph.fork.status !== "unresolved"
  ) {
    throw new RangeError("Sun rebase requires a ready, unresolved Sun");
  }
  const c = previewCombat(combat);
  const rebased = structuredClone(graph);
  const existing = graph.phases.flatMap((p) => p.windows);
  const used = new Set(graph.prefix.map((n) => n.phaseInstanceId));
  const windowOwners = new Map(
    c.windows.map((w) => [
      w.id,
      existing.find(
        (old) =>
          old.windowId === w.id &&
          old.name === w.name &&
          used.has(old.instanceId),
      )?.instanceId ?? `${graph.id}:prefix:window-${w.id}`,
    ]),
  );
  for (const phase of rebased.phases)
    phase.windows = phase.windows.filter(
      (w) => windowOwners.get(w.windowId) === w.instanceId,
    );
  addWindows(rebased.phases, c, `${graph.id}:prefix`, new Set(), windowOwners);
  const node = rebased.prefix.find((n) => n.id === trigger.id);
  Object.assign(node, {
    time: c.time,
    spell: reference.spell,
    slot: reference.slot,
    conditional: false,
    reference,
    reason: reference.text,
    ...phaseFor(c, `${graph.id}:prefix`, windowOwners),
  });
  rebased.fork = sunFork(c, {
    id: graph.fork.id,
    triggerNodeId: trigger.id,
    maxActions: graph.maxActions,
    horizon: graph.horizon,
    phases: rebased.phases,
    windowOwners,
  });
  rebased.fork.rebasedAt = combat.time;
  rebased.fork.basis = {
    source: "actual-pre-sun",
    actionId: combat.actionSerial,
    sunIndex: combat.sunCount,
  };
  return rebased;
}
