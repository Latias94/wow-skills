import { CALIBRATION } from './calibration.js';
import { referenceDecision } from './policy.js';

export const SKILLS = {
  palm: { name: '猛虎掌', glyph: '虎', color: '#c59b55', chi: 0, energy: 55 },
  blackout: { name: '幻灭踢', glyph: '灭', color: '#b68bcb', chi: 1 },
  sun: { name: '旭日东升踢', glyph: '日', color: '#f0ba56', chi: 2, cooldown: 10 },
  fists: { name: '怒雷破', glyph: '雷', color: '#79b9dc', chi: 2, cooldown: 24 },
  crane: { name: '神鹤引项踢', glyph: '鹤', color: '#70cba4', chi: 2 },
  dragon: { name: '升龙霸', glyph: '龙', color: '#88d5b8', chi: 0, cooldown: 30 },
  tiger: { name: '白虎下凡', glyph: '寅', color: '#e2e5d3', chi: 0, cooldown: 90 },
  zenith: { name: '乾元', glyph: '乾', color: '#e7ac67', chi: 0, offGcd: true },
  conduit: { name: '天神御身', glyph: '神', color: '#88cfc2', chi: 0, cooldown: 90 },
  stomp: { name: '乾元镇踏', glyph: '踏', color: '#a2be71', chi: 0 },
};

const EPS = 1e-7;
const CORE_CDS = new Set(['sun', 'wind', 'fists', 'dragon']);
const HASTED_CDS = new Set(['sun', 'wind', 'fists']);
const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
const STATE_FIELDS = [
  'options', 'randomState', 'time', 'energy', 'chi', 'damage', 'gcdEnd', 'lastSkill', 'activeCombo',
  'cooldowns', 'previousAction', 'zenithRecharge', 'zenithLock', 'buffs', 'rhythm', 'dance', 'combo',
  'stomps', 'brew', 'brewAccumulator', 'teachings', 'zenithCrit', 'channel', 'pending', 'events',
  'hits', 'casts', 'controls', 'windows', 'windowSerial', 'queue', 'queueInput', 'wastedChi',
  'droppedProcs', 'clippedFists', 'comboBreaks', 'serial', 'castSerial', 'lastError',
  'lastDanceAttempt', 'danceBadLuck', 'fistsOpportunities', 'fistsCycle', 'totals',
  'attempts', 'attemptSerial', 'queueAttemptId', 'sunCount', 'attackable', 'actionSerial',
];

export class Combat {
  constructor(options = {}) {
    this.options = { seed: 1026, targets: 1, duration: 45, initialChi: 2, initialBrew: 10, bloodlust: false, critMode: 'random',
      inputMode: 'raw', protectCrane: false, sunOutcomes: [], encounterEvents: [], ...structuredClone(options) };
    this.randomState = (Number(this.options.seed) >>> 0) || 1;
    this.time = 0;
    this.attackable = true;
    this.energy = 150;
    this.chi = this.options.initialChi;
    this.damage = 0;
    this.totals = { fists: 0, jadeFists: 0, fistsDamage: 0, jadeFistsDamage: 0 };
    this.gcdEnd = 0;
    this.lastSkill = null;
    this.activeCombo = null;
    this.cooldowns = { sun: 0, wind: 0, fists: 0, dragon: 0, tiger: 0, conduit: 0 };
    this.previousAction = null;
    this.zenithRecharge = [];
    this.zenithLock = 0;
    this.buffs = {};
    this.rhythm = 0;
    this.dance = 0;
    this.combo = 0;
    this.stomps = 0;
    this.brew = this.options.initialBrew;
    this.brewAccumulator = 0;
    this.teachings = 0;
    this.zenithCrit = 0;
    this.channel = null;
    this.pending = [];
    this.events = [];
    this.hits = [];
    this.casts = [];
    this.controls = [];
    this.attempts = [];
    this.attemptSerial = 0;
    this.windows = [];
    this.windowSerial = 0;
    this.queue = null;
    this.queueInput = null;
    this.queueAttemptId = null;
    this.wastedChi = 0;
    this.droppedProcs = 0;
    this.clippedFists = 0;
    this.comboBreaks = 0;
    this.serial = 0;
    this.castSerial = 0;
    this.actionSerial = 0;
    this.sunCount = 0;
    this.lastError = '';
    this.lastDanceAttempt = 0;
    this.danceBadLuck = 0;
    this.fistsOpportunities = [];
    this.fistsCycle = 0;
    if (this.options.bloodlust) this.setBuff('bloodlust', 40);
    for (const event of this.options.encounterEvents) this.later(event.at, 'scenario', { ...event });
    while (this.pending.length && this.pending[0].at <= EPS) this.dispatch(this.pending.shift());
  }

