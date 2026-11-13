import { SPELL_DATA } from "./skill-data.js";

const views = new WeakMap();
let viewSerial = 0;
const PHASES = [
  ["opening", "起手"],
  ["first-zenith", "首乾元"],
  ["small-jade", "升龙青龙"],
  ["great-jade", "天神大青龙"],
  ["second-zenith", "二乾元"],
  ["sustain", "衔接"],
];
const COMPLETED = new Set([
  "matched",
  "executed",
  "completed",
  "done",
  "waited",
  "accepted",
  "alternative",
  "accepted-alternative",
]);
const SLOTS = { conduit: "tiger", stomp: "zenith", wind: "sun" };

function element(doc, tag, className, text) {
  const el = doc.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = text;
  return el;
}

function text(el, value) {
  const next = String(value ?? "");
  if (el.textContent !== next) el.textContent = next;
}

function attr(el, name, value) {
  if (value == null || value === false) {
    if (el.hasAttribute(name)) el.removeAttribute(name);
  } else if (el.getAttribute(name) !== String(value)) {
    el.setAttribute(name, String(value));
  }
}

function keyed(parent, records, values, keyFor, create, update) {
  const retained = new Set();
  let position = parent.firstElementChild;
  for (const value of values) {
    const key = keyFor(value);
    let record = records.get(key);
    if (!record) {
      record = create(value);
      records.set(key, record);
    }
    retained.add(key);
    update(record, value);
    if (record.el !== position) parent.insertBefore(record.el, position);
    position = record.el.nextElementSibling;
  }
  for (const [key, record] of records) {
    if (!retained.has(key)) {
      record.el.remove();
      records.delete(key);
    }
  }
}

function number(value, digits = 1) {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(digits).replace(/\.0$/, "")
    : null;
}

function critCount(outcome = {}) {
  return (
    Number(outcome.mainCrit === true) +
    Number(outcome.dawnTriggered === true && outcome.dawnCrit === true)
  );
}

function outcomeText(branch) {
  const outcome = branch.outcome;
  if (!outcome)
    return {
      short: branch.label || "结果未提供",
      full: branch.label || "结果未提供",
    };
  const main = outcome.mainCrit ? "本体暴击" : "本体未暴";
  const dawn = !outcome.dawnTriggered
    ? "未触发晨晖"
    : outcome.dawnCrit
      ? "晨晖暴击"
      : "晨晖未暴";
  return {
    short: `${outcome.mainCrit ? "本暴" : "本未暴"}·${!outcome.dawnTriggered ? "无晨" : outcome.dawnCrit ? "晨暴" : "晨未暴"}`,
    full: `${main}，${dawn}`,
  };
}

function summaryText(summary = {}) {
  const parts = [];
  const chi = number(summary.chi);
  const fists = number(summary.fists);
  const jade = number(summary.jadeLeft);
  if (chi != null) parts.push(`气 ${chi}`);
  if (fists != null)
    parts.push(Number(summary.fists) <= 0 ? "怒雷就绪" : `怒雷 ${fists}s`);
  if (jade != null) parts.push(`青龙 ${jade}s`);
  return parts.join(" · ") || "结算状态未提供";
}

function phaseInfo(graph, current, combat) {
  if (combat) {
    const zeniths = combat.windows.filter((w) => w.name === "zenith").length;
    const index = combat.buffLeft("greatJade")
      ? 3
      : combat.buffLeft("jade")
        ? 2
        : combat.buffLeft("zenith")
          ? zeniths > 1
            ? 4
            : 1
          : zeniths
            ? 5
            : 0;
    const visited = [
      true,
      zeniths > 0,
      combat.windows.some((w) => w.name === "jade"),
      combat.windows.some((w) => w.name === "greatJade"),
      zeniths > 1,
      index === 5,
    ];
    return { index, label: PHASES[index][1], visited };
  }
  const supplied = current?.phase ?? graph.phase;
  const id = typeof supplied === "object" ? supplied?.id : supplied;
  const metadata = graph.phases?.find((phase) => phase.id === id);
  const known = PHASES.findIndex(
    ([phaseId, label]) => phaseId === id || label === id,
  );
  if (known >= 0)
    return { index: known, label: metadata?.label || PHASES[known][1] };
  if (supplied) {
    return {
      index: -1,
      label:
        (typeof supplied === "object"
          ? supplied.label || supplied.name
          : metadata?.label || metadata?.name || supplied) || "当前阶段",
    };
  }
  if (!combat) return { index: -1, label: "阶段待确认" };
  const casts = combat?.casts ?? [];
  const zeniths = casts.filter((cast) => cast.skill === "zenith").length;
  const active = (name) =>
    typeof combat?.buffLeft === "function" && combat.buffLeft(name) > 0;
  const index =
    zeniths > 1
      ? 4
      : active("greatJade") || casts.some((cast) => cast.skill === "conduit")
        ? 3
        : active("jade") || casts.some((cast) => cast.skill === "dragon")
          ? 2
          : zeniths
            ? 1
            : 0;
  return { index, label: PHASES[index][1] };
}

