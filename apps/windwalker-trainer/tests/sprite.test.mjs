import test from "node:test";
import assert from "node:assert/strict";
import { Combat } from "../dist/combat.js";
import { TrainingSession } from "../dist/session.js";
import { resolveSpriteState } from "../dist/sprite.js";

const actions = [
  "idle",
  "palm",
  "blackout",
  "sun",
  "wind",
  "fists",
  "crane",
  "dragon",
  "tiger",
  "conduit",
  "zenith",
  "stomp",
];
const art = {
  character: Object.fromEntries(
    actions.map((action) => [action, {
      src: `fixture/body/${action}.webp`,
      cols: 1,
      rows: 1,
      frames: 1,
      durationsMs: [80],
      duration: 0.55,
      loop: false,
    }]),
  ),
  effects: Object.fromEntries(
    [
      ...actions.filter((action) => action !== "idle"),
      "jade", "greaterJade", "bloodlust",
    ].map((action) => [action, {
      src: `fixture/fx/${action}.webp`,
      cols: 2,
      rows: 2,
      frames: 4,
      duration: action === "crane" ? 0.12 : 0.4,
      loop: true,
    }]),
  ),
};
for (const action of ["idle", "palm"]) {
  art.character[action] = {
    src: `fixture/body/${action}.webp`,
    cols: 3,
    rows: 2,
    frames: 5,
    durationsMs: [100, 200, 100, 100, 300],
    loop: action === "idle",
  };
}
const sprite = (combat, reducedMotion = false) =>
  resolveSpriteState(combat, art, reducedMotion);
const effect = (state, layer) =>
  state.effects.find((entry) => entry.layer === layer);

test("body timing uses manifest frame durations and keeps single-frame skill poses readable", () => {
  const combat = new Combat({ initialChi: 6 });
  assert.equal(combat.cast("palm").ok, true);
  combat.advance(0.1);
  assert.equal(sprite(combat).body.frame, 1);
  combat.advance(0.2);
  assert.equal(sprite(combat).body.frame, 2);
  combat.advance(0.4);
  assert.equal(sprite(combat).body.frame, 4);
  combat.advance(0.3);
  assert.equal(combat.cast("sun").ok, true);
  combat.advance(0.3);
  assert.equal(sprite(combat).action, "sun");
  assert.equal(sprite(combat).body.frame, 0);
  combat.advance(0.249);
  assert.equal(sprite(combat).action, "sun");
  combat.advance(0.002);
  assert.equal(sprite(combat).action, "idle");
});

test("SCK FX coexist with legal sun, tiger and blackout body weaves", () => {
  for (const skill of ["sun", "tiger", "blackout"]) {
    const combat = new Combat({ initialChi: 6, inputMode: "raw" });
    assert.equal(combat.cast("crane").ok, true);
    const channelId = combat.channel.id;
    combat.advance(1);
    assert.equal(combat.cast(skill).ok, true);
    const state = sprite(combat);
    assert.equal(combat.channel.id, channelId);
    assert.equal(state.action, skill);
    assert.ok(effect(state, "channel:crane")?.sheet);
    const layer = skill === "tiger" ? "buff:xuen" : `cast:${skill}`;
    assert.ok(effect(state, layer)?.sheet);
    assert.match(state.label, /神鹤独立伤害/);
  }
});

test("canceling SCK preserves its independent FX between scheduled damage pulses", () => {
  const combat = new Combat({ initialChi: 6, inputMode: "raw" });
  combat.cast("crane");
  combat.advance(0.13);
  assert.equal(combat.cancel({ source: "keyboard", key: "X" }), true);
  assert.equal(combat.channel, null);
  assert.ok(combat.time - combat.hits.at(-1).time > art.effects.crane.duration);
  assert.ok(effect(sprite(combat), "channel:crane")?.sheet);
  const lastPulse = combat.pending.findLast(
    (entry) => entry.type === "hit" && entry.data.skill === "crane",
  );
  combat.advance(lastPulse.at - combat.time);
  assert.equal(combat.hits.filter((hit) => hit.skill === "crane").length, 4);
  assert.ok(effect(sprite(combat), "channel:crane")?.sheet);
  combat.advance(art.effects.crane.duration + 0.01);
  assert.equal(effect(sprite(combat), "channel:crane"), undefined);
});

test("FoF body and FX end with early cancellation or the final real hit", () => {
  for (const early of [true, false]) {
    const combat = new Combat({ initialChi: 6, inputMode: "raw" });
    combat.cast("fists");
    assert.ok(effect(sprite(combat), "channel:fists")?.sheet);
    if (early) {
      combat.advance(0.05);
      combat.cancel({ source: "keyboard", key: "X" });
    } else {
      combat.advance(combat.channel.end - combat.time);
    }
    assert.equal(combat.channel, null);
    assert.equal(sprite(combat).action, "idle");
    assert.equal(effect(sprite(combat), "channel:fists"), undefined);
    assert.equal(combat.clippedFists, Number(early));
  }
});