  saveState({ history = true } = {}) {
    const state = Object.fromEntries(STATE_FIELDS.map(key => [key, this[key]]));
    if (!history) {
      for (const key of ['events', 'hits', 'casts', 'controls', 'attempts', 'fistsOpportunities']) state[key] = [];
      state.windows = this.windows.filter(w => w.end > this.time + EPS);
    }
    return structuredClone(state);
  }

  static fromState(state) {
    return Object.assign(new Combat(), structuredClone(state));
  }

  random() {
    let n = this.randomState;
    n ^= n << 13; n ^= n >>> 17; n ^= n << 5;
    this.randomState = n >>> 0;
    return this.randomState / 4294967296;
  }

  buffLeft(name) { const left = (this.buffs[name] || 0) - this.time; return left > EPS ? left : 0; }
  green() { return ['jade', 'greatJade', 'avatar'].some(k => this.buffLeft(k) > EPS); }
  jadeCount() { return Number(this.buffLeft('greatJade') > EPS || this.buffLeft('jade') > EPS) + Number(this.buffLeft('avatar') > EPS); }
  haste() { return (1 + CALIBRATION.stats.haste_pct) * 1.1 ** this.jadeCount() * (this.buffLeft('bloodlust') ? 1.3 : 1); }
  recovery() {
    let rate = 1;
    if (this.buffLeft('greatJade') > EPS) rate *= 2.5;
    else if (this.buffLeft('jade') > EPS) rate *= 1.75;
    if (this.buffLeft('avatar') > EPS) rate *= 1.75;
    return rate;
  }

  setBuff(name, duration) {
    if (name === 'greatJade') this.endBuff('jade');
    if (name === 'jade' && this.buffLeft('greatJade') > EPS) return;
    this.endBuff(name);
    this.buffs[name] = this.time + duration;
    if (['jade', 'greatJade', 'avatar', 'zenith', 'tiger', 'bloodlust'].includes(name)) {
      this.windows.push({ id: ++this.windowSerial, name, start: this.time, end: this.time + duration });
    }
  }

  endBuff(name) {
    if (this.buffLeft(name) > EPS) {
      const w = this.windows.findLast(w => w.name === name && w.end > this.time);
      if (w) w.end = this.time;
    }
    this.buffs[name] = 0;
  }

  charges(id) { return id === 'zenith' ? 2 - this.zenithRecharge.length : id === 'stomp' ? this.stomps : 0; }
  remaining(id) {
    if (id === 'zenith') return Math.max(0, this.zenithLock - this.time, this.charges(id) ? 0 : this.zenithRecharge[0] - this.time);
    if (id === 'stomp') return this.stomps && this.buffLeft('zenith') ? 0 : Infinity;
    const work = this.cooldowns[id] || 0;
    return work / ((HASTED_CDS.has(id) ? this.haste() : 1) * (CORE_CDS.has(id) ? this.recovery() : 1));
  }

  costs(id) {
    const s = SKILLS[id];
    let chi = s.chi;
    if (id === 'blackout' && this.combo) chi = 0;
    if (id === 'crane' && this.dance) chi = 0;
    if (this.buffLeft('zenith')) chi = Math.max(0, chi - 1);
    return { chi, energy: s.energy || 0 };
  }

