import { CALIBRATION } from './calibration.js';

export const POLICY = {
  revision: '73a372b76188c703e48729caded3258cdc5b726b',
  source: 'engine/class_modules/apl/apl_monk.cpp',
  scope: '沙僧固定天赋、核心技能、300秒木桩的APL投影；不含饰品、药水、种族、轮回之触与宠物决策。',
};
const EPS = 1e-7;
const decisionTime = n => n <= EPS ? 0 : Math.ceil((n - EPS) * 1000) / 1000;
const decision = (skill, line, rule, text, extra = {}) => ({ skill, line, rule, text, ...extra });

// Explicit projection for this build, in source order. No random roll is read here.
export function referenceDecision(c) {
  if (c.time >= c.options.duration - EPS) return decision(null, 0, 'session-end', '本轮已结束。', { wait: 0 });
  if (!c.attackable || c.options.targets <= 0) return decision(null, 0, 'no-target', '当前没有可攻击目标，等待遭遇状态变化。', {
    blocker: 'no-target', wait: c.nextBoundary() - c.time,
  });
  if (c.channel?.skill === 'fists') return decision(null, 0, 'protect-fists', '继续打满怒雷，等待最后一次脉冲。', {
    blocker: 'fists-channel', wait: Math.max(0, c.channel.end - c.time),
  });
  const up = name => c.buffLeft(name) > EPS;
  const left = name => decisionTime(c.buffLeft(name));
  const cd = id => decisionTime(c.remaining(id));
  const ready = id => {
    // Zero own GCD does not opt this APL line into use_off_gcd.
    if (id === 'zenith' && c.gcdEnd > c.time + EPS) return false;
    if (c.channel?.skill === 'crane' && !['palm', 'sun', 'blackout', 'dragon', 'tiger', 'stomp'].includes(id)) return false;
    return id === 'wind' ? up('wind') && c.available('sun').ok :
      id === 'sun' ? !up('wind') && c.available('sun').ok : c.available(id).ok;
  };
  const combo = id => c.lastSkill !== (id === 'sun' && up('wind') ? 'wind' : id);
  const chi = c.chi, zen = up('zenith'), lust = up('bloodlust'), multi = c.options.targets > 1;
  const fullRecharge = c.zenithRecharge.length ? decisionTime(c.zenithRecharge.at(-1) - c.time) : 0;
  const timeToMax = (150 - c.energy) / (CALIBRATION.energyRegen * c.haste());
  const remains = Math.max(0, 300 - c.time);
  const take = (skill, condition, line, rule, text) => condition && ready(skill) ? decision(skill === 'wind' ? 'sun' : skill, line, rule, text, { action: skill }) : null;
  let d;
  if (c.time < 2 && (d = take('palm', combo('palm') && chi < 4, 210, 'opener-palm', '起手先用猛虎补到4气，再召白虎。'))) return d;
  if (c.channel?.skill === 'conduit') {
    // cancel_if is latched by a nonzero timed tick, independent of the GCD.
    if (c.channel.cancelEligible) return decision('cancel', 232, 'conduit-cancel', '天神已到取消检查点，结束通道获得大青龙。');
    if ((d = take('stomp', combo('stomp') && chi < 5 && c.previousAction === 'conduit', 229, 'conduit-stomp', '天神引导内用镇踏补气，保留通道。'))) return d;
    return decision(null, 232, 'conduit-tick', '等待天神下一次伤害脉冲检查取消条件。', { blocker: 'conduit-channel', wait: c.channel.nextTick - c.time });
  }
  if ((d = take('tiger', remains > 25 && (cd('zenith') < EPS || left('zenith') > 13) &&
    !up('jade') && (chi > 2 || chi > 1 && c.energy < 40), 226, 'coc-tiger', '白虎与乾元对齐，已有足够真气。'))) return d;
  if ((d = take('tiger', remains <= 25, 228, 'coc-tail-tiger', '木桩最后25秒内使用白虎。'))) return d;
  if ((d = take('stomp', combo('stomp') && c.previousAction === 'conduit' && chi < 5, 229, 'coc-after-conduit-stomp', '天神之后用镇踏补气。'))) return d;
  if ((d = take('stomp', combo('stomp') && (chi < 2 || left('zenith') < 2), 230, 'coc-stomp', '镇踏补到核心技能所需真气，或在乾元结束前消费。'))) return d;
  const conduit = !up('jade') && !up('avatar') && (!up('dragonReady') || cd('dragon') > EPS) ||
    remains < 4 || c.options.targets > 2 && lust;
  if ((d = take('conduit', zen && conduit || remains < 4 || c.options.targets > 2 && lust, 232, 'coc-conduit', '按青龙、嗜血或战斗尾段条件衔接天神。'))) return d;
  if ((d = take('zenith', left('tiger') > 10 && !zen, 236, 'zenith-tiger', '白虎剩余超过10秒且乾元未激活，开启乾元。'))) return d;
  if ((d = take('zenith', left('bloodlust') > 10 && (multi && c.options.targets > 2 || cd('sun') > EPS || up('wind')) &&
    (!zen || !cd('fists') && !up('jade') && !up('greatJade')), 237, 'zenith-lust', '嗜血期间满足第二乾元窗口条件；重置旭日并补气。'))) return d;
  if ((d = take('zenith', remains > 25 && lust && cd('conduit') > EPS && (cd('sun') > EPS || c.options.targets > 2) && !zen,
    238, 'zenith-after-conduit', '嗜血内天神已进入冷却，开启下一轮乾元。'))) return d;
  if ((d = take('zenith', !zen && cd('fists') < 10 &&
    (cd('sun') > EPS || chi < 2 && c.energy < 50 || multi) && fullRecharge < 30 &&
    (remains > 120 || remains < 50 && remains > fullRecharge), 248, 'zenith-recharge', '木桩常规乾元：核心冷却接近且充能将满。'))) return d;
  if ((d = take('zenith', remains <= 23 && (cd('sun') > EPS || c.options.targets > 2), 249, 'zenith-tail', '木桩尾段使用乾元。'))) return d;
  if ((d = take('zenith', remains < 45 && fullRecharge < 5 && (cd('sun') > EPS || multi), 250, 'zenith-tail-charge', '木桩尾段乾元接近满充能。'))) return d;
  if (!multi) {
    if ((d = take('dragon', left('greatJade') < 2 && (!cd('sun') || !cd('fists')) && c.dance < 2 && cd('tiger') > 9, 262, 'st-grace-dragon', '升龙宽限仍在，即使一个核心冷却已转好也可先建青龙。'))) return d;
    if ((d = take('conduit', conduit, 263, 'st-conduit', '单体列表：当前无普通及乾元青龙，开启天神。'))) return d;
    if ((d = take('fists', ['jade', 'greatJade', 'avatar'].some(n => up(n) && left(n) < 1), 265, 'st-last-jade', '青龙即将结束，优先让怒雷在窗口内起手。'))) return d;
    if ((d = take('palm', combo('palm') && !zen && chi < 5 && timeToMax <= 3 && (!lust || chi < 1) && c.combo < 2, 266, 'st-energy-cap', '平稳期防能量溢出，先猛虎掌。'))) return d;
    if ((d = take('fists', fullRecharge > 2, 268, 'st-fists', '怒雷就绪且乾元全充能不在2秒内，优先怒雷。'))) return d;
    if ((d = take('dragon', left('greatJade') < 1 && c.dance < 2 && cd('tiger') > 9, 270, 'st-dragon', '升龙可用，建立小青龙并获得赤精。'))) return d;
    if ((d = take('blackout', combo('blackout') && !zen && chi < 2 && c.combo && !cd('fists'), 271, 'st-fists-proc-chi', '怒雷缺气，先用高亮幻灭回气。'))) return d;
    if ((d = take('palm', combo('palm') && chi < 2 && !cd('fists') && (!c.combo || chi < 1), 272, 'st-fists-chi', '怒雷已好但缺气，先猛虎掌。'))) return d;
    if ((d = take('blackout', combo('blackout') && !zen && chi < 2 && c.combo && !cd('sun'), 273, 'st-sun-proc-chi', '旭日缺气，用高亮幻灭回气。'))) return d;
    if ((d = take('wind', up('wind'), 274, 'st-wind', '单体优先疾风呼啸踢；旭日槽替换，并消费套装。'))) return d;
    if ((d = take('crane', combo('crane') && c.dance && c.rhythm && c.combo < 2, 275, 'st-dance-tier', '套装与赤精同时存在，优先神鹤。'))) return d;
    if ((d = take('sun', combo('sun') && !cd('dragon') && (!c.dance || !c.rhythm), 276, 'st-unlock-dragon', '旭日解锁已转好的升龙。'))) return d;
    if ((d = take('sun', combo('sun') && lust && !c.dance, 278, 'st-lust-sun', '嗜血期间无赤精，优先旭日减冷却。'))) return d;
    if ((d = take('blackout', combo('blackout') && c.combo > 1 && left('combo') < 8, 279, 'st-expiring-combo', '高亮幻灭双层且即将到期，先消费。'))) return d;
    if ((d = take('crane', combo('crane') && (c.dance && c.rhythm || c.dance && left('dance') < 5 && c.combo < 2), 280, 'st-expiring-dance', '消费套装或即将到期的赤精。'))) return d;
    if ((d = take('crane', combo('crane') && c.rhythm, 281, 'st-tier', '单体当前构筑：先消费怒雷的套装层数。'))) return d;
    if ((d = take('sun', combo('sun'), 282, 'st-sun', '旭日伤害与怒雷减冷却；命中后重读分支。'))) return d;
    if ((d = take('blackout', combo('blackout') && c.combo === 2, 283, 'st-double-combo', '双层高亮幻灭先消费。'))) return d;
    if ((d = take('blackout', combo('blackout') && zen && cd('sun') > EPS && cd('fists') > EPS && c.combo, 284, 'st-zen-combo', '乾元中消费高亮幻灭，推动核心冷却。'))) return d;
    if ((d = take('crane', combo('crane') && c.dance === 2 && c.combo < 2, 285, 'st-double-dance', '双层赤精防溢出。'))) return d;
    if ((d = take('crane', combo('crane') && zen && (c.dance && c.combo < 2 || chi > 4), 286, 'st-zen-crane', '乾元中消费赤精或多余真气。'))) return d;
    if ((d = take('palm', combo('palm') && chi < 2, 289, 'st-chi', '猛虎掌补气。'))) return d;
    if ((d = take('blackout', combo('blackout') && c.combo, 290, 'st-combo', '消费高亮幻灭。'))) return d;
    if ((d = take('crane', combo('crane') && c.dance, 291, 'st-dance', '消费赤精。'))) return d;
    if ((d = take('crane', combo('crane') && !zen && chi > 3, 292, 'st-spend', '平稳期真气充裕，用神鹤消耗。'))) return d;
    if ((d = take('blackout', combo('blackout') && zen && chi > 3, 293, 'st-zen-spend', '乾元中真气充裕，普通幻灭作为低位填充。'))) return d;
    if ((d = take('palm', combo('palm') && chi < 5, 294, 'st-palm', '平稳期猛虎掌补气，保留连击。'))) return d;
  } else {
    if ((d = take('fists', up('jade') && left('jade') < 1, 297, 'aoe-last-jade', '小青龙即将结束，怒雷优先。'))) return d;
    if ((d = take('dragon', left('greatJade') < 2 && c.dance < 2 && cd('tiger') > 9, 299, 'aoe-dragon', '群体升龙优先建立青龙。'))) return d;
    if ((d = take('fists', true, 300, 'aoe-fists', '群体怒雷可用，优先完整引导。'))) return d;
    if ((d = take('stomp', combo('stomp') && (c.stomps === 2 || cd('conduit') > 50) &&
      (chi < 5 && !up('greatJade') || left('zenith') < 5 && c.stomps === 2 || left('zenith') < 4 || chi < 3) &&
      (cd('dragon') > EPS || chi < 2), 301, 'aoe-stomp', '群体镇踏补气，保留升龙衔接。'))) return d;
    if ((d = take('crane', combo('crane') && c.dance && c.combo < 2 && left('dance') < 3, 302, 'aoe-expiring-dance', '赤精即将到期，消费并获得高亮。'))) return d;
    if ((d = take('palm', combo('palm') && chi < 2 - Number(zen) && (up('jade') || up('greatJade')) && !cd('fists'), 303, 'aoe-fists-chi', '青龙内怒雷缺气，猛虎掌补气。'))) return d;
    if ((d = take('sun', combo('sun') && cd('dragon') < 2 && cd('fists') > EPS && !c.rhythm && !up('dragonReady'), 305, 'aoe-unlock-dragon', '群体无套装，旭日解锁升龙。'))) return d;
    if ((d = take('palm', combo('palm') && (chi < 5 && timeToMax <= 3 && !zen && !lust ||
      chi < 3 - Number(zen) && !cd('fists') && !c.combo && !c.stomps), 307, 'aoe-palm', '防能量溢出或为怒雷补气。'))) return d;
    if ((d = take('crane', combo('crane') && c.rhythm, 308, 'aoe-tier', '群体优先套装神鹤，再考虑疾风。'))) return d;
    if ((d = take('wind', up('wind') && !c.rhythm, 309, 'aoe-wind', '无套装层数时使用疾风呼啸踢。'))) return d;
    if ((d = take('stomp', combo('stomp') && zen && chi < 5 && (chi < 3 || left('zenith') < 5) && (c.stomps === 2 || cd('conduit') > 50) && (cd('dragon') > EPS || chi < 2), 310, 'aoe-late-stomp', '群体乾元后段镇踏补气。'))) return d;
    if ((d = take('dragon', c.dance < 2 && cd('tiger') > 9 && (zen || cd('zenith') > 5 && left('greatJade') < 2), 312, 'aoe-late-dragon', '群体列表后段升龙。'))) return d;
    if ((d = take('crane', combo('crane') && c.dance === 2 && c.combo < 2, 313, 'aoe-double-dance', '双层赤精先消费。'))) return d;
    if ((d = take('crane', combo('crane') && zen && chi > 1, 315, 'aoe-zen-crane', '乾元群体神鹤填充。'))) return d;
    if ((d = take('sun', combo('sun') && !c.rhythm && cd('fists') > EPS && (cd('dragon') < 5 || zen || lust), 316, 'aoe-sun', '群体旭日推动下一次怒雷或升龙。'))) return d;
    if ((d = take('blackout', combo('blackout') && zen && chi > 1 && chi < 6 && c.combo && cd('sun') > EPS, 317, 'aoe-combo', '群体乾元高亮幻灭填充。'))) return d;
    if ((d = take('crane', combo('crane') && cd('fists') > EPS, 321, 'aoe-crane', '怒雷冷却中，用神鹤填充和减冷却。'))) return d;
    if ((d = take('blackout', combo('blackout') && c.combo, 322, 'aoe-blackout', '消费高亮幻灭。'))) return d;
    if ((d = take('palm', combo('palm') && (!zen && !c.combo && (6 - chi >= 2 || !cd('fists') && chi < 3) || chi === 0), 323, 'aoe-palm-fallback', '群体补气。'))) return d;
    if ((d = take('sun', combo('sun'), 325, 'aoe-sun-fallback', '群体列表末位旭日。'))) return d;
  }
  if ((d = take('blackout', combo('blackout'), 328, 'fallback', 'APL最后回退：普通幻灭，保留连击。'))) return d;
  if ((d = take('palm', combo('palm'), 330, 'fallback-palm', 'APL最后回退：猛虎掌。'))) return d;
  if (c.gcdEnd > c.time + EPS) return decision(null, 0, 'gcd', `公共冷却还剩 ${(c.gcdEnd - c.time).toFixed(2)} 秒；不计为晚接怒雷。`, { blocker: 'gcd', wait: c.gcdEnd - c.time });
  if (c.channel?.skill === 'crane') return decision(null, 0, 'crane-channel', '等待神鹤通道结束；共存白名单技能以外暂不可用。', { blocker: 'crane-channel', wait: c.channel.end - c.time });
  return decision(null, 330, 'wait', '等待资源、冷却或下一个状态变化。', { blocker: 'resources', wait: 0.05 });
}
