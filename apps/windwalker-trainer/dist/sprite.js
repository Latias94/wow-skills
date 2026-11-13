import { SPRITE_ART } from "./sprite-data.js";

const CHANNEL_ACTIONS = new Set(["fists", "crane", "conduit"]);
const ACTION_NAMES = {
  idle: "凝神待势",
  palm: "猛虎掌",
  blackout: "幻灭踢",
  sun: "旭日东升踢",
  wind: "疾风呼啸踢",
  fists: "怒雷破",
  crane: "神鹤引项踢",
  dragon: "升龙霸",
  tiger: "召唤白虎",
  conduit: "天神御身",
  zenith: "乾元之巅",
  stomp: "乾元镇踏",
};
const BUFF_ART = [
  ["jade", "jade", "升龙青龙"],
  ["greatJade", "greaterJade", "天神大青龙"],
  ["avatar", "jade", "乾元青龙"],
  ["zenith", "zenith", "乾元之巅"],
  ["bloodlust", "bloodlust", "嗜血"],
  ["xuen", "tiger", "白虎雪怒"],
];
const stageElements = new WeakMap();
const sheetAssets = new Map();
const paintTargets = new WeakMap();

function loadSheet(src) {
  if (sheetAssets.has(src)) return sheetAssets.get(src);
  const image = new Image();
  image.decoding = "async";
  const asset = { image, status: "loading" };
  asset.promise = new Promise((resolve) => {
    const finish = (ready) => {
      if (asset.status !== "loading") return;
      asset.status = ready ? "ready" : "failed";
      image.onload = image.onerror = null;
      resolve(ready);
    };
    image.onload = () => {
      Promise.resolve(image.decode?.()).then(
        () => finish(true),
        () => finish(false),
      );
    };
    image.onerror = () => finish(false);
  });
  sheetAssets.set(src, asset);
  image.src = src;
  return asset;
}

function sheetTiming(sheet) {
  const cols = Math.max(1, sheet?.cols || 1);
  const rows = Math.max(1, sheet?.rows || 1);
  const frames = Math.max(1, Math.min(sheet?.frames || cols * rows, cols * rows));
  const durations = sheet?.durationsMs?.slice(0, frames);
  const hasDurations =
    durations?.length === frames &&
    durations.every((duration) => Number.isFinite(duration) && duration > 0);
  const durationMs = hasDurations
    ? durations.reduce((sum, duration) => sum + duration, 0)
    : Math.max(1, (sheet?.duration || 0.72) * 1000);
  return {
    cols,
    rows,
    frames,
    durations: hasDurations ? durations : null,
    durationMs,
  };
}

function sampleSheet(sheet, elapsed, reducedMotion, loop = sheet?.loop) {
  if (!sheet?.src) return null;
  const { cols, rows, frames, durations, durationMs } = sheetTiming(sheet);
  let frame = Math.min(
    frames - 1,
    Math.max(0, sheet.posterFrame ?? Math.floor((frames - 1) / 2)),
  );
  if (!reducedMotion) {
    const elapsedMs = Math.max(0, elapsed * 1000);
    const phaseMs = loop
      ? elapsedMs % durationMs
      : Math.min(durationMs, elapsedMs);
    frame = frames - 1;
    if (durations) {
      let boundary = 0;
      for (let index = 0; index < frames; index++) {
        boundary += durations[index];
        if (phaseMs + 0.000001 < boundary) {
          frame = index;
          break;
        }
      }
    } else {
      frame = Math.min(frames - 1, Math.floor((phaseMs / durationMs) * frames));
    }
  }
  return { src: sheet.src, cols, rows, frame };
}

function actionFor(event) {
  return event?.spell || event?.skill;
}

function poseDuration(sheet) {
  return sheet?.duration > 0
    ? sheet.duration
    : sheetTiming(sheet).durationMs / 1000;
}