  available(id, ignoreGcd = false) {
    const s = SKILLS[id];
    if (!s || this.time >= this.options.duration) return { ok: false, reason: '本轮已结束' };
    if ((!this.attackable || this.options.targets <= 0) && !['tiger', 'zenith'].includes(id)) return { ok: false, reason: '当前没有可攻击目标' };
    if (this.options.inputMode === 'protected' && this.channel?.skill === 'fists') return { ok: false, reason: '保护怒雷引导中' };
    if (this.options.protectCrane && this.channel?.skill === 'crane' && id === 'fists') return { ok: false, reason: '保护神鹤引导中' };
    if (!ignoreGcd && !s.offGcd && this.gcdEnd > this.time + EPS) return { ok: false, reason: '公共冷却中' };
    const spell = id === 'sun' && this.buffLeft('wind') ? 'wind' : id;
    if (this.remaining(spell) > EPS) return { ok: false, reason: id === 'stomp' ? '需要乾元踏层数' : '技能冷却中' };
    if (id === 'zenith' && this.stomps) return { ok: false, reason: '先消费剩余的乾元踏次数' };
    if (id === 'conduit' && !this.buffLeft('conduitReady')) return { ok: false, reason: '先召唤白虎' };
    if (id === 'dragon' && !this.buffLeft('dragonReady')) return { ok: false, reason: '需要旭日和怒雷触发的升龙可用窗口' };
    const cost = this.costs(id);
    if (this.chi < cost.chi) return { ok: false, reason: `需要 ${cost.chi} 点真气` };
    if (this.energy + EPS < cost.energy) return { ok: false, reason: '能量不足' };
    return { ok: true };
  }

  triggerDragon() {
    const both = Math.min(this.remaining('sun'), this.remaining('fists'));
    if (both > EPS && !this.buffLeft('dragonReady')) this.setBuff('dragonReady', both + 1.5 / this.haste());
  }

  gainChi(amount) {
    const overflow = Math.max(0, this.chi + amount - 6);
    this.wastedChi += overflow;
    if (overflow) this.emit('resourceWaste', `真气溢出 ${overflow} 点`, { amount: overflow });
    this.chi = clamp(this.chi + amount, 0, 6);
  }

  proc(name) {
    if (this[name] >= 2) { this.droppedProcs++; this.emit('procWaste', `${name === 'dance' ? '赤精' : '幻灭高亮'}触发溢出`); }
    this[name] = Math.min(2, this[name] + 1);
    this.setBuff(name, 15);
  }

  later(delay, type, data, channelId = null) {
    this.pending.push({ at: this.time + delay, type, data, channelId });
    this.pending.sort((a, b) => a.at - b.at);
  }

  fistsPulse(data, channelId, tier = false) {
    this.hit('fists', CALIBRATION.damage[tier ? 'fistsTier' : 'fists'].reference, 1,
      { aoe: true, secondary: 0.6, tier, combo: data.combo, castId: data.castId });
    this.rhythm = Math.min(6, this.rhythm + 1);
    this.setBuff('rhythm', 20);
    if (!tier && this.channel?.id === channelId) this.channel.ticks++;
  }

  scheduleFists(data, channelId) {
    const interval = Math.round(1000 / data.hasteSnapshot * 0.5 ** this.jadeCount()) / 1000;
    this.later(Math.min(interval, data.endAt - this.time), 'fistsTick', data, channelId);
  }

  dispatch(event) {
    const { data, channelId } = event;
    switch (event.type) {
      case 'scenario':
        if (data.targets != null) this.options.targets = data.targets;
        if (data.attackable != null) this.attackable = data.attackable;
        if (data.bloodlust === true) this.setBuff('bloodlust', 40);
        if (data.bloodlust === false) this.endBuff('bloodlust');
        this.emit('scenario', '遭遇状态变化', { at: data.at, targets: this.options.targets,
          attackable: this.attackable, bloodlust: this.buffLeft('bloodlust') > 0 });
        break;
      case 'hit':
        this.hit(data.skill, data.reference, data.multiplier, data.options);
        break;
      case 'fistsTick':
        this.fistsPulse(data, channelId);
        if (this.time >= data.endAt - EPS) this.channel = null;
        else this.scheduleFists(data, channelId);
        break;
      case 'channelEnd':
        if (this.channel?.id === channelId) this.channel = null;
        break;
      case 'craneExpire':
        this.reduce('fists', 0.5 * Math.min(5, this.options.targets));
        break;
      case 'conduitTick':
        this.hit('conduit', CALIBRATION.damage.conduit.reference, 1,
          { aoe: true, mastery: false, combo: data.combo, castId: data.castId });
        if (this.channel?.id === channelId) {
          this.channel.ticks++;
          this.channel.nextTick = this.time + data.interval;
          this.channel.cancelEligible = data.index > 0 && (this.remaining('sun') <= EPS || this.remaining('fists') <= EPS || !this.buffLeft('jade')) &&
            (!this.buffLeft('bloodlust') || !this.stomps || this.chi > 4);
          if (data.index === 4) { this.channel = null; this.setBuff('greatJade', 6); }
        }
        break;
      default:
        throw new Error(`Unknown combat event: ${event.type}`);
    }
  }

