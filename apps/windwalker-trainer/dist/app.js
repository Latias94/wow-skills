import { SKILLS } from "./combat.js";
import { TrainingSession } from "./session.js";
import { renderRoutineMap } from "./routine-view.js";
import { CALIBRATION } from "./calibration.js";
import { SPELL_DATA } from "./skill-data.js";
import { ACTION_SLOTS, slotAction, slotSpell } from "./actionbar.js";
import { POLICY, referenceDecision } from "./policy.js";
import { reviewRoutine } from "./routines.js";
import { SCENARIOS } from "./scenarios.js";
import { critFeedback, channelFeedback } from "./feedback.js";
import { renderSprite } from "./sprite.js";
import { SIMC_SAMPLES } from "./simc-samples.js";

const $ = (id) => document.getElementById(id);
const fmt = (n) =>
  n >= 1e6
    ? `${(n / 1e6).toFixed(2)}m`
    : n >= 1e4
      ? `${(n / 1e4).toFixed(1)}万`
      : Math.round(n).toLocaleString("zh-CN");
const at = (n) => (n == null ? "—" : `${n.toFixed(2)}s`);
const routeReason = (entry) =>
  ({
    "expected-action-executed": "沿当前参考施放",
    "observed-reference-changed": "触发或状态改变，重新衔接",
    "different-action-executed": "采用了不同走法，原参考已保留",
    "action-after-deviation": "偏离后的实际衔接",
  })[entry?.reason] ||
  entry?.reason ||
  "";
const slotFor = (skill) =>
  ({ conduit: "tiger", stomp: "zenith" })[skill] || skill;
const nameFor = (skill) =>
  skill === "cancel"
    ? "主动断条"
    : skill === "dawn"
      ? "晨晖"
      : skill
        ? SPELL_DATA[skill]?.name || SKILLS[skill]?.name || skill
        : "等待";
const keyFor = (skill) =>
  skill === "cancel"
    ? "X"
    : skill
      ? keys[slotFor(skill)]?.toUpperCase() || "—"
      : "·";
const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text != null) node.textContent = text;
  if (className) node.className = className;
  return node;
};
const buffDefs = [
  ["greatJade", "天神大青龙", 6, "#dcc47e"],
  ["jade", "升龙青龙", 6, "#9acbb2"],
  ["avatar", "乾元青龙", 4, "#81b97f"],
  ["zenith", "乾元", 20, "#d9ab6b"],
  ["bloodlust", "嗜血", 40, "#d6937d"],
];
$("reduce-motion").checked = matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;
let keys = Object.fromEntries(
  Object.entries(ACTION_SLOTS).map(([id, s]) => [id, s.key.toLowerCase()]),
);
try {
  const stored = JSON.parse(localStorage.getItem("windwalker-dojo-keys-v2"));
  if (
    stored &&
    Object.keys(stored).length === 8 &&
    Object.keys(keys).every((id) => /^[a-wyz0-9]$/.test(stored[id])) &&
    new Set(Object.values(stored)).size === 8
  )
    keys = stored;
} catch {
  /* Storage is optional. */
}
let session;
let previous = performance.now(),
  seenHits = 0,
  seenSun = 0,
  inputUntil = 0;
let audio,
  recentSignature = "",
  channelSignature = "";

for (const scenario of SCENARIOS)
  $("scenario").append(new Option(scenario.name, scenario.id));