function nodeShape(node) {
  return [
    node.id,
    node.kind,
    node.skill,
    node.spell,
    node.time,
    node.duration,
    node.phase,
    node.conditional,
  ];
}

function graphShape(graph) {
  return [
    graph.id,
    graph.createdAt,
    graph.phase,
    graph.phases?.map((p) => [p.id, p.label, p.name]),
    (graph.prefix ?? []).map(nodeShape),
    graph.fork && [
      graph.fork.id,
      graph.fork.triggerNodeId,
      (graph.fork.branches ?? []).map((branch) => [
        branch.id,
        branch.label,
        branch.outcome,
        branch.summary,
        (branch.nodes ?? []).map(nodeShape),
      ]),
    ],
  ];
}

function historyRevision(runner) {
  const history = runner.history ?? [];
  const last = history.at(-1);
  return [
    runner.historyRevision ?? runner.revision,
    history.length,
    history[0]?.actionId,
    last?.actionId,
    last?.castId,
    last?.graphId,
    last?.nodeId,
    last?.status,
    last?.reason,
    last?.branchId,
  ];
}

function nodeHistory(history, graphId) {
  const result = new Map();
  for (const row of history) {
    if (row.graphId !== graphId || row.nodeId == null) continue;
    if (COMPLETED.has(row.status)) result.set(row.nodeId, row);
    else if (
      row.status === "deviation" &&
      !COMPLETED.has(result.get(row.nodeId)?.status)
    )
      result.set(row.nodeId, row);
  }
  return result;
}

function completedWaits(graph, cursor, selected, finished) {
  const result = new Set();
  const prefix = graph.prefix ?? [];
  const branch = graph.fork?.branches?.find((entry) => entry.id === selected);
  const collect = (nodes, end) => {
    nodes.slice(0, Math.max(0, end)).forEach((node) => {
      if (node.kind === "wait") result.add(node.id);
    });
  };
  collect(
    prefix,
    selected || finished
      ? prefix.length
      : prefix.findIndex((node) => node.id === cursor),
  );
  if (branch)
    collect(
      branch.nodes ?? [],
      finished
        ? branch.nodes?.length
        : branch.nodes?.findIndex((node) => node.id === cursor),
    );
  return result;
}

function createNode(doc) {
  const el = element(doc, "li", "rmap-node");
  const face = element(doc, "span", "rmap-node-face");
  const image = element(doc, "img", "rmap-node-image");
  image.alt = "";
  image.draggable = false;
  const glyph = element(doc, "span", "rmap-node-glyph");
  const key = element(doc, "kbd", "rmap-node-key");
  const mark = element(doc, "span", "rmap-node-mark");
  mark.setAttribute("aria-hidden", "true");
  const label = element(doc, "span", "rmap-node-label");
  face.append(image, glyph, key, mark);
  el.append(face, label);
  return { el, image, glyph, key, mark, label, signature: "" };
}