  emit(type, text, extra = {}) { this.events.push({ time: this.time, type, text, ...extra }); }

  // SimC adjust() scales reductions by recovery, not haste. Convert the wall-time
  // reduction back into the unhasted work representation used here.
  reduce(id, amount) { this.cooldowns[id] = Math.max(0, this.cooldowns[id] - amount * (HASTED_CDS.has(id) ? this.haste() : 1)); }

  rollDance() {
    if (this.time <= this.lastDanceAttempt + EPS) return;
    const elapsed = this.time - this.lastDanceAttempt;
    this.danceBadLuck += Math.min(elapsed, 3.5);
    const rate = this.haste();
    const protection = Math.max(1, 1 + (Math.min(1000, this.danceBadLuck) / (60 / rate) - 1.5) * 3);
    const chance = rate * Math.min(elapsed, 3.5) / 60 * protection;
    this.lastDanceAttempt = this.time;
    if (this.random() < chance) { this.proc('dance'); this.danceBadLuck = 0; }
  }

  hit(skill, reference, multiplier = 1, { crit = null, aoe = false, secondary = 1, tier = false, mastery = true, combo = this.activeCombo, castId = null, spell = skill } = {}) {
    if (!this.attackable || this.options.targets <= 0) return null;
    let critChance = CALIBRATION.stats.crit_pct + (this.buffLeft('zenith') ? this.zenithCrit : 0) + (this.buffLeft('tiger') ? 0.04 : 0);
    if (['sun', 'dawn'].includes(skill)) critChance += 0.2 + 0.04 * Math.min(5, this.options.targets);
    const isCrit = crit ?? (this.random() < clamp(critChance, 0, 1));
    const comboMultiplier = mastery && combo === false ? 1 / (1 + CALIBRATION.stats.mastery_pct) : 1;
    const targets = aoe ? 1 + (this.options.targets - 1) * secondary : 1;
    const amount = reference * multiplier * comboMultiplier * targets * (isCrit ? 2.1 : 1);
    const hit = { time: this.time, skill, spell, castId, amount, crit: isCrit, jade: this.green(), tier, targets: aoe ? this.options.targets : 1 };
    this.damage += amount;
    if (skill === 'fists') {
      this.totals.fistsDamage += amount;
      if (hit.jade) this.totals.jadeFistsDamage += amount;
    }
    this.hits.push(hit);
    return hit;
  }