for (let i = 0; i < 6; i++) $("chi-pips").append(el("i"));
for (const [id, label, max, color] of buffDefs) {
  const node = el("div", null, "buff-bar");
  node.id = `buff-${id}`;
  node.style.setProperty("--bar-color", color);
  node.append(el("i"), el("span", label), el("b", "—"));
  $("buff-bars").append(node);
}
for (const [id, slot] of Object.entries(ACTION_SLOTS)) {
  const button = el("button", null, "skill");
  button.dataset.slot = id;
  const icon = el("span", null, "icon"),
    img = el("img");
  img.src = SPELL_DATA[id].iconPath;
  img.alt = "";
  img.width = 42;
  img.height = 42;
  icon.append(img);
  button.append(
    el("kbd", slot.key),
    icon,
    el("span", null, "cooldown"),
    el("span", null, "charge"),
    el("span", null, "queued-mark"),
    el("small", SKILLS[id].name),
  );
  button.addEventListener("click", () =>
    press(id, { source: "click", slot: id }),
  );
  button.addEventListener("pointerenter", (e) => {
    if (e.pointerType !== "touch") showTooltip(id, button);
  });
  button.addEventListener("focus", () => showTooltip(id, button));
  button.addEventListener("pointerleave", hideTooltip);
  button.addEventListener("blur", hideTooltip);
  $("skillbar").append(button);
}
function selectedOptions() {
  const mode = $("crit-mode").value;
  const options = {
    targets: Number($("targets").value),
    duration: Number($("duration").value),
    seed: Number($("seed").value) || 1026,
    bloodlust: $("bloodlust").value === "on",
    inputMode: $("input-mode").value,
    protectCrane: $("protect-crane").checked,
    critMode: ["none", "single", "double"].includes(mode) ? mode : "random",
  };
  if (mode !== "random")
    options.sunOutcomes = Array.from({ length: 200 }, () => ({
      mainCrit: ["single", "double"].includes(mode),
      dawnTriggered: mode !== "no-dawn",
      dawnCrit: ["dawn", "double"].includes(mode),
    }));
  return options;
}
function applyScenarioDefaults() {
  const preset = SCENARIOS.find((s) => s.id === $("scenario").value);
  for (const id of ["targets", "duration"])
    if (preset.options[id] != null) $(id).value = preset.options[id];
  $("bloodlust").value = preset.options.bloodlust ? "on" : "off";
  $("scenario-description").textContent = preset.description;
}
function prepare() {
  if (!session) {
    session = new TrainingSession({
      scenario: $("scenario").value,
      options: selectedOptions(),
    });
    try {
      const worker = new Worker(
        new URL("./planner-worker.js", import.meta.url),
        { type: "module" },
      );
      session.connectPlanner(
        worker,
        () => ({
          mode: $("planner-mode").value,
          horizon: 10,
          samples: 4,
          maxActions: 5,
        }),
        (error) => {
          if (error) notify(error);
          renderPlan();
        },
      );
    } catch {
      session.workerFailed = true;
    }
  } else session.prepare($("scenario").value, selectedOptions());
  resetPresentation();
}
function resetPresentation() {
  seenHits = session.combat.hits.length;
  seenSun = 0;
  channelSignature = "";
  recentSignature = "";
  $("floating-damage").replaceChildren();
  $("impact-label").textContent = "";
  render();
}
function start(demo = false) {
  session.start({
    demo,
    scenario: $("scenario").value,
    options: selectedOptions(),
  });
  previous = performance.now();
  resetPresentation();
  notify(
    demo
      ? "参考演示沿相同拳谱推进；旭日后自动点亮实际分支。"
      : "沿技能路线练习，旭日结果揭晓后看高亮分支。Esc / X 可主动结束通道。",
  );
}
function setPaused(value) {
  session.setPaused(value);
  previous = performance.now();
  render();
}
function finish() {
  session.finish();
  render();
  renderReview();
  openDialog("review-dialog");
}
function notify(text) {
  $("input-message").textContent = text;
  inputUntil = performance.now() + 2600;
}
function announce(text) {
  $("live-announcement").textContent = text;
}
function restoreCheckpoint(id) {
  const cp = session.retry(id);
  if (!cp) {
    notify("该节点已超出本轮保留的100个检查点。");
    return;
  }
  previous = performance.now();
  for (const dialog of document.querySelectorAll("dialog[open]"))
    dialog.close();
  resetPresentation();
  notify(`已恢复 ${cp.time.toFixed(2)}s 的战斗、拳谱位置与分支。空格继续。`);
}
function press(slot, input) {
  const result = session.act(slot, input);
  if (!result.ok) notify(result.reason);
  else {
    const record = session.inputRecords.at(-1);
    notify(
      `${nameFor(record.spell)}${result.queued ? " · 已排队，执行时才推进拳谱" : ""}`,
    );
    const button = document.querySelector(`[data-slot="${slot}"]`);
    button.classList.add("pressed");
    setTimeout(() => button.classList.remove("pressed"), 100);
  }
  render();
}
function cancelInput(source = "click") {
  const ok = session.cancel({ source, key: "X" });
  notify(
    ok
      ? "已主动结束通道；拳谱保留这次操作与后续衔接。"
      : "当前没有可结束的通道，或训练已暂停。",
  );
  render();
}
function activeDecision() {
  return referenceDecision(session.combat);
}
function renderPlan() {
  if (!session) return;
  const hints = $("hints").checked,
    d = activeDecision();
  document.body.classList.toggle("hints-hidden", !hints);
  $("planner-label").textContent = "分支拳谱";
  $("next-key").textContent = hints ? keyFor(d.skill) : "·";
  $("next-skill").textContent = hints
    ? nameFor(d.action === "wind" ? "wind" : d.skill)
    : "自行判断";
  $("coach-text").textContent = hints
    ? d.text
    : "路线提示已隐藏；实际分支与操作仍会保留供复盘。";
  const selected = session.routine.graph.fork?.branches.find(
    (b) => b.id === session.routine.selectedBranchId,
  );
  $("route-status").textContent = selected
    ? `本次路线：${selected.label}`
    : "沿公共段推进 · 旭日结算后点亮分支";
  $("route-detail").textContent = selected
    ? "其他走法保留对照；后续遇到新触发继续更新。"
    : "实线为当前参考；虚线为条件后续。";
  $("alternatives-open").disabled =
    !session.plan || session.planEpoch !== session.epoch;
  renderRoutineMap($("routine-map"), session.routine, {
    keys,
    hints,
    combat: session.combat,
  });
}
function renderChannel() {
  const c = session.combat.channel,
    feedback = channelFeedback(session.combat),
    left = c ? Math.max(0, c.end - session.combat.time) : 0;
  const craneExpiry = session.combat.pending.find(
    (p) => p.type === "craneExpire",
  );
  $("cast-label").textContent = feedback.label;
  $("cast-effect").textContent =
    feedback.text +
    (craneExpiry
      ? ` 神鹤独立减冷却将在 ${Math.max(0, craneExpiry.at - session.combat.time).toFixed(2)}s 后结算。`
      : "");
  $("cast-track").dataset.state = feedback.state;
  $("channel-rule").textContent =
    c?.skill === "fists"
      ? session.combat.options.inputMode === "protected"
        ? "防误断保护"
        : "可被换技能打断"
      : c?.skill === "crane"
        ? "可穿插白名单瞬发"
        : c?.skill === "conduit"
          ? c.cancelEligible
            ? "参考建议：可以结束"
            : "可主动结束获得大青龙"
          : "";
  $("cast-time").textContent = c ? `${left.toFixed(2)}s` : "—";
  $("cast-progress").style.width = c
    ? `${Math.max(0, (c.end - session.combat.time) / (c.end - c.start)) * 100}%`
    : "0%";
  const signature = c
    ? `${c.id}:${session.combat.pending
        .filter((p) => p.channelId === c.id)
        .map((p) => p.at)
        .join()}`
    : "none";
  if (signature !== channelSignature) {
    channelSignature = signature;
    const craneCast =
      c?.skill === "crane"
        ? session.combat.casts.findLast(
            (cast) => cast.skill === "crane" && cast.time === c.start,
          )
        : null;
    const ticks = c
      ? session.combat.pending
          .filter(
            (p) =>
              (p.channelId === c.id &&
                ["fistsTick", "conduitTick"].includes(p.type)) ||
              (craneCast &&
                p.type === "hit" &&
                p.data?.options?.castId === craneCast.castId &&
                p.at <= c.end),
          )
          .map((p) => p.at)
      : [];
    $("cast-ticks").replaceChildren(
      ...ticks.map((time) => {
        const i = el("i");
        i.style.left = `${Math.max(0, Math.min(100, ((c.end - time) / (c.end - c.start)) * 100))}%`;
        return i;
      }),
    );
  }
}
function renderCrit() {
  const result = session.combat.events.findLast((e) => e.type === "sunResult");
  if (result && result.castId !== seenSun) {
    seenSun = result.castId;
    const f = critFeedback(result);
    $("crit-badge").textContent = f.label;
    $("crit-feedback").dataset.count = f.count;
    $("crit-parts").replaceChildren(
      ...f.parts.map((part) =>
        el(
          "span",
          `${part.label}${part.crit === true ? " · 暴击" : part.crit === false ? " · 普通" : ""}`,
          part.crit ? "is-crit" : "",
        ),
      ),
    );
    $("crit-cooldown").textContent = f.cooldown;
    $("crit-feedback").classList.remove("pulse");
    void $("crit-feedback").offsetWidth;
    $("crit-feedback").classList.add("pulse");
    announce(`${f.label}，${f.cooldown}${f.ready ? "，怒雷冷却归零" : ""}`);
    if (f.count) critSound(f.count);
  } else if (!result) {
    $("crit-badge").textContent = "等待旭日";
    $("crit-feedback").dataset.count = "";
    $("crit-parts").replaceChildren(el("span", "本体与晨晖分别判定"));
    $("crit-cooldown").textContent = "暴击后重新读取怒雷冷却";
  }
  const ready = session.combat.remaining("fists") < 1e-7,
    available = session.combat.available("fists");
  $("fists-ready-note").classList.toggle("ready", ready);
  $("fists-ready-note").textContent = ready
    ? available.ok
      ? `${keyFor("fists")} 怒雷 · 现在可用`
      : `怒雷已好 · ${available.reason}`
    : `怒雷 ${session.combat.remaining("fists").toFixed(1)}s`;
}
function renderHits() {
  const hits = session.combat.hits.slice(seenHits);
  seenHits = session.combat.hits.length;
  for (const [index, hit] of hits.entries()) {
    const node = el("div", null, `floating-hit${hit.crit ? " critical" : ""}`);
    node.style.left = `${59 + (index % 3) * 6}%`;
    node.style.top = `${22 + (session.combat.hits.indexOf(hit) % 4) * 12}%`;
    node.append(
      document.createTextNode(fmt(hit.amount)),
      el(
        "small",
        `${nameFor(hit.spell)}${hit.tier ? " · 套装" : ""}${hit.crit ? " 暴击" : ""}`,
      ),
    );
    $("floating-damage").append(node);
    setTimeout(() => node.remove(), 1250);
  }
  while ($("floating-damage").children.length > 16)
    $("floating-damage").firstElementChild.remove();
}
function render() {
  if (!session.combat) return;
  const summary = session.combat.summary(),
    d = activeDecision();
  document.body.classList.toggle("reduced-motion", $("reduce-motion").checked);
  document.body.classList.toggle(
    "training",
    session.running && !session.paused,
  );
  $("start").disabled = session.running;
  $("demo").disabled = session.running;
  $("pause").disabled = !session.running;
  $("finish").disabled = !session.running;
  $("start").textContent = session.finished ? "再练一轮 ↵" : "开始练习 ↵";
  $("pause").textContent = session.paused ? "继续" : "暂停";
  $("clock").textContent = session.combat.time.toFixed(1).padStart(4, "0");
  $("clock-limit").textContent = ` / ${session.combat.options.duration}s`;
  $("phase").textContent =
    (session.demonstration ? "参考演示 · " : "") +
    (session.paused
      ? "已暂停"
      : session.finished
        ? "本轮结束"
        : !session.running
          ? "准备就绪"
          : !session.combat.attackable
            ? "转场 · 无目标"
            : session.combat.buffLeft("zenith")
              ? "乾元爆发期"
              : session.combat.green()
                ? "青龙窗口"
                : "衔接 / 平稳期");
  $("target-label").textContent =
    `${session.combat.options.targets === 1 ? "单体" : `${session.combat.options.targets}目标`}木桩`;
  $("encounter-note").textContent =
    $("scenario").value === "dungeon-waves"
      ? "公开波次：18s单体 · 25s转场 · 30s五目标"
      : "当前天赋固定 · 场景不会自动切换天赋";
  $("fists-count").textContent = summary.fists;
  $("jade-count").textContent = summary.jadeFists;
  $("damage-total").textContent = fmt(session.combat.damage);
  $("energy-fill").style.width = `${(session.combat.energy / 150) * 100}%`;
  $("energy-text").textContent = `${Math.floor(session.combat.energy)} / 150`;
  [...$("chi-pips").children].forEach((node, i) =>
    node.classList.toggle("filled", i < session.combat.chi),
  );
  $("brew").textContent = `虎酒${session.combat.brew}`;
  $("gcd-text").textContent = session.combat.queue
    ? `队列：${nameFor(session.combat.queue)}`
    : session.combat.gcdEnd > session.combat.time
      ? `公共冷却 ${(session.combat.gcdEnd - session.combat.time).toFixed(2)}s`
      : "公共冷却就绪";
  for (const [id, label, max] of buffDefs) {
    const left = session.combat.buffLeft(id),
      node = $(`buff-${id}`);
    node.classList.toggle("active", left > 0);
    node.querySelector("b").textContent = left ? `${left.toFixed(1)}s` : "—";
    node.querySelector("i").style.width = `${Math.min(1, left / max) * 100}%`;
  }
  for (const button of $("skillbar").children) {
    const slot = button.dataset.slot,
      action = slotAction(session.combat, slot),
      spell = slotSpell(session.combat, slot),
      cd = session.combat.remaining(spell),
      source = SPELL_DATA[spell];
    const available = session.combat.available(action),
      proc =
        (slot === "blackout" && session.combat.combo) ||
        (slot === "crane" && session.combat.dance) ||
        (slot === "sun" && session.combat.buffLeft("wind")) ||
        (slot === "dragon" && session.combat.buffLeft("dragonReady"));
    const img = button.querySelector("img");
    if (img.dataset.spell !== spell) {
      img.src = source.iconPath;
      img.dataset.spell = spell;
      button.querySelector("small").textContent = source.name;
    }
    button.querySelector("kbd").textContent = keys[slot].toUpperCase();
    const overlay = button.querySelector(".cooldown");
    overlay.textContent =
      Number.isFinite(cd) && cd > 0.04
        ? cd >= 10
          ? Math.ceil(cd)
          : cd.toFixed(1)
        : "";
    overlay.hidden = !(cd > 0.04 && Number.isFinite(cd));
    button.querySelector(".charge").textContent =
      action === "stomp"
        ? `${session.combat.stomps}踏`
        : action === "zenith"
          ? `${session.combat.charges("zenith")}/2`
          : slot === "blackout" && session.combat.combo
            ? `${session.combat.combo}高亮`
            : slot === "crane" && session.combat.rhythm
              ? `${session.combat.rhythm}律`
              : "";
    button.querySelector(".queued-mark").textContent =
      session.combat.queue === action ? "排队" : "";
    button.classList.toggle("unavailable", !available.ok);
    button.classList.toggle("proc", Boolean(proc));
    button.classList.toggle(
      "recommended",
      $("hints").checked && d.skill === action,
    );
    button.setAttribute(
      "aria-label",
      `${source.name} [${keys[slot].toUpperCase()}]${available.ok ? " 可用" : ` ${available.reason}`}`,
    );
  }
  const signature = session.combat.casts
    .slice(-5)
    .map((c) => c.castId)
    .join();
  if (signature !== recentSignature) {
    recentSignature = signature;
    $("recent-casts").replaceChildren(
      ...session.combat.casts.slice(-5).map((c) => {
        const li = el("li"),
          img = el("img");
        img.src = SPELL_DATA[c.spell].iconPath;
        img.alt = nameFor(c.spell);
        li.title = `${at(c.time)} ${nameFor(c.spell)}`;
        li.append(img, el("small", keyFor(c.skill)));
        return li;
      }),
    );
  }
  $("jade-aura").classList.toggle("active", session.combat.green());
  renderSprite($("arena"), session.combat, $("reduce-motion").checked);
  renderChannel();
  renderCrit();
  renderHits();
  renderPlan();
  const overlay = $("stage-overlay");
  overlay.hidden = session.running && !session.paused;
  if (!overlay.hidden) {
    overlay.querySelector(".overlay-seal").textContent = session.paused
      ? "静"
      : session.finished
        ? "成"
        : "练";
    overlay.querySelector("h1").textContent = session.paused
      ? "停下来，看清下一拳。"
      : session.finished
        ? `本轮 ${summary.fists} 次怒雷`
        : "看清这一拳。";
    overlay.querySelector("p").textContent = session.paused
      ? "冷却、资源与动作均已暂停。"
      : session.finished
        ? "打开复盘，选择判断节点再练。"
        : "下一键、读条与资源，都在手边。";
  }
  if (performance.now() > inputUntil)
    $("input-message").textContent =
      `套装${session.combat.rhythm}/6 · 赤精${session.combat.dance}/2 · 高亮幻灭${session.combat.combo}/2 · ${session.combat.options.inputMode === "protected" ? "保护宏" : "裸键"} · Esc / X 主动断条`;
}
function frame(now) {
  const dt = Math.min(0.1, Math.max(0, (now - previous) / 1000));
  previous = now;
  if (session?.running && !session.paused) {
    session.tick(dt * Number($("speed").value));
    if (session.finished) {
      renderReview();
      openDialog("review-dialog");
    }
    render();
  }
  requestAnimationFrame(frame);
}
function openDialog(id) {
  hideTooltip();
  if (session.running && !session.paused) setPaused(true);
  if (!$(id).open) $(id).showModal();
}
function renderReview() {
  const s = session.combat.summary(),
    review = reviewRoutine(session.combat);
  $("review-summary").replaceChildren(
    ...[
      [`${s.fists} / ${s.jadeFists}`, "怒雷 / 青龙内起手"],
      [`${Math.round(s.jadeCoverage * 100)}%`, "怒雷伤害青龙覆盖"],
      [`${s.clippedFists} / ${s.comboBreaks}`, "提前断怒雷 / 连击重复"],
    ].map(([value, label]) => {
      const article = el("article");
      article.append(el("strong", value), el("span", label));
      return article;
    }),
  );
  $("review-findings").replaceChildren(
    ...review.findings.slice(-35).map((f) => {
      const article = el("article", null, f.kind);
      article.append(
        el("strong", `${at(f.time)} · ${f.title}`),
        el("p", f.detail),
      );
      return article;
    }),
  );
  if (!review.findings.length)
    $("review-findings").append(
      el("p", "未发现规则内需复查项；这不代表已经证明最优。"),
    );
  $("fists-opportunities").replaceChildren(
    ...review.opportunities.map((o) => {
      const tr = el("tr");
      [
        at(o.cooldownReadyAt),
        at(o.legalAt),
        at(o.referenceAt),
        at(o.actualAt),
        o.sinceFirstReference == null
          ? "尚未建议"
          : `${o.sinceFirstReference.toFixed(2)}s${o.actualAt == null ? " · 尚未接" : ""}`,
      ].forEach((value) => tr.append(el("td", value)));
      return tr;
    }),
  );
  const routeHistory = session.routine.history;
  $("review-route-log").replaceChildren(
    ...routeHistory.slice(-60).map((entry) => {
      const action = [...session.combat.casts, ...session.combat.controls].find(
        (a) => a.actionId === entry.actionId,
      );
      const cp = action?.input?.checkpointId;
      const item = el(
        "button",
        `${at(action?.time ?? entry.time)} ${entry.status === "adapted" ? "状态变化" : nameFor(action?.spell || action?.skill)} · ${{ matched: "沿参考", deviation: "走法不同", adapted: "按触发衔接" }[entry.status] || entry.status}`,
        "route-log-item",
      );
      item.dataset.nodeId = entry.nodeId || "";
      item.dataset.status = entry.status;
      item.title = routeReason(entry);
      item.onclick = () => {
        const archived = session.routine.archives.find(
          (a) => (a.graph?.id || a.id) === entry.graphId,
        );
        const runner =
          entry.graphId === session.routine.graph.id
            ? session.routine
            : {
                ...session.routine,
                graph: archived?.graph || archived || session.routine.graph,
                cursorNodeId: entry.nodeId,
                selectedBranchId: entry.branchId || null,
              };
        renderRoutineMap($("review-map"), runner, {
          keys,
          hints: true,
          combat: session.combat,
        });
        if (cp && session.checkpoints.some((c) => c.id === cp))
          notify(`该操作可在下面逐键表中选择“从此重练”。`);
      };
      return item;
    }),
  );
  renderRoutineMap($("review-map"), session.routine, {
    keys,
    hints: true,
    combat: session.combat,
  });
  const rows = review.rows.filter(
    (r) => r.input?.source !== "scenario-checkpoint",
  );
  $("review-rows").replaceChildren(
    ...rows.map((row) => {
      const tr = el("tr"),
        b = row.before;
      const attempt =
        row.castId != null
          ? session.combat.attempts.find((a) => a.castId === row.castId)
          : null;
      const routeEntry = routeHistory.find(
        (entry) => entry.actionId === row.actionId,
      );
      tr.dataset.nodeId = routeEntry?.nodeId || "";
      const record =
        (row.input?.checkpointId != null
          ? session.inputRecords.find(
              (r) => r.checkpointId === row.input.checkpointId,
            )
          : attempt
            ? session.inputRecords.find(
                (r) => r.attemptId === attempt.attemptId,
              )
            : null) ||
        session.inputRecords.find(
          (r) => r.skill === row.skill && Math.abs(r.time - row.time) < 1e-7,
        );
      const result = session.combat.events.find(
        (e) => e.type === "sunResult" && e.castId === row.castId,
      );
      const branch = result ? critFeedback(result) : null;
      const values = [
        at(row.time),
        `${row.input?.key || keyFor(row.skill)} ${nameFor(row.spell || row.skill)}`,
        b
          ? `真气${b.chi} · 怒雷${b.cooldowns.fists.toFixed(2)}s · 套装${b.rhythm}`
          : "—",
        `${routeEntry ? `拳谱：${routeReason(routeEntry)}。` : ""}${row.expected}。${row.note}${branch ? ` ${branch.parts.map((p) => `${p.label}${p.crit ? "暴击" : ""}`).join(" / ")}；${branch.cooldown}` : ""}`,
      ];
      values.forEach((value) => tr.append(el("td", value)));
      const td = el("td"),
        button = el("button", "从此重练", "text-button");
      button.disabled =
        !record?.checkpointId ||
        !session.checkpoints.some((c) => c.id === record.checkpointId);
      button.addEventListener("click", () =>
        restoreCheckpoint(record.checkpointId),
      );
      td.append(button);
      tr.append(td);
      return tr;
    }),
  );
}
function showAlternatives() {
  if (!session.plan || session.planEpoch !== session.epoch) return;
  $("alternatives-note").textContent =
    `${session.planTime.toFixed(2)}s 的状态。${session.plan.scope} 评分窗口${session.plan.evaluationHorizon.toFixed(1)}秒；每项${session.plan.alternatives[0]?.samples || 0}个配对样本。${session.plan.uncertain ? "当前差距不确定，保留参考基线。" : ""}`;
  $("alternatives-list").replaceChildren(
    ...session.plan.alternatives.map((a) => {
      const article = el("article");
      article.append(
        el("b", `${fmt(a.mean)} ± ${fmt(a.spread)}`),
        el(
          "strong",
          `${nameFor(a.action === "wind" ? "wind" : a.skill)}${a.baseline ? " · APL基线" : ""}`,
        ),
        el(
          "p",
          `相比基线 ${a.deltaFromBaseline >= 0 ? "+" : ""}${fmt(a.deltaFromBaseline)} 核心模型伤害；离散度为样本标准差。`,
        ),
      );
      return article;
    }),
  );
  openDialog("alternatives-dialog");
}
function critSound(count) {
  if (!$("sound").checked || !audio) return;
  const now = audio.currentTime;
  for (let i = 0; i < count; i++) {
    const osc = audio.createOscillator(),
      gain = audio.createGain();
    osc.type = "sine";
    osc.frequency.value = i ? 880 : 660;
    gain.gain.setValueAtTime(0, now + i * 0.075);
    gain.gain.linearRampToValueAtTime(0.035, now + i * 0.075 + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.075 + 0.12);
    osc.connect(gain);
    gain.connect(audio.destination);
    osc.start(now + i * 0.075);
    osc.stop(now + i * 0.075 + 0.13);
  }
}
function enableAudio() {
  if (!$("sound").checked) return;
  try {
    audio ||= new AudioContext();
    audio.resume().catch(() => {});
  } catch {
    /* Audio is optional. */
  }
}
function skillContent(id, detailed) {
  const actual = id === "sun" && session.combat.buffLeft("wind") ? "wind" : id,
    source = SPELL_DATA[actual];
  const texts = {
    palm: "55能量换2真气。注意不要连续重复，也不要让真气溢出。",
    blackout:
      "普通消耗1气，高亮时免费并回气；乾元内免费。推动旭日和怒雷冷却，高亮可能触发疾风；按钮本身不替换为疾风。",
    sun: "当前旭日与晨晖分别判暴。每次暴击减少怒雷基础冷却4秒，实际减少的墙钟时间受青龙恢复速率影响；请看最近结算栏。疾风在同一槽位，使用独立冷却。",
    fists:
      "当前构筑2气，乾元内1气。急速锁定开条值，青龙改变后续脉冲节拍；通道固定结束时间可能导致少于5跳。保护宏下不会被其他技能误断，Esc / X 可主动取消。",
    crane:
      "普通2气，乾元1气，赤精免费。4次独立地面命中，施放1.5秒后独立结算减冷却；最多5目标各减0.5秒基础冷却。普通旭日等瞬发可共存；疾风与怒雷属于另一个通道。",
    dragon:
      "冷却30秒，不吃急速，受青龙恢复速率影响。独立可用窗口包含宽限；给予约6秒青龙与赤精。",
    tiger: "白虎持续20秒，解锁天神槽位。白虎宠物及部分被动伤害未完整计入。",
    conduit:
      "天神有真实引导条。镇踏可共存；有效替换或Esc结束时，当前SimC模型立即给大青龙。实服伪取消差异待核验。",
    zenith:
      "2充能顺序恢复90秒，最短间隔16秒。自动踏一次，另有两次手动镇踏，未消费完时按钮保持为踏。参考调度等待白虎公共冷却结束。",
    stomp:
      "产生2真气；当前SimC投影中手动踏占1秒公共冷却，并可与天神引导共存。攻略中免费踏的差异待实服核验。",
  };
  const content = el("div"),
    heading = el("div", null, "spell-heading"),
    img = el("img");
  img.src = source.iconPath;
  img.alt = "";
  heading.append(img, el("h3", source.name));
  content.append(heading, el("p", texts[id] || texts.sun));
  if (detailed) {
    const a = el("a", "Wowhead 中文资料 ↗");
    a.href = source.source;
    a.target = "_blank";
    a.rel = "noreferrer";
    const details = el("details");
    details.append(
      el("summary", "基础提示快照 · 可能包含其他专精"),
      el("p", source.tooltip, "base-tooltip"),
    );
    content.append(
      a,
      el(
        "p",
        `资料快照 ${source.fetchedAt.slice(0, 10)}。当前构筑机制以固定SimC投影为准。`,
        "source-link",
      ),
      details,
    );
  }
  return content;
}
function hideTooltip() {
  $("spell-tooltip").hidden = true;
}
function showTooltip(slot, button) {
  if (document.querySelector("dialog[open]")) return;
  const tip = $("spell-tooltip");
  tip.replaceChildren(skillContent(slotAction(session.combat, slot), false));
  tip.hidden = false;
  const rect = button.getBoundingClientRect();
  tip.style.left = `${Math.max(10, Math.min(innerWidth - tip.offsetWidth - 10, rect.left))}px`;
  tip.style.top = `${Math.max(10, rect.top - tip.offsetHeight - 10)}px`;
}
for (const id of Object.keys(SKILLS))
  $("spell-picker").append(new Option(nameFor(id), id));