export function resolveSpriteState(
  combat,
  art = SPRITE_ART,
  reducedMotion = false,
) {
  const time = combat.time;
  const casts = combat.casts || [];
  const hits = combat.hits || [];
  const character = art.character || {};
  const effectArt = art.effects || {};
  const cast = casts.findLast((entry) => entry.time <= time);
  const channel =
    combat.channel?.start <= time && time < combat.channel.end
      ? combat.channel
      : null;
  let action = "idle";
  let startedAt = 0;
  if (channel) {
    action = channel.skill;
    startedAt = channel.start;
    if (
      action === "crane" &&
      cast?.time >= channel.start &&
      !CHANNEL_ACTIONS.has(actionFor(cast)) &&
      time - cast.time < poseDuration(character[actionFor(cast)])
    ) {
      action = actionFor(cast);
      startedAt = cast.time;
    }
  } else if (
    cast &&
    !CHANNEL_ACTIONS.has(actionFor(cast)) &&
    time - cast.time < poseDuration(character[actionFor(cast)])
  ) {
    action = actionFor(cast);
    startedAt = cast.time;
  }

  const effects = [];
  const addEffect = (layer, key, start, loop, label) => {
    effects.push({
      layer,
      action: key,
      label,
      sheet: sampleSheet(effectArt[key], time - start, reducedMotion, loop),
    });
  };

  if (channel && channel.skill !== "crane") {
    addEffect(
      `channel:${channel.skill}`,
      channel.skill,
      channel.start,
      effectArt[channel.skill]?.loop ?? true,
      ACTION_NAMES[channel.skill],
    );
  }

  // SCK's independent hits survive a body weave and even an explicit channel cancel.
  const craneCast = casts.findLast(
    (entry) => entry.time <= time && actionFor(entry) === "crane",
  );
  const craneHit = hits.findLast(
    (entry) => entry.time <= time && entry.skill === "crane",
  );
  const pendingCrane = combat.pending?.find(
    (entry) =>
      entry.at >= time &&
      entry.type === "hit" &&
      entry.data.skill === "crane" &&
      (!craneCast || entry.data.options?.castId === craneCast.castId),
  );
  const craneTail =
    craneHit &&
    time - craneHit.time < sheetTiming(effectArt.crane).durationMs / 1000;
  if (channel?.skill === "crane" || pendingCrane || craneTail) {
    addEffect(
      "channel:crane",
      "crane",
      channel?.skill === "crane"
        ? channel.start
        : craneCast?.time ?? craneHit?.time ?? time,
      true,
      "神鹤独立伤害",
    );
  }

  for (const key of Object.keys(ACTION_NAMES)) {
    if (key === "idle" || key === "tiger" || CHANNEL_ACTIONS.has(key)) continue;
    const latestCast = casts.findLast(
      (entry) => entry.time <= time && actionFor(entry) === key,
    );
    const latestHit = hits.findLast(
      (entry) => entry.time <= time && actionFor(entry) === key,
    );
    const start = Math.max(
      latestCast?.time ?? -Infinity,
      latestHit?.time ?? -Infinity,
    );
    if (time - start < sheetTiming(effectArt[key]).durationMs / 1000) {
      addEffect(`cast:${key}`, key, start, false, ACTION_NAMES[key]);
    }
  }

  const buffs = [];
  for (const [buff, key, label] of BUFF_ART) {
    // Older combat states name the summon buff "tiger". An explicit xuen lifetime wins.
    const sourceBuff =
      buff === "xuen" && combat.buffs?.xuen == null ? "tiger" : buff;
    if (!(combat.buffLeft?.(sourceBuff) > 0)) continue;
    const window = combat.windows?.findLast(
      (entry) =>
        entry.name === sourceBuff && entry.start <= time && time < entry.end,
    );
    const start =
      window?.start ??
      (buff === "xuen"
        ? casts.findLast(
            (entry) => entry.time <= time && actionFor(entry) === "tiger",
          )?.time
        : null) ??
      0;
    const sheet = effectArt[key] || (key === "greaterJade" ? effectArt.jade : null);
    const effect = {
      layer: `buff:${buff}`,
      action: key,
      label,
      sheet: sampleSheet(sheet, time - start, reducedMotion, true),
    };
    effects.push(effect);
    buffs.push(label);
  }

  const labels = [ACTION_NAMES[action] || "凝神待势"];
  if (
    effects.some((effect) => effect.layer === "channel:crane") &&
    action !== "crane"
  ) {
    labels.push("神鹤独立伤害");
  }
  labels.push(...buffs);
  return {
    action,
    body: sampleSheet(
      character[action] || character.idle,
      time - startedAt,
      reducedMotion,
    ),
    effects,
    label: labels.join(" · "),
    scene: art.scene || {},
  };
}