  cast(id, input = null, queuedAttemptId = null) {
    const attemptId = queuedAttemptId ?? ++this.attemptSerial;
    const acceptedInput = input ? { ...input, at: input.at ?? this.time } : null;
    const s = SKILLS[id];
    let check = this.available(id);
    const attempt = (status, extra = {}) => {
      this.attempts.push({ attemptId, time: this.time, skill: id,
        spell: id === 'sun' && this.buffLeft('wind') ? 'wind' : id, input: acceptedInput, status, ...extra });
    };
    if (!check.ok) {
      if (check.reason === '公共冷却中' && this.gcdEnd - this.time <= 0.4 + EPS) {
        const projected = Combat.fromState(this.saveState({ history: false }));
        projected.queue = null;
        projected.queueInput = null;
        projected.queueAttemptId = null;
        projected.advance(this.gcdEnd - this.time);
        check = projected.available(id);
        if (check.ok) {
          this.queue = id;
          this.queueInput = acceptedInput;
          this.queueAttemptId = attemptId;
          attempt('queued');
          return { ok: true, queued: true, status: 'queued', attemptId };
        }
      }
      this.lastError = check.reason;
      attempt('rejected', { reason: check.reason });
      return { ...check, status: 'rejected', attemptId };
    }
    const before = this.snapshot();
    const decision = referenceDecision(this);
    this.observeFists();
    const openOpportunity = this.fistsOpportunities.findLast(o => o.cycle === this.fistsCycle && o.actualAt == null);
    if (openOpportunity && id !== 'fists') openOpportunity.choices.push({ time: this.time, skill: id, decision });
    const spell = id === 'sun' && this.buffLeft('wind') ? 'wind' : id;
    if (this.channel && !(id === 'stomp' && this.channel.skill === 'conduit') &&
      !(this.channel.skill === 'crane' && ['palm', 'blackout', 'sun', 'dragon', 'tiger', 'stomp'].includes(spell))) this.cancel({ source: 'spell', skill: id, input: acceptedInput });
    const atStart = this.snapshot();
    if (!s.offGcd) { this.queue = null; this.queueInput = null; this.queueAttemptId = null; }
    this.lastError = '';
    const cost = this.costs(id);
    this.chi -= cost.chi;
    this.energy -= cost.energy;
    if (id !== 'tiger') this.registerCombo(id === 'sun' && this.buffLeft('wind') ? 'wind' : id);
    if (!s.offGcd) this.gcdEnd = this.time + (id === 'tiger' ? Math.max(0.75, 1 / this.haste()) : id === 'conduit' ? 0.75 : 1);
    if (s.cooldown) this.cooldowns[spell] = s.cooldown;
    this.previousAction = spell;
    const castId = ++this.castSerial;
    attempt('executed', { castId });
    this.casts.push({ castId, actionId: ++this.actionSerial, time: this.time, skill: id, spell, chi: this.chi, jade: this.green(), before, atStart, input: acceptedInput, combo: this.activeCombo, decision });
    this.emit('cast', spell === 'wind' ? '疾风呼啸踢' : s.name, { castId, skill: id, spell });
    const d = CALIBRATION.damage;
    const combo = this.activeCombo;
    const hit = (skill, ref, multiplier = 1, opts = {}) => this.hit(skill, ref, multiplier, { combo, castId, spell: skill === id ? spell : skill, ...opts });
    const hadDance = this.dance > 0;
    if (['blackout', 'sun', 'fists', 'crane'].includes(id)) {
      this.brewAccumulator += id === 'blackout' ? 1 : id === 'fists' ? 3 : 2;
      while (this.brewAccumulator >= 3) { this.brew = Math.min(30, this.brew + 1); this.brewAccumulator -= 3; }
      this.rollDance();
    }

    if (id === 'palm') {
      hit(id, d.palm.reference);
      this.gainChi(2);
      this.teachings = Math.min(3, this.teachings + 1);
      if (this.random() < 0.08) this.proc('combo');
    } else if (id === 'blackout') {
      const highlighted = this.combo > 0;
      hit(id, d.blackout.reference);
      this.reduce('sun', this.buffLeft('zenith') ? 2 : 1);
      this.reduce('fists', this.buffLeft('zenith') ? 2 : 1);
      for (let i = 0; i <= this.teachings; i++) if (this.random() < 0.12) this.cooldowns.sun = 0;
      this.teachings = 0;
      if (highlighted) {
        this.combo--;
        if (this.random() < 0.6) { this.setBuff('wind', 15); this.cooldowns.sun = 0; this.emit('proc', '疾风踢触发，旭日已重置'); }
        this.gainChi(1);
      }
    } else if (id === 'sun') {
      const wind = this.buffLeft('wind') > 0;
      const multiplier = 1 + this.rhythm * 0.1;
      this.rhythm = 0;
      this.endBuff('rhythm');
      this.endBuff('wind');
      const mode = this.options.critMode;
      const forced = mode !== 'random';
      const sunIndex = this.sunCount++;
      const outcome = this.options.sunOutcomes[sunIndex] ?? {};
      const fistsBefore = this.remaining('fists');
      const first = hit(id, d[wind ? 'wind' : 'sun'].reference, multiplier,
        { crit: outcome.mainCrit ?? (forced ? mode !== 'none' : null), aoe: wind, secondary: 0.5 });
      if (first.crit) this.reduce('fists', 4);
      const dawn = outcome.dawnTriggered ?? (forced || this.random() < clamp(this.haste() - 1, 0, 1));
      const result = { castId, sunIndex, mainCrit: first.crit, dawnTriggered: dawn, dawnCrit: null,
        crits: Number(first.crit), dawn, wind, castTime: this.time, fistsBefore };
      if (dawn) {
        const h = hit('dawn', d.dawn.reference, multiplier, { crit: outcome.dawnCrit ?? (forced ? mode === 'double' : null) });
        this.gainChi(1);
        if (h.crit) this.reduce('fists', 4);
        result.dawnCrit = h.crit;
        result.crits += Number(h.crit);
      }
      if (!wind) this.triggerDragon();
      const fistsAfter = this.remaining('fists');
      this.emit('sunResult', dawn ? `旭日${result.crits}次暴击 · 怒雷还剩 ${fistsAfter.toFixed(1)} 秒` : `旭日${result.crits}次暴击 · 未触发晨晖`,
        { ...result, fistsAfter, reductionSeconds: fistsBefore - fistsAfter, ready: fistsAfter <= EPS, state: this.snapshot() });
    } else if (id === 'fists') {
      this.totals.fists++;
      if (this.green()) this.totals.jadeFists++;
      const opportunity = this.fistsOpportunities.findLast(o => o.cycle === this.fistsCycle);
      if (opportunity) {
        opportunity.actualAt = this.time;
        opportunity.delay = opportunity.referenceAt == null ? null : this.time - opportunity.referenceAt;
      }
      this.fistsCycle++;
      const channelId = ++this.serial;
      const hasteSnapshot = this.haste();
      const interval = () => Math.round(1000 / hasteSnapshot * 0.5 ** this.jadeCount()) / 1000;
      const duration = 4 * interval();
      this.channel = { id: channelId, skill: id, start: this.time, end: this.time + duration, ticks: 0 };
      const data = { combo, castId, hasteSnapshot, endAt: this.time + duration };
      this.fistsPulse(data, channelId, true);
      this.fistsPulse(data, channelId);
      this.scheduleFists(data, channelId);
      this.triggerDragon();
    } else if (id === 'crane') {
      const channelId = ++this.serial;
      const duration = 3 * Math.round(500 / this.haste()) / 1000;
      this.channel = { id: channelId, skill: id, start: this.time, end: this.time + duration, ticks: 0 };
      this.later(duration, 'channelEnd', {}, channelId);
      const multiplier = 1 + this.rhythm * 0.2;
      this.rhythm = 0;
      this.endBuff('rhythm');
      if (hadDance) { this.dance = Math.max(0, this.dance - 1); this.proc('combo'); }
      const interval = Math.max(0.05, 1.5 / this.haste() / 4 - 0.1);
      for (let i = 0; i < 4; i++) this.later(interval * i, 'hit',
        { skill: id, reference: d.crane.reference, multiplier, options: { aoe: true, combo, castId } });
      this.later(1.5, 'craneExpire', {});
    } else if (id === 'dragon') {
      hit(id, d.dragonSingle.reference);
      for (let i = 0; i < 3; i++) this.later(i * 0.25, 'hit',
        { skill: id, reference: d.dragonAoe.reference, multiplier: 1, options: { aoe: true, combo, castId } });
      this.setBuff('jade', 6);
      this.proc('dance');
    } else if (id === 'tiger') {
      this.setBuff('tiger', 20);
      this.setBuff('conduitReady', 60);
    } else if (id === 'zenith') {
      const previous = this.zenithRecharge.at(-1) || this.time;
      this.zenithRecharge.push(Math.max(this.time, previous) + 90);
      this.zenithLock = this.time + 16;
      this.zenithCrit = Math.min(20, this.brew) * 0.01;
      this.brew -= Math.min(20, this.brew);
      this.setBuff('zenith', 20);
      this.setBuff('avatar', 4);
      this.stomps = 2;
      this.cooldowns.sun = 0;
      this.gainChi(2);
      const stompCombo = this.registerCombo('stomp');
      hit('stomp', d.stompAuto.reference, 1, { aoe: true, combo: stompCombo });
      this.emit('proc', '乾元自动踏：获得真气；乾元青龙开始');
    } else if (id === 'stomp') {
      this.stomps--;
      this.gainChi(2);
      hit(id, d.stomp.reference, 1, { aoe: true });
    } else if (id === 'conduit') {
      this.endBuff('conduitReady');
      const channelId = ++this.serial;
      const duration = 4 / this.haste();
      this.channel = { id: channelId, skill: id, start: this.time, end: this.time + duration, ticks: 0, nextTick: this.time };
      for (let i = 0; i <= 4; i++) this.later(duration * i / 4, 'conduitTick',
        { index: i, interval: duration / 4, combo, castId }, channelId);
    }
    this.advance(0);
    return { ok: true, status: 'executed', castId, attemptId };
  }