for (const [id, name, note] of [
  ["single", "单体拳谱", "原图为不同天赋示例，分支取决于实际触发。"],
  ["aoe", "2+目标拳谱", "2至5目标的神鹤减冷却不同，不能照抄同一串。"],
  ["bloodlust", "嗜血全双暴示例", "图按每次旭日双暴；次数不是合格线。"],
]) {
  const section = el("section"),
    img = el("img");
  img.src = `assets/references/${id}.png`;
  img.alt = name;
  img.loading = "lazy";
  img.className = "reference-image";
  section.append(el("h3", name), el("p", note), img);
  $("reference-images").append(section);
}
$("policy-source").href =
  `https://github.com/simulationcraft/simc/blob/${POLICY.revision}/${POLICY.source}`;
for (const sample of SIMC_SAMPLES.samples)
  $("simc-sample-picker").append(
    new Option(
      `${sample.targets}目标${sample.bloodlust ? " · 嗜血" : ""} · ${sample.label} · seed ${sample.seed}`,
      sample.id,
    ),
  );
function renderSimcSample() {
  const sample = SIMC_SAMPLES.samples.find(
    (s) => s.id === $("simc-sample-picker").value,
  );
  const root = $("simc-sample-detail");
  const note = el(
    "p",
    `首次旭日 ${at(sample.sunTime)}；本体${sample.mainCrit ? "暴击" : "普通"}，${sample.dawn.present ? `晨晖${sample.dawn.result === "crit" ? "暴击" : "普通"}` : "无晨晖"}；结算后${sample.chi}气。怒雷施放前剩余${sample.fistsBefore.toFixed(3)}s；${sample.fistsAfter ? `日志直接记录结算后${sample.fistsAfter.seconds.toFixed(3)}s` : "日志未直接记录结算后剩余值"}。`,
  );
  const list = el("ol", null, "simc-cast-list");
  for (const cast of sample.casts) {
    const item = el("li");
    const img = el("img");
    img.src = SPELL_DATA[cast.spell].iconPath;
    img.alt = "";
    item.append(
      img,
      el("span", nameFor(cast.spell)),
      el("small", at(cast.time)),
    );
    list.append(item);
  }
  root.replaceChildren(note, list, el("p", SIMC_SAMPLES.scope, "small-note"));
}
$("simc-sample-picker").onchange = renderSimcSample;
renderSimcSample();
for (const button of document.querySelectorAll("[data-close]"))
  button.addEventListener("click", () => $(button.dataset.close).close());
