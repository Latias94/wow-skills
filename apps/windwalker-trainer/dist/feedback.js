export function critFeedback(event) {
  const count = event.crits;
  const before = event.fistsBefore ?? event.state?.cooldowns.fists ?? 0;
  const after = event.fistsAfter ?? event.state?.cooldowns.fists ?? 0;
  const reduction = event.reductionSeconds ?? Math.max(0, before - after);
  return {
    label: ["未暴", "单暴", "双暴"][count] || "命中",
    count,
    parts: [
      {
        label: event.wind ? "疾风本体" : "旭日本体",
        crit: event.mainCrit ?? null,
      },
      {
        label: event.dawn ? "晨晖" : "晨晖未触发",
        crit: event.dawn ? (event.dawnCrit ?? null) : null,
      },
    ],
    cooldown: `怒雷 ${before.toFixed(2)} → ${after.toFixed(2)}秒 · 实际减少 ${reduction.toFixed(2)}秒`,
    ready: after < 0.0001,
  };
}

export function channelFeedback(combat) {
  const skill = combat.channel?.skill;
  if (skill === "fists")
    return {
      state: "protected",
      label: "怒雷引导",
      text:
        combat.options.inputMode === "protected"
          ? "怒雷保护中；其他输出键不会误剪断条。Esc / X 主动结束。"
          : "裸键模式；换技能会取消未完成怒雷，丢失后续命中。",
    };
  if (skill === "crane")
    return {
      state: "weave",
      label: "神鹤引导",
      text: `普通旭日、猛虎、幻灭可共存；${combat.options.protectCrane ? "怒雷等待神鹤结束。" : "怒雷可主动替换通道。"}伤害脉冲与1.5秒减冷却分别结算。`,
    };
  if (skill === "conduit")
    return {
      state: "cancel",
      label: "天神引导",
      text: "镇踏可共存；Esc / X 或有效替换结束天神，当前SimC模型立即触发大青龙。",
    };
  return {
    state: "idle",
    label: "当前没有引导",
    text: "先看真气与怒雷冷却，再看青龙能覆盖多久。",
  };
}