  registerCombo(id) {
    this.activeCombo = id !== this.lastSkill;
    if (!this.activeCombo) { this.comboBreaks++; this.emit('warning', '重复技能：本次未获得精通加成'); }
    this.lastSkill = id;
    return this.activeCombo;
  }

  snapshot() {
    return {
      time: this.time, targets: this.options.targets, attackable: this.attackable,
      chi: this.chi, energy: this.energy, rhythm: this.rhythm, gcdRemaining: Math.max(0, this.gcdEnd - this.time),
      dance: this.dance, combo: this.combo, wind: this.buffLeft('wind'),
      jade: this.green(), haste: this.haste(), lastSkill: this.lastSkill,
      buffs: Object.fromEntries(['avatar', 'jade', 'greatJade', 'zenith', 'tiger', 'bloodlust', 'dragonReady', 'combo', 'dance'].map(id => [id, this.buffLeft(id)])),
      cooldowns: Object.fromEntries(['sun', 'wind', 'fists', 'dragon', 'conduit', 'tiger', 'zenith'].map(id => [id, this.remaining(id)])),
      previousAction: this.previousAction, stomps: this.stomps,
      fullRecharge: this.zenithRecharge.length ? this.zenithRecharge.at(-1) - this.time : 0,
      channel: this.channel ? { skill: this.channel.skill, remaining: this.channel.end - this.time, ticks: this.channel.ticks ?? 0,
        cancelEligible: this.channel.cancelEligible ?? false } : null,
      activeWindows: this.windows.filter(w => w.start <= this.time && w.end > this.time + EPS).map(w => w.id),
    };
  }