$("start").onclick = () => {
  enableAudio();
  start();
};
$("demo").onclick = () => {
  enableAudio();
  start(true);
};
$("pause").onclick = () => setPaused(!session.paused);
$("finish").onclick = finish;
$("reset").onclick = () => prepare();
$("cancel").onclick = () => cancelInput();
$("retry").onclick = () => restoreCheckpoint(session.checkpoints.at(-1)?.id);
$("settings-open").onclick = () => openDialog("settings-dialog");
$("source-open").onclick = () => openDialog("source-dialog");
$("review-open").onclick = () => {
  renderReview();
  openDialog("review-dialog");
};
$("alternatives-open").onclick = showAlternatives;
$("route-focus").onclick = () => {
  const node =
    $("routine-map").querySelector('[aria-current="step"]') ||
    $("routine-map").querySelector("[data-node-id]");
  node?.scrollIntoView({
    behavior: $("reduce-motion").checked ? "instant" : "smooth",
    block: "nearest",
    inline: "center",
  });
};
$("spell-open").onclick = () => {
  $("spell-detail").replaceChildren(
    skillContent($("spell-picker").value, true),
  );
  openDialog("spell-dialog");
};
$("spell-picker").onchange = () => {
  $("spell-detail").replaceChildren(
    skillContent($("spell-picker").value, true),
  );
};
$("scenario").onchange = () => {
  applyScenarioDefaults();
  prepare();
};
$("settings-form").onsubmit = (e) => {
  e.preventDefault();
  enableAudio();
  $("settings-dialog").close();
  prepare();
  notify("设置已应用，按 Enter 开始新一轮。");
};
$("bindings-open").onclick = () => {
  $("binding-error").textContent = "";
  $("binding-fields").replaceChildren(
    ...Object.entries(ACTION_SLOTS).map(([id, s]) => {
      const label = el("label", s.label),
        input = el("input");
      input.value = keys[id].toUpperCase();
      input.name = id;
      input.maxLength = 1;
      input.setAttribute("aria-label", `${s.label}键位`);
      input.onkeydown = (e) => {
        if (e.key === "Tab") return;
        e.preventDefault();
        if (/^[a-z0-9]$/i.test(e.key)) input.value = e.key.toUpperCase();
      };
      label.append(input);
      return label;
    }),
  );
  openDialog("bindings-dialog");
};
$("bindings-form").onsubmit = (e) => {
  e.preventDefault();
  const next = Object.fromEntries(
    [...new FormData(e.target)].map(([id, value]) => [id, value.toLowerCase()]),
  );
  if (
    Object.values(next).some((k) => !/^[a-wyz0-9]$/.test(k)) ||
    new Set(Object.values(next)).size !== 8
  ) {
    $("binding-error").textContent =
      "请使用互不重复的字母或数字，X保留为主动断条。";
    return;
  }
  keys = next;
  try {
    localStorage.setItem("windwalker-dojo-keys-v2", JSON.stringify(keys));
  } catch {
    /* The chosen keys remain valid for this session. */
  }
  $("bindings-dialog").close();

  render();
};
$("event-open").onclick = () => {
  const records = [
    ...session.combat.events.map((e) => ({ time: e.time, text: e.text })),
    ...session.combat.attempts.map((a) => ({
      time: a.time,
      text: `输入${a.attemptId} · ${nameFor(a.spell)} · ${{ rejected: "拒绝", queued: "入队", executed: "执行" }[a.status]}${a.reason ? ` · ${a.reason}` : ""}`,
    })),
  ].sort((a, b) => a.time - b.time);
  $("event-log").replaceChildren(
    ...records.slice(-500).map((record) => {
      const li = el("li");
      li.append(el("time", at(record.time)), el("span", record.text));
      return li;
    }),
  );
  openDialog("event-dialog");
};
$("export").onclick = () => {
  const report = {
    ...session.export(),
    policy: POLICY,
    calibrationSha256: CALIBRATION.sha256,
    referenceReview: reviewRoutine(session.combat),
    criteria:
      "Pinned reference and observed route branches; core-model recommendations are not a proof of global optimality.",
    checkpointPolicy:
      "The latest 100 accepted inputs retain atomic combat and route checkpoints in browser memory.",
  };
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
  );
  const a = el("a");
  a.href = url;
  a.download = `shaseng-training-${Date.now()}.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
document.addEventListener("keydown", (e) => {
  if (
    e.ctrlKey ||
    e.metaKey ||
    e.altKey ||
    e.target.matches("input,select,textarea") ||
    document.querySelector("dialog[open]")
  )
    return;
  const key = e.key.toLowerCase();
  if ([" ", "enter", "x", "escape", ...Object.values(keys)].includes(key))
    e.preventDefault();
  if (e.repeat) return;
  if (key === "enter" && !session.running) {
    enableAudio();
    start();
  } else if (key === " ") setPaused(!session.paused);
  else if (key === "x" || key === "escape") cancelInput("keyboard");
  else {
    const slot = Object.keys(keys).find((id) => keys[id] === key);
    if (slot) {
      enableAudio();
      press(slot, { source: "keyboard", key: e.key.toUpperCase(), slot });
    }
  }
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) setPaused(true);
});
window.addEventListener("resize", () => renderPlan());
applyScenarioDefaults();
prepare();
requestAnimationFrame(frame);