function updateNode(record, node, model) {
  const row = model.history.get(node.id);
  const status =
    model.cursor === node.id
      ? "current"
      : COMPLETED.has(row?.status) || model.completedWaits.has(node.id)
        ? "done"
        : row?.status === "deviation"
          ? "review"
          : "pending";
  const revealed = model.hints || status === "done" || status === "review";
  const cancel = node.kind === "cancel";
  const wait = node.kind === "wait";
  const slot = SLOTS[node.skill] || node.skill;
  const binding = !revealed || wait ? null : cancel ? "X" : model.keys?.[slot];
  const key =
    typeof binding === "string" && binding.trim() ? binding.toUpperCase() : "";
  const spell = node.spell || node.skill;
  const data = SPELL_DATA[spell];
  const duration = number(node.duration);
  const name = !revealed
    ? "提示已关闭"
    : cancel
      ? "主动断条"
      : wait
        ? "等待"
        : data?.name || String(spell || "未命名技能");
  const description = [
    name,
    key && `按键 ${key}`,
    revealed &&
      duration != null &&
      `${node.kind === "channel" ? "引导" : wait ? "等待" : "持续"} ${duration}秒`,
    node.conditional && "条件路线",
    status === "current"
      ? "当前步骤"
      : status === "done"
        ? "已完成"
        : status === "review"
          ? "偏离参考，需复查"
          : "待执行",
  ]
    .filter(Boolean)
    .join("；");
  const signature = JSON.stringify([
    nodeShape(node),
    status,
    revealed,
    key,
    description,
  ]);
  if (record.signature === signature) return;
  record.signature = signature;
  attr(record.el, "data-node-id", node.id);
  attr(record.el, "data-kind", node.kind);
  attr(record.el, "data-phase", node.phase || "sustain");
  attr(record.el, "data-state", status);
  attr(record.el, "data-concealed", String(!revealed));
  attr(record.el, "aria-current", status === "current" ? "step" : null);
  attr(record.el, "aria-label", description);
  const phase = PHASES.find(([id]) => id === node.phase)?.[1] || "";
  attr(record.el, "title", `${description}${phase ? `；${phase}阶段` : ""}`);
  const path = revealed && !cancel && !wait ? data?.iconPath : null;
  record.image.hidden = !path;
  attr(record.image, "src", path || null);
  record.glyph.hidden = Boolean(path);
  text(record.glyph, !revealed ? "·" : cancel ? "×" : wait ? "◷" : "?");
  record.key.hidden = !key;
  text(record.key, key);
  record.mark.hidden = status !== "done" && status !== "review";
  text(record.mark, status === "done" ? "✓" : "!");
  text(
    record.label,
    !revealed
      ? "待观察"
      : duration != null && (node.kind === "channel" || wait)
        ? `${wait ? "等" : "引导"} ${duration}s`
        : cancel
          ? "断条"
          : name
              .replace("旭日东升踢", "旭日")
              .replace("神鹤引项踢", "神鹤")
              .replace("疾风呼啸踢", "疾风")
              .replace("乾元之巅", "乾元"),
  );
}

function renderNodes(list, records, nodes, model) {
  keyed(
    list,
    records,
    nodes,
    (node) => `${model.graph.id}:${node.id}`,
    () => createNode(list.ownerDocument),
    (record, node) => updateNode(record, node, model),
  );
}

function createCard(state, index) {
  const doc = state.root.ownerDocument;
  const el = element(doc, "section", "rmap-card");
  const heading = element(doc, "div", "rmap-card-heading");
  const title = element(doc, "h3", "", ["未暴", "单暴", "双暴"][index]);
  const count = element(doc, "span", "rmap-variant-count");
  const badge = element(doc, "span", "rmap-route-badge");
  heading.append(title, count, badge);
  const body = element(doc, "div", "rmap-card-body");
  const variants = element(doc, "div", "rmap-variants");
  variants.setAttribute("role", "group");
  variants.setAttribute("aria-label", `${title.textContent}的精确结果`);
  const detail = element(doc, "div", "rmap-detail");
  const route = element(doc, "ol", "rmap-route rmap-scroll");
  route.id = `${state.root.id}-branch-group-${index}`;
  route.tabIndex = 0;
  const empty = element(doc, "span", "rmap-empty", "等待后续状态");
  const summary = element(doc, "p", "rmap-summary");
  detail.append(route, empty, summary);
  body.append(variants, detail);
  el.append(heading, body);
  return {
    el,
    count,
    badge,
    variants,
    route,
    empty,
    summary,
    variantRecords: new Map(),
    nodeRecords: new Map(),
  };
}