  cancel(input = { source: 'explicit' }) {
    if (!this.channel) return false;
    const before = this.snapshot();
    const channel = this.channel;
    this.pending = this.pending.filter(e => e.channelId !== channel.id);
    this.channel = null;
    if (channel.skill === 'conduit') {
      this.setBuff('greatJade', 6);
      this.emit('proc', '结束天神通道 → 大青龙');
    } else if (channel.skill === 'fists') {
      this.clippedFists++;
      this.emit('clippedFists', `怒雷提前打断：只完成 ${channel.ticks}/5 次正常脉冲`, { ticks: channel.ticks, startedAt: channel.start });
    }
    const after = this.snapshot();
    this.emit('channelEnd', `${SKILLS[channel.skill].name}通道结束`, { source: input.source, causeSkill: input.skill ?? null, before, after });
    if (input.source !== 'spell') this.controls.push({ actionId: ++this.actionSerial, time: this.time, skill: 'cancel', spell: 'cancel', input: { ...input, at: this.time }, before, after });
    return true;
  }

  observeFists() {
    if (!this.fistsCycle || this.remaining('fists') > EPS) return;
    let o = this.fistsOpportunities.findLast(o => o.cycle === this.fistsCycle);
    if (!o) {
      o = { cycle: this.fistsCycle, cooldownReadyAt: this.time, legalAt: null, referenceAt: null, actualAt: null, delay: null,
        state: this.snapshot(), blockers: [], choices: [] };
      this.fistsOpportunities.push(o);
    }
    if (o.actualAt != null) return;
    const blocker = this.time >= this.options.duration - EPS ? '本轮结束' :
      !this.attackable || this.options.targets <= 0 ? '没有可攻击目标' : this.channel?.skill === 'fists' ? '怒雷引导未结束' :
      this.gcdEnd > this.time + EPS ? '公共冷却' : this.chi < this.costs('fists').chi ? '缺真气' :
      !this.available('fists').ok ? this.available('fists').reason : null;
    if (blocker && !o.blockers.includes(blocker)) o.blockers.push(blocker);
    if (!blocker && o.legalAt == null) o.legalAt = this.time;
    const d = referenceDecision(this);
    if (d.skill === 'fists' && o.referenceAt == null) {
      o.referenceAt = this.time;
      o.reference = d;
      o.referenceState = this.snapshot();
    }
  }

