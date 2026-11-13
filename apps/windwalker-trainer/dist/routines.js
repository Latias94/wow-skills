function describeCast(c, targets) {
  const b = c.before;
  if (c.skill === 'cancel') return { status: b?.channel?.skill === 'fists' ? 'error' : 'neutral', expected: '主动结束通道',
    note: b?.channel?.skill === 'conduit' ? '明确记录主动断条，随后获得大青龙。' :
      b?.channel?.skill === 'crane' ? '结束神鹤通道；独立伤害脉冲和延迟减冷却仍保留。' : '主动取消怒雷，正常脉冲未完成。' };
  if (!b) return { status: 'neutral', expected: '无施法前快照', note: '旧记录无法逐键判定。' };
  if (b.channel?.skill === 'fists' && c.skill !== 'zenith') return { status: 'error', expected: '打满怒雷', note: '本次施法打断了尚未完成的怒雷。' };
  if (c.combo === false && c.skill !== 'tiger') return { status: 'error', expected: '换一个连击技能', note: '连续相同技能，失去本次精通收益。' };
  if (c.skill === 'sun' && c.spell === 'wind' && targets === 1 && b.rhythm) return { status: 'good', expected: '单体疾风消费套装', note: '疾风消费套装是神鹤的合法替代，不记为漏神鹤。' };
  if (c.skill === 'crane' && b.rhythm) return { status: 'good', expected: '消费套装', note: `使用${b.rhythm}层连绵武律；套装与赤精分别记录。` };
  if (c.skill === 'fists') return { status: c.jade ? 'good' : 'neutral', expected: '安排青龙怒雷', note: c.jade ? '青龙内起手；还需看后续每次伤害是否被覆盖。' : '普通怒雷不是自动错误，可能是开场或尾部冷却分支。' };
  if (c.skill === 'sun' && targets > 1 && b.rhythm) return { status: 'review', expected: '通常先套装神鹤', note: '群体套装由旭日消费；请复查是否为解锁升龙等必要分支。' };
  if (c.skill === 'blackout' && !b.combo && !b.buffs.zenith) return { status: 'review', expected: '平稳期1＋1／高亮消费', note: '乾元外打了普通幻灭；当前构筑通常优先猛虎与旭日／神鹤。' };
  if (b.jade && b.cooldowns.fists < 0.001 && b.chi >= (b.buffs.zenith ? 1 : 2) && !['zenith', 'tiger'].includes(c.skill)) return { status: 'review', expected: '优先复查已就绪怒雷', note: '青龙内怒雷已可用，但插入其他技能；不直接等同于伤害损失。' };
  if (c.skill === 'sun') return { status: 'good', expected: '旭日后重新读冷却', note: '暴击结果记录在下方分支事件；不按预设填充次数判对错。' };
  if (c.skill === 'dragon') return { status: 'good', expected: '建立普通青龙', note: '下一目标是青龙怒雷；不要只看升龙本身打出去了。' };
  if (['palm', 'stomp', 'blackout', 'crane'].includes(c.skill)) return { status: 'neutral', expected: '资源／触发填充', note: '允许灵活穿插，不因不同于图片顺序判错。' };
  return { status: 'neutral', expected: '爆发衔接', note: c.skill === 'conduit' ? '记录通道结束及大青龙起止，检查是否抢占小青龙。' : '按实际窗口继续观察。' };
}

export function reviewRoutine(combat) {
  const rows = [...combat.casts, ...combat.controls].sort((a, b) => a.time - b.time || (a.actionId ?? 0) - (b.actionId ?? 0)).map(c => {
    const result = c.skill === 'sun' ? combat.events.find(e => e.type === 'sunResult' && e.castTime === c.time) : null;
    const reading = describeCast(c, c.before?.targets ?? combat.options.targets);
    const d = c.decision;
    if (d?.line && d.skill && reading.status !== 'error' && c.skill !== 'cancel') {
      const expected = d.action === 'wind' ? '疾风呼啸踢' : { palm: '猛虎掌', tiger: '白虎下凡', zenith: '乾元', conduit: '天神御身',
        fists: '怒雷破', crane: '神鹤引项踢', sun: '旭日东升踢', blackout: '幻灭踢', dragon: '升龙霸', stomp: '乾元镇踏' }[d.skill] || '结束天神';
      reading.expected = `参考下一键：${expected}（APL:${d.line}）`;
      reading.note = `${d.text} ${reading.note}`;
      reading.status = c.skill === d.skill ? 'good' : 'review';
    }
    return { ...c, ...reading, branch: result ? `${['未暴', '单暴', '双暴'][result.crits]}${result.dawn ? '（含晨晖）' : '（无晨晖）'}，结算后怒雷${result.state.cooldowns.fists.toFixed(1)}秒` : null };
  });
  const findings = [];
  for (const e of combat.events) {
    if (e.type === 'clippedFists') findings.push({ kind: 'error', time: e.time, title: '怒雷提前断条', detail: e.text });
    if (e.type === 'resourceWaste') findings.push({ kind: 'error', time: e.time, title: '真气溢出', detail: e.text });
    if (e.type === 'procWaste') findings.push({ kind: 'error', time: e.time, title: '高亮触发溢出', detail: e.text });
  }
  for (const row of rows) {
    if (row.status === 'review') findings.push({ kind: 'review', time: row.time, title: row.expected, detail: row.note });
    if (row.combo === false && row.skill !== 'tiger') findings.push({ kind: 'error', time: row.time, title: '连击重复', detail: row.note });
  }
  for (const w of combat.windows.filter(w => ['avatar', 'jade', 'greatJade'].includes(w.name) && w.end <= combat.time)) {
    if (!combat.casts.some(c => c.skill === 'fists' && c.time >= w.start && c.time < w.end)) findings.push({ kind: 'review', time: w.start, title: '青龙段没有怒雷起手', detail: '可能是提早开启、被替换或冷却未到。需结合该段前后顺序，不把它直接算成损失一条怒雷。' });
  }
  const opportunities = combat.fistsOpportunities.map(o => ({ ...o,
    status: o.actualAt != null ? 'used' : o.referenceAt != null ? 'unspent' : 'blocked',
    observedUntil: combat.time, sinceFirstReference: o.referenceAt == null ? null : (o.actualAt ?? combat.time) - o.referenceAt,
  }));
  return { rows, opportunities, findings: findings.sort((a, b) => a.time - b.time), branches: combat.events.filter(e => e.type === 'sunResult') };
}