function createView(container) {
  const doc = container.ownerDocument;
  const root = element(doc, "div", "routine-map-view");
  root.id = `routine-map-view-${++viewSerial}`;
  root.setAttribute("aria-label", "拳谱阶段与旭日分支路线");
  const phases = element(doc, "ol", "rmap-phases");
  phases.setAttribute("aria-label", "完整六阶段");
  const phaseItems = PHASES.map(([id, label], index) => {
    const el = element(doc, "li", "rmap-phase");
    el.dataset.phase = id;
    el.append(
      element(doc, "span", "rmap-phase-number", String(index + 1)),
      doc.createTextNode(label),
    );
    phases.append(el);
    return el;
  });
  const common = element(doc, "div", "rmap-common");
  const caption = element(doc, "div", "rmap-caption");
  const commonTitle = element(doc, "strong", "rmap-common-title");
  const archives = element(doc, "select", "rmap-archives");
  archives.setAttribute("aria-label", "查看当前或已保留的拳谱");
  const retry = element(doc, "button", "rmap-retry", "重练此段");
  retry.type = "button";
  caption.append(commonTitle, archives, retry);
  const prefix = element(doc, "ol", "rmap-route rmap-prefix rmap-scroll");
  prefix.tabIndex = 0;
  prefix.setAttribute("aria-label", "共享技能路线，可横向滚动");
  const junction = element(doc, "span", "rmap-junction");
  common.append(caption, prefix, junction);
  const branchScroller = element(doc, "div", "rmap-branches rmap-scroll");
  branchScroller.tabIndex = 0;
  branchScroller.setAttribute("aria-label", "旭日结果的三组分支，可横向滚动");
  const single = element(doc, "div", "rmap-single");
  const singleTitle = element(doc, "strong", "rmap-single-title");
  const singleNote = element(doc, "span", "rmap-single-note");
  single.append(singleTitle, singleNote);
  root.append(phases, common, branchScroller, single);
  container.append(root);
  const state = {
    root,
    phases,
    phaseItems,
    commonTitle,
    archives,
    retry,
    prefix,
    junction,
    branchScroller,
    single,
    singleTitle,
    singleNote,
    nodeRecords: new Map(),
    archiveRecords: new Map(),
    previews: new Map(),
    signature: "",
    archiveKey: "",
    previewRevision: 0,
  };
  state.cards = [0, 1, 2].map((index) => createCard(state, index));
  branchScroller.append(...state.cards.map((card) => card.el));
  archives.addEventListener("change", () => {
    state.archiveKey = archives.value;
    renderRoutineMap(container, state.runner, state.options);
  });
  retry.addEventListener("click", () => {
    const model = state.model;
    state.options.onRetry?.({
      graphId: model.graph.id,
      nodeId: model.cursor ?? model.graph.prefix?.[0]?.id ?? null,
      branchId: model.selected,
    });
  });
  return state;
}

function updateCard(state, card, branches, index, model) {
  const selected = branches.find((branch) => branch.id === model.selected);
  const previewKey = `${model.graph.id}:${model.graph.fork?.id ?? "no-fork"}:${index}`;
  const previewId = state.previews.get(previewKey);
  const preview =
    selected ||
    branches.find((branch) => branch.id === previewId) ||
    branches[0];
  attr(
    card.el,
    "data-state",
    selected
      ? "observed-selected"
      : model.selected
        ? "observed-not-selected"
        : "unresolved",
  );
  attr(
    card.el,
    "aria-label",
    `${["未暴", "单暴", "双暴"][index]}${selected ? "，本次路线" : "，条件路线"}`,
  );
  text(card.count, `${branches.length} 种结果`);
  text(
    card.badge,
    selected ? "本次路线" : model.selected ? "其他结果" : "待判定",
  );
  keyed(
    card.variants,
    card.variantRecords,
    branches,
    (branch) => `${model.graph.id}:${branch.id}`,
    () => {
      const el = element(state.root.ownerDocument, "button", "rmap-variant");
      el.type = "button";
      return { el };
    },
    (record, branch) => {
      const actual = branch.id === model.selected;
      const expanded = preview?.id === branch.id;
      const label = outcomeText(branch);
      text(record.el, `${actual ? "✓ " : ""}${label.short}`);
      attr(record.el, "data-branch-id", branch.id);
      attr(record.el, "data-selected", String(actual));
      attr(
        record.el,
        "data-state",
        actual
          ? "observed-selected"
          : model.selected
            ? "observed-not-selected"
            : "unresolved",
      );
      attr(record.el, "data-preview", String(expanded));
      attr(record.el, "aria-current", actual ? "true" : null);
      attr(record.el, "aria-expanded", String(expanded));
      attr(record.el, "aria-controls", card.route.id);
      attr(
        record.el,
        "aria-label",
        `${label.full}；${actual ? "本次路线" : "条件路线"}；${summaryText(branch.summary)}${selected && !actual ? "；本组已固定显示实际结果" : "；预览技能"}`,
      );
      attr(
        record.el,
        "title",
        `${label.full}${branch.label ? ` · ${branch.label}` : ""}`,
      );
      record.el.disabled = Boolean(selected && !actual);
      record.el.onclick = () => {
        state.previews.set(previewKey, branch.id);
        state.previewRevision++;
        renderRoutineMap(state.root.parentElement, state.runner, state.options);
      };
    },
  );
  attr(card.route, "data-preview-branch-id", preview?.id);
  attr(
    card.route,
    "aria-label",
    preview
      ? `${outcomeText(preview).full}的技能路线，可横向滚动`
      : "尚无具体路线",
  );
  const nodes = preview?.nodes ?? [];
  renderNodes(card.route, card.nodeRecords, nodes, model);
  card.route.hidden = nodes.length === 0;
  card.empty.hidden = nodes.length > 0;
  text(card.summary, preview ? summaryText(preview.summary) : "结果状态未提供");
  attr(card.summary, "title", card.summary.textContent);
}