  nextBoundary() {
    const times = [this.gcdEnd, this.zenithLock, this.pending[0]?.at ?? Infinity, ...this.zenithRecharge,
      2, 255, 255.001, 275, 277, 296, 296.001, 300];
    // Strict APL comparisons cross on the next millisecond, consistently across frames.
    for (const at of Object.values(this.buffs)) for (const threshold of [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 13]) times.push(at - threshold, at - threshold + 0.001);
    if (this.zenithRecharge.length) for (const threshold of [0, 2, 5, 30]) {
      times.push(this.zenithRecharge.at(-1) - threshold, this.zenithRecharge.at(-1) - threshold + 0.001);
    }
    for (const id of Object.keys(this.cooldowns)) for (const threshold of [0, 1, 2, 5, 9, 10, 50]) {
      const remaining = this.remaining(id);
      if (remaining > EPS && remaining + 0.001 > threshold + EPS) times.push(this.time + remaining - threshold, this.time + remaining - threshold + 0.001);
    }
    const regen = CALIBRATION.energyRegen * this.haste();
    for (const energy of [40, 50, 55, 150 - 3 * regen]) if (energy > this.energy + EPS) times.push(this.time + (energy - this.energy) / regen);
    return Math.min(this.options.duration, ...times.filter(t => t > this.time + EPS));
  }

  advance(seconds) {
    const end = Math.min(this.options.duration, this.time + Math.max(0, seconds));
    do {
      const nextBuff = Object.values(this.buffs).filter(t => t > this.time + EPS);
      let next = Math.min(end, this.time + 0.025, this.nextBoundary(), this.pending[0]?.at ?? Infinity,
        ...nextBuff, this.zenithRecharge[0] ?? Infinity,
        this.gcdEnd > this.time + EPS ? this.gcdEnd : Infinity,
        this.remaining('fists') > EPS ? this.time + this.remaining('fists') : Infinity);
      if (end - next < EPS) next = end;
      const dt = Math.max(0, next - this.time);
      const haste = this.haste();
      const recovery = this.recovery();
      for (const id of Object.keys(this.cooldowns)) this.cooldowns[id] = Math.max(0, this.cooldowns[id] - dt * (HASTED_CDS.has(id) ? haste : 1) * (CORE_CDS.has(id) ? recovery : 1));
      this.energy = Math.min(150, this.energy + dt * CALIBRATION.energyRegen * haste);
      this.time = next;
      for (const name of ['combo', 'dance', 'rhythm']) if (this[name] && !this.buffLeft(name)) this[name] = 0;
      if (!this.buffLeft('zenith')) this.stomps = 0;
      while (this.zenithRecharge.length && this.zenithRecharge[0] <= this.time + EPS) this.zenithRecharge.shift();
      while (this.pending.length && this.pending[0].at <= this.time + EPS) this.dispatch(this.pending.shift());
      this.observeFists();
      if (this.queue && this.gcdEnd <= this.time + EPS) {
        const skill = this.queue, input = this.queueInput, attemptId = this.queueAttemptId;
        this.queue = null; this.queueInput = null; this.queueAttemptId = null;
        this.cast(skill, input, attemptId);
      }
      if (this.time >= end - EPS) break;
    } while (true);
  }

  recommend() {
    return referenceDecision(this);
  }

  summary() {
    return {
      elapsed: this.time, damage: this.damage, dps: this.damage / Math.max(1, this.time),
      fists: this.totals.fists,
      jadeFists: this.totals.jadeFists,
      jadeCoverage: this.totals.fistsDamage ? this.totals.jadeFistsDamage / this.totals.fistsDamage : 0,
      clippedFists: this.clippedFists, comboBreaks: this.comboBreaks,
      wastedChi: this.wastedChi, droppedProcs: this.droppedProcs,
    };
  }
}
