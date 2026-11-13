export const ACTION_SLOTS = {
  sun: { key: '1', label: '旭日 / 疾风踢' },
  palm: { key: '2', label: '猛虎掌' },
  blackout: { key: '3', label: '幻灭踢' },
  tiger: { key: '4', label: '白虎 / 天神' },
  zenith: { key: '5', label: '乾元 / 乾元镇踏' },
  crane: { key: 'E', label: '神鹤引项踢' },
  fists: { key: 'F', label: '怒雷破' },
  dragon: { key: 'G', label: '升龙霸' },
};

export function slotAction(combat, slot) {
  if (slot === 'tiger' && (combat.buffLeft('conduitReady') || combat.channel?.skill === 'conduit')) return 'conduit';
  if (slot === 'zenith' && combat.stomps > 0 && combat.buffLeft('zenith')) return 'stomp';
  return slot;
}

export function slotSpell(combat, slot) {
  const action = slotAction(combat, slot);
  return action === 'sun' && combat.buffLeft('wind') ? 'wind' : action;
}