/**
 * Append/update the map without changing the runner, combat, or host header.
 * Keys are indexed by physical slot; absent bindings stay hidden.
 * onRetry receives { graphId, nodeId, branchId }; checkpoint lookup belongs to the host.
 * Returns the stable map root, or null when no container was supplied.
 */
export function renderRoutineMap(
  container,
  runner,
  { keys, hints = true, combat, onRetry } = {},
) {
  if (!container || typeof container.append !== "function") return null;
  let state = views.get(container);
  if (!state || state.root.parentElement !== container) {
    state = createView(container);
    views.set(container, state);
  }
  state.runner = runner;
  state.options = { keys, hints, combat, onRetry };
  const archives = (runner?.archives ?? []).map((entry, index) => ({
    entry,
    key: `${index}:${entry.graph?.id ?? entry.id}`,
  }));
  const archive = archives.find((item) => item.key === state.archiveKey)?.entry;
  if (!archive) state.archiveKey = "";
  const graph = archive?.graph ??
    archive ??
    runner?.graph ?? { id: "unavailable", prefix: [], fork: null };
  const selectedId = archive
    ? (archive.selectedBranchId ?? graph.fork?.selectedBranchId)
    : runner?.selectedBranchId;
  const selected = graph.fork?.branches?.some(
    (branch) => branch.id === selectedId,
  )
    ? selectedId
    : null;
  const cursor = archive ? null : runner?.cursorNodeId;
  const nodes = [
    ...(graph.prefix ?? []),
    ...(graph.fork?.branches ?? []).flatMap((branch) => branch.nodes ?? []),
  ];
  const current = nodes.find((node) => node.id === cursor);
  const archivedFocus =
    archive &&
    (nodes.find((node) => node.id === archive.cursorNodeId) ??
      graph.fork?.branches
        ?.find((branch) => branch.id === selected)
        ?.nodes?.at(-1) ??
      graph.prefix?.at(-1));
  const phase = phaseInfo(
    graph,
    current ?? archivedFocus,
    archive ? null : combat,
  );
  const signature = JSON.stringify([
    container.clientWidth,
    graphShape(graph),
    selected,
    cursor,
    historyRevision(runner ?? {}),
    keys,
    hints,
    phase,
    Boolean(onRetry),
    state.archiveKey,
    state.previewRevision,
    archives.map(({ entry, key }) => [
      key,
      entry.selectedBranchId,
      entry.status,
    ]),
  ]);
  if (state.signature === signature && state.historySource === runner?.history)
    return state.root;
  const scrollPositions = [...state.root.querySelectorAll(".rmap-scroll")].map(
    (el) => [el, el.scrollLeft, el.scrollTop],
  );
  state.signature = signature;
  state.historySource = runner?.history;
  const model = {
    graph,
    selected,
    cursor,
    keys,
    hints,
    history: nodeHistory(archive?.history ?? runner?.history ?? [], graph.id),
    completedWaits: completedWaits(
      graph,
      archive?.cursorNodeId ?? cursor,
      selected,
      archive?.status === "completed",
    ),
  };
  state.model = model;
  attr(state.root, "data-graph-id", graph.id);
  attr(state.root, "data-hints", String(Boolean(hints)));
  attr(state.root, "data-archived", String(Boolean(archive)));
  attr(state.root, "data-has-fork", String(Boolean(graph.fork)));
  state.phaseItems.forEach((el, index) => {
    attr(el, "aria-current", phase.index === index ? "true" : null);
    attr(
      el,
      "data-state",
      phase.index === index
        ? "current"
        : (phase.visited ? phase.visited[index] : phase.index > index)
          ? "past"
          : "upcoming",
    );
  });
  attr(
    state.phases,
    "aria-label",
    `完整六阶段；${archive ? "保留路线" : "当前阶段"}：${phase.label}`,
  );
  text(
    state.commonTitle,
    archive ? "保留路线" : graph.fork ? "公共段" : "单路线",
  );
  attr(state.commonTitle, "title", `当前阶段：${phase.label}`);
  const archiveOptions = [
    { key: "", label: "当前路线" },
    ...archives.map(({ entry, key }, index) => {
      const archivedGraph = entry.graph ?? entry;
      const archivedBranch = archivedGraph.fork?.branches?.find(
        (branch) =>
          branch.id ===
          (entry.selectedBranchId ?? archivedGraph.fork.selectedBranchId),
      );
      return {
        key,
        label: `保留 ${index + 1}${archivedBranch ? ` · ${["未暴", "单暴", "双暴"][critCount(archivedBranch.outcome)]}` : ""}`,
      };
    }),
  ];
  keyed(
    state.archives,
    state.archiveRecords,
    archiveOptions,
    (option) => option.key,
    () => ({ el: element(container.ownerDocument, "option") }),
    (record, option) => {
      record.el.value = option.key;
      text(record.el, option.label);
    },
  );
  state.archives.hidden = archives.length === 0;
  state.archives.value = state.archiveKey;
  state.retry.hidden = typeof onRetry !== "function";
  state.retry.disabled = !nodes.length;
  renderNodes(state.prefix, state.nodeRecords, graph.prefix ?? [], model);
  text(state.junction, graph.fork ? "旭日判支\n↙ ↓ ↘" : phase.label);
  attr(
    state.junction,
    "title",
    graph.fork ? "以实际旭日结果点亮精确路线" : `当前阶段：${phase.label}`,
  );
  state.branchScroller.hidden = !graph.fork;
  state.single.hidden = Boolean(graph.fork);
  if (graph.fork) {
    const branches = graph.fork.branches ?? [];
    state.cards.forEach((card, index) =>
      updateCard(
        state,
        card,
        branches.filter((branch) => critCount(branch.outcome) === index),
        index,
        model,
      ),
    );
  } else {
    state.cards.forEach((card, index) =>
      updateCard(state, card, [], index, model),
    );
    text(state.singleTitle, "未到旭日判断点");
    text(
      state.singleNote,
      graph.prefix?.length
        ? "按当前单路线衔接；到旭日后再读取实际结果。"
        : "等待后续状态；当前图没有可展示的技能。",
    );
  }
  for (const [el, left, top] of scrollPositions) {
    if (el.isConnected) {
      if (el.scrollLeft !== left) el.scrollLeft = left;
      if (el.scrollTop !== top) el.scrollTop = top;
    }
  }
  const selectionKey = selected
    ? `${graph.id}:${selected}:${container.clientWidth}`
    : null;
  if (selectionKey && selectionKey !== state.lastSelection) {
    const card = state.cards.find(
      (entry) => entry.el.dataset.state === "observed-selected",
    );
    if (card) {
      const parent = state.branchScroller.getBoundingClientRect();
      const rect = card.el.getBoundingClientRect();
      if (rect.left < parent.left || rect.right > parent.right) {
        state.branchScroller.scrollLeft += rect.left - parent.left;
      }
    }
  }
  state.lastSelection = selectionKey;
  return state.root;
}
