import { Combat, SKILLS } from './combat.js';

export const SCENARIOS = [
  { id: 'burst-single', name: '单体爆发', description: '单目标起手，练习白虎、乾元与完整怒雷的衔接。',
    options: { duration: 45, targets: 1, initialChi: 2, bloodlust: true } },
  { id: 'burst-aoe', name: '群体爆发', description: '五目标起手，观察套装神鹤、疾风槽替换与怒雷优先级。',
    options: { duration: 45, targets: 5, initialChi: 2, bloodlust: true } },
  { id: 'crit-branch', name: '旭日暴击分支', description: '从一次完整怒雷后的合法检查点继续。下一次旭日已声明主段暴击、触发晨晖且晨晖不暴击；之后恢复随机。',
    checkpoint: ['tiger', 'zenith', 'fists'],
    options: { duration: 45, targets: 1, initialChi: 4, bloodlust: true,
      sunOutcomes: [{ mainCrit: true, dawnTriggered: true, dawnCrit: false }] } },
  { id: 'resource', name: '低真气与通道共存', description: '从猛虎、旭日、猛虎、神鹤的实际执行检查点继续，保留神鹤脉冲与公共冷却，练习补气与等待。',
    checkpoint: ['palm', 'sun', 'palm', 'crane'],
    options: { duration: 45, targets: 1, initialChi: 0,
      sunOutcomes: [{ mainCrit: false, dawnTriggered: false, dawnCrit: false }] } },
  { id: 'sustain', name: '120秒持续循环', description: '两分钟单目标练习，观察爆发后资源、充能与多轮怒雷。',
    options: { duration: 120, targets: 1, initialChi: 2, bloodlust: false } },
  { id: 'dungeon-waves', name: '公开波次示例', description: '训练示例，并非具体副本路线：0秒五目标、18秒单目标、25秒不可攻击、30秒恢复五目标。',
    options: { duration: 60, targets: 5, initialChi: 2, encounterEvents: [
      { at: 0, targets: 5, attackable: true }, { at: 18, targets: 1 },
      { at: 25, attackable: false }, { at: 30, targets: 5, attackable: true },
    ] } },
];

function castCheckpointStep(combat, skill) {
  let iterations = 0;
  while (!combat.available(skill).ok && combat.time < combat.options.duration - 1e-7) {
    if (++iterations > 2048) throw new Error('Scenario checkpoint exceeded its setup budget');
    combat.advance(Math.min(combat.options.duration - combat.time,
      Math.max(0.001, combat.nextBoundary() - combat.time)));
  }
  const result = combat.cast(skill, { source: 'scenario-checkpoint' });
  if (!result.ok || result.queued) throw new RangeError(`Scenario options cannot establish the ${skill} checkpoint`);
}

export function buildScenario(id, baseOptions = {}) {
  const preset = SCENARIOS.find(scenario => scenario.id === id);
  if (!preset) throw new RangeError(`Unknown scenario: ${id}`);
  const combat = new Combat({ ...structuredClone(preset.options), ...structuredClone(baseOptions) });
  for (const skill of preset.checkpoint ?? []) {
    if (!SKILLS[skill].offGcd && combat.gcdEnd > combat.time) combat.advance(combat.gcdEnd - combat.time);
    castCheckpointStep(combat, skill);
  }
  if (id === 'crit-branch') {
    combat.advance(Math.max(0, combat.channel?.end - combat.time || 0, combat.gcdEnd - combat.time));
  } else if (id === 'resource') {
    combat.advance(0.2);
  }
  return combat;
}