test("Conduit completion and cancellation replace small jade while preserving avatar", () => {
  for (const early of [true, false]) {
    const combat = new Combat({ inputMode: "raw" });
    combat.cast("tiger");
    combat.advance(1);
    combat.cast("zenith");
    combat.setBuff("jade", 6);
    assert.equal(combat.cast("conduit").ok, true);
    assert.ok(effect(sprite(combat), "channel:conduit")?.sheet);
    assert.ok(effect(sprite(combat), "buff:jade")?.sheet);
    if (early) {
      combat.advance(0.05);
      combat.cancel({ source: "keyboard", key: "X" });
    } else {
      combat.advance(combat.channel.end - combat.time);
    }
    const state = sprite(combat);
    assert.equal(effect(state, "channel:conduit"), undefined);
    assert.equal(effect(state, "buff:jade"), undefined);
    assert.equal(
      effect(state, "buff:greatJade").sheet.src,
      art.effects.greaterJade.src,
    );
    assert.ok(effect(state, "buff:avatar")?.sheet);
    assert.match(state.label, /天神大青龙.*乾元青龙/);
    combat.advance(combat.buffLeft("greatJade"));
    assert.equal(effect(sprite(combat), "buff:greatJade"), undefined);
  }
});

test("white tiger lasts for its real summon buff, independently of body and Conduit", () => {
  const combat = new Combat({ inputMode: "raw" });
  combat.cast("palm");
  combat.advance(1);
  combat.cast("tiger");
  combat.advance(0.15);
  assert.equal(effect(sprite(combat), "buff:xuen").sheet.frame, 1);
  assert.equal(effect(sprite(combat), "cast:tiger"), undefined);
  combat.advance(1);
  combat.cast("conduit");
  combat.advance(0.8);
  combat.cancel();
  assert.ok(effect(sprite(combat), "buff:xuen")?.sheet);
  combat.advance(combat.buffLeft("tiger") - 0.01);
  assert.ok(effect(sprite(combat), "buff:xuen")?.sheet);
  combat.advance(0.01);
  assert.equal(combat.buffLeft("tiger"), 0);
  assert.equal(effect(sprite(combat), "buff:xuen"), undefined);
});

test("an explicit xuen lifetime takes precedence over the legacy tiger buff", () => {
  const combat = new Combat();
  combat.cast("palm");
  combat.advance(1);
  combat.cast("tiger");
  combat.setBuff("xuen", 2);
  combat.advance(0.15);
  assert.equal(effect(sprite(combat), "buff:xuen").sheet.frame, 1);
  combat.advance(2);
  assert.ok(combat.buffLeft("tiger") > 0);
  assert.equal(combat.buffLeft("xuen"), 0);
  assert.equal(effect(sprite(combat), "buff:xuen"), undefined);
});

test("session pause and retry restore identical sprite frames without mutating engine state", () => {
  const session = new TrainingSession({
    options: { bloodlust: false, initialChi: 6, inputMode: "raw" },
  });
  session.start();
  session.act("tiger");
  session.tick(1);
  session.act("fists");
  session.tick(0.23);
  const saved = session.combat.saveState();
  const expected = sprite(session.combat);
  assert.deepEqual(session.combat.saveState(), saved);
  session.setPaused(true);
  session.tick(2);
  assert.deepEqual(sprite(session.combat), expected);
  session.setPaused(false);
  session.cancel({ source: "keyboard", key: "X" });
  const checkpointId = session.checkpoints.at(-1).id;
  session.tick(1);
  assert.equal(effect(sprite(session.combat), "channel:fists"), undefined);
  session.retry(checkpointId);
  assert.equal(session.paused, true);
  assert.deepEqual(sprite(session.combat), expected);
  session.tick(0.5);
  assert.deepEqual(sprite(session.combat), expected);
});

test("reduced motion holds key frames and text while respecting channel cancellation", () => {
  const combat = new Combat({ initialChi: 6, bloodlust: true });
  combat.cast("fists");
  combat.advance(0.05);
  const first = sprite(combat, true);
  combat.advance(0.5);
  const later = sprite(combat, true);
  assert.deepEqual(later.body, first.body);
  assert.deepEqual(
    effect(later, "channel:fists").sheet,
    effect(first, "channel:fists").sheet,
  );
  assert.match(later.label, /怒雷破.*嗜血/);
  combat.cancel();
  const stopped = sprite(combat, true);
  assert.equal(stopped.action, "idle");
  assert.equal(effect(stopped, "channel:fists"), undefined);
  assert.match(stopped.label, /凝神待势.*嗜血/);
});