function paintSheet(element, sheet) {
  let target = paintTargets.get(element);
  if (!target) {
    target = { sheet: null, waitingFor: null };
    paintTargets.set(element, target);
  }
  target.sheet = sheet;
  if (!sheet) {
    target.waitingFor = null;
    element.hidden = true;
    return;
  }
  const asset = loadSheet(sheet.src);
  if (asset.status !== "ready") {
    // Keep the last decoded pose painted while a replacement loads or fails.
    if (asset.status === "loading" && target.waitingFor !== sheet.src) {
      const src = sheet.src;
      target.waitingFor = src;
      asset.promise.then((ready) => {
        if (target.waitingFor !== src) return;
        target.waitingFor = null;
        // Read the latest frame; a canceled effect or reset must stay canceled.
        if (ready && target.sheet?.src === src) paintSheet(element, target.sheet);
      });
    }
    return;
  }
  target.waitingFor = null;
  element.hidden = false;
  const signature = `${sheet.src}|${sheet.cols}|${sheet.rows}`;
  if (element.dataset.sheet !== signature) {
    element.dataset.sheet = signature;
    element.style.backgroundImage = `url(${JSON.stringify(sheet.src)})`;
    element.style.backgroundSize = `${sheet.cols * 100}% ${sheet.rows * 100}%`;
  }
  const x =
    sheet.cols > 1
      ? ((sheet.frame % sheet.cols) / (sheet.cols - 1)) * 100
      : 0;
  const y =
    sheet.rows > 1
      ? (Math.floor(sheet.frame / sheet.cols) / (sheet.rows - 1)) * 100
      : 0;
  const position = `${x}% ${y}%`;
  if (element.style.backgroundPosition !== position) {
    element.style.backgroundPosition = position;
  }
}

export function renderSprite(
  stage,
  combat,
  reducedMotion = false,
  art = SPRITE_ART,
) {
  let elements = stageElements.get(stage);
  if (!elements) {
    elements = {
      body: stage.querySelector("#monk-sprite"),
      layers: [...stage.querySelectorAll("[data-sprite-layer]")],
      scenes: [...stage.querySelectorAll("[data-sprite-scene]")],
      status: stage.querySelector("#sprite-status"),
    };
    stageElements.set(stage, elements);
    for (const sheet of [
      ...Object.values(art.character || {}),
      ...Object.values(art.effects || {}),
    ]) {
      if (sheet?.src) loadSheet(sheet.src);
    }
  }
  const state = resolveSpriteState(combat, art, reducedMotion);
  paintSheet(elements.body, state.body);
  if (elements.body.dataset.action !== state.action) {
    elements.body.dataset.action = state.action;
  }
  const description = `熊猫武僧练习插画 · ${state.label}`;
  if (elements.body.getAttribute("aria-label") !== description) {
    elements.body.setAttribute("aria-label", description);
  }
  const active = new Map(state.effects.map((effect) => [effect.layer, effect]));
  for (const element of elements.layers) {
    const effect = active.get(element.dataset.spriteLayer);
    paintSheet(element, effect?.sheet);
    const fallback = Boolean(
      effect &&
      !effect.sheet &&
      effect.layer !== "buff:xuen" &&
      effect.layer.startsWith("buff:"),
    );
    if (element.dataset.fallback !== String(fallback)) {
      element.dataset.fallback = String(fallback);
    }
    if (fallback) element.hidden = false;
  }
  for (const element of elements.scenes) {
    const src = state.scene[element.dataset.spriteScene];
    if (src && element.getAttribute("src") !== src) {
      element.setAttribute("src", src);
    }
    if (element.hidden !== !src) element.hidden = !src;
  }
  if (elements.status.textContent !== state.label) {
    elements.status.textContent = state.label;
  }
}
