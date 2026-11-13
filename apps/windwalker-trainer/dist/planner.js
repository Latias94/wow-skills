import { Combat, SKILLS } from './combat.js';
import { ACTION_SLOTS, slotAction } from './actionbar.js';
import { referenceDecision } from './policy.js';

const EPS = 1e-7;
const TAIL = 4;
const MAX_FIRST_ACTIONS = 5;
const SCOPE = '当前状态的核心模型局部续算；比较少量合法首动作，后续使用参考策略。均值是模型预期伤害，不是实服DPS或精确损失，也不保证全局最优。';
const bounded = (value, fallback, min, max) => Number.isFinite(value) ? Math.max(min, Math.min(max, value)) : fallback;

function stableJSON(value) {
  if (Array.isArray(value)) return `[${value.map(stableJSON).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().filter(key => value[key] !== undefined)
      .map(key => `${JSON.stringify(key)}:${stableJSON(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function hash(text) {
  let result = 2166136261;
  for (let i = 0; i < text.length; i++) result = Math.imul(result ^ text.charCodeAt(i), 16777619);
  return result >>> 0;
}

function samplingFor(combat, count) {
  const options = Object.fromEntries(['targets', 'duration', 'attackable', 'bloodlust', 'critMode',
    'inputMode', 'protectCrane', 'encounterEvents', 'sunOutcomes'].map(key => [key, combat.options[key]]));
  // Seed and live RNG are deliberately absent. Pending descriptors contain captured,
  // already-observed cast data; future rolls are generated only inside each fork.
  const observed = { snapshot: combat.snapshot(), options, channel: combat.channel, pending: combat.pending,
    queue: combat.queue, cooldowns: combat.cooldowns, brew: combat.brew, teachings: combat.teachings,
    zenithCrit: combat.zenithCrit, sunCount: combat.sunCount };
  const observedHash = hash(stableJSON(observed));
  const seeds = Array.from({ length: count }, (_, index) => hash(`${observedHash}:sample:${index}`) || 1);
  return { observedHash: observedHash.toString(16).padStart(8, '0'), seeds, paired: true };
}

function physicalActions(combat) {
  return [...new Set(Object.keys(ACTION_SLOTS).map(slot => slotAction(combat, slot)))];
}

function legal(combat, skill) {
  if (combat.time >= combat.options.duration - EPS) return false;
  if (skill === 'cancel') return combat.channel?.skill === 'conduit';
  return physicalActions(combat).includes(skill) && combat.available(skill).ok;
}

function boundaryWait(combat) {
  const remaining = combat.options.duration - combat.time;
  if (remaining <= EPS) return 0;
  const boundary = combat.nextBoundary() - combat.time;
  return Math.min(remaining, Number.isFinite(boundary) && boundary > EPS ? boundary : 0.05);
}

function currentDecision(combat) {
  const reference = referenceDecision(combat);
  if (reference.skill && legal(combat, reference.skill)) {
    const action = reference.skill === 'sun' && combat.buffLeft('wind') ? 'wind' : reference.skill;
    return { ...reference, action };
  }
  const wait = Math.min(boundaryWait(combat), reference.wait > EPS ? reference.wait : Infinity);
  return { ...reference, skill: null, action: 'wait', wait,
    text: reference.skill ? '当前物理按键或输入保护不允许该动作，等待下一个状态边界。' : reference.text };
}

function perform(combat, skill) {
  if (!legal(combat, skill)) throw new Error(`Planner attempted an unavailable action: ${skill}`);
  if (skill === 'cancel') return combat.cancel({ source: 'planner' });
  const result = combat.cast(skill, { source: 'planner' });
  if (!result.ok || result.queued) throw new Error(`Planner failed to execute ${skill}`);
  return true;
}

function rollReference(combat, end) {
  let iterations = 0;
  while (combat.time < end - EPS) {
    if (++iterations > 30000) throw new Error('Planner exceeded its bounded rollout budget');
    const decision = currentDecision(combat);
    if (decision.skill) perform(combat, decision.skill);
    else combat.advance(Math.min(end - combat.time, decision.wait || boundaryWait(combat)));
  }
}

function candidatesFor(combat, baseline, mode) {
  const candidates = [{ id: 'baseline', skill: baseline.skill, action: baseline.action, baseline: true }];
  if (mode === 'apl' || combat.time >= combat.options.duration - EPS) return candidates;
  // The reference keeps a complete FoF channel. Do not turn its wait into a
  // suggestion to clip; explicit cancellation is considered only for Conduit.
  if (combat.channel?.skill !== 'fists') {
    const priority = ['fists', 'sun', 'crane', 'dragon', 'stomp', 'conduit', 'zenith', 'tiger', 'palm', 'blackout'];
    const actions = priority.filter(skill => skill !== baseline.skill && legal(combat, skill));
    for (const skill of actions.slice(0, MAX_FIRST_ACTIONS)) {
      candidates.push({ id: skill, skill, action: skill === 'sun' && combat.buffLeft('wind') ? 'wind' : skill });
    }
    if (baseline.skill !== 'cancel' && legal(combat, 'cancel')) {
      candidates.push({ id: 'cancel', skill: 'cancel', action: 'cancel' });
    }
  }
  candidates.push({ id: 'wait', skill: null, action: 'wait', wait: boundaryWait(combat) });
  return candidates;
}

function sequenceFor(combat, candidate, start, horizonEnd, maxActions) {
  const actions = [...combat.casts, ...combat.controls]
    .filter(action => action.time >= start - EPS && action.time < horizonEnd - EPS)
    .sort((a, b) => a.time - b.time || (a.actionId ?? 0) - (b.actionId ?? 0))
    .map(({ time, skill, spell }) => ({ time, skill, spell, conditional: true }));
  if (candidate.action === 'wait') {
    actions.unshift({ time: start, skill: null, spell: null, action: 'wait', conditional: false });
  } else if (actions.length) actions[0].conditional = false;
  return actions.slice(0, maxActions);
}

function evaluate(state, candidate, sampling, horizon, maxActions) {
  const end = Math.min(state.options.duration, state.time + horizon + TAIL);
  const values = [];
  let sequence = [];
  for (const [index, seed] of sampling.seeds.entries()) {
    const combat = Combat.fromState(state);
    combat.randomState = seed;
    combat.options.seed = seed;
    if (!candidate.baseline) {
      if (candidate.skill) perform(combat, candidate.skill);
      else combat.advance(Math.min(candidate.wait, end - combat.time));
    }
    rollReference(combat, end);
    values.push(combat.damage - state.damage);
    if (index === 0) sequence = sequenceFor(combat, candidate, state.time,
      Math.min(state.options.duration, state.time + horizon), maxActions);
  }
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const spread = values.length > 1 ?
    Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (values.length - 1)) : 0;
  return { ...candidate, mean, spread, min: Math.min(...values), max: Math.max(...values),
    samples: values.length, values, sequence };
}

function comparison(a, b) {
  const differences = a.values.map((value, index) => value - b.values[index]);
  const mean = a.mean - b.mean;
  const error = differences.length > 1 ? Math.sqrt(differences.reduce((sum, value) =>
    sum + (value - mean) ** 2, 0) / (differences.length - 1) / differences.length) : Infinity;
  return { mean, close: Math.abs(mean) <= Math.max(1, Math.abs(b.mean) * 0.02),
    noisy: mean <= 2 * error };
}

/**
 * Pure current-state preview. Absolute sequence times use the combat clock.
 * `maxActions` limits displayed entries; the score includes an additional 4s
 * reference continuation, capped by the declared encounter duration.
 */
export function createPlan(combat, { mode = 'apl', horizon = 10, samples = 4, maxActions = 5 } = {}) {
  if (!['apl', 'search'].includes(mode)) throw new TypeError('mode must be apl or search');
  horizon = bounded(horizon, 10, 8, 12);
  samples = Math.floor(bounded(samples, 4, 1, 16));
  maxActions = Math.floor(bounded(maxActions, 5, 1, 12));
  const state = combat.saveState({ history: false });
  // Decisions and observation hashing also run on an isolated instance.
  const observed = Combat.fromState(state);
  const baselineDecision = currentDecision(observed);
  const sampling = samplingFor(observed, samples);
  const candidates = candidatesFor(observed, baselineDecision, mode);
  const results = candidates.map(candidate => evaluate(state, candidate, sampling, horizon, maxActions));
  const baseline = results[0];
  const ranked = [...results].sort((a, b) => b.mean - a.mean);
  let selected = ranked[0];
  let uncertain = samples < 4;
  if (mode === 'search' && selected !== baseline) {
    const margin = comparison(selected, baseline);
    if (margin.close || margin.noisy) { selected = baseline; uncertain = true; }
  }
  const rival = ranked.find(candidate => candidate !== selected);
  if (rival) {
    const margin = comparison(selected, rival);
    uncertain ||= margin.close || margin.noisy;
  }
  const ended = state.time >= state.options.duration - EPS;
  if (mode === 'apl') uncertain ||= !ended && selected.spread > EPS;
  if (ended) uncertain = false;
  const decision = selected.baseline ? baselineDecision : selected.skill ?
    { skill: selected.skill, action: selected.action, rule: 'local-search',
      text: selected.skill === 'cancel' ? '局部样本比较建议结束当前天神通道。' :
        `局部样本比较建议${selected.action === 'wind' ? '疾风呼啸踢' : SKILLS[selected.skill].name}。` } :
    { skill: null, action: 'wait', wait: selected.wait, rule: 'local-search-wait',
      text: '等待下一个状态边界，再根据届时资源、触发与目标情况重算。' };
  return {
    decision: { ...decision, uncertain }, sequence: selected.sequence,
    alternatives: ranked.map(({ values, sequence, ...candidate }) => ({
      ...candidate, deltaFromBaseline: candidate.mean - baseline.mean, unit: 'core-model-damage',
    })),
    method: mode, scope: SCOPE, uncertain, horizon, tail: TAIL,
    evaluationHorizon: Math.max(0, Math.min(horizon + TAIL, state.options.duration - state.time)),
    sampling, previewSample: 0,
    notes: ['仅搜索首动作，后续条件动作须随实测状态重算。', '少量配对样本的差距与离散度仅供练习比较。'],
  };
}
