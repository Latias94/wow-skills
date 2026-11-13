import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Combat } from "../dist/combat.js";
import { CALIBRATION } from "../dist/calibration.js";

const evidence = JSON.parse(
  readFileSync(
    new URL("./fixtures/simc-branch-evidence.json", import.meta.url),
  ),
);

test("natural SimC fixtures cover the five declared observed outcomes on the pinned build", () => {
  assert.ok(
    evidence.provenance.source.sha.startsWith(CALIBRATION.simcRevision),
  );
  assert.equal(evidence.settings.lifetimeSeconds, 300);
  assert.equal(evidence.sweep.attempted, 64);
  assert.deepEqual(
    new Set(
      evidence.samples.filter((s) => s.targets === 1).map((s) => s.branch),
    ),
    new Set([
      "no-crit",
      "main-only-crit",
      "dawn-only-crit",
      "double-crit",
      "no-dawn",
    ]),
  );
  for (const s of evidence.samples) {
    if (s.targets === 1) assert.equal(s.debugMatchesSweep, true);
    assert.equal(s.fullStatesMatchesPriorRun, true);
    assert.ok(s.coreCasts.length > 10);
    assert.ok(s.firstRSK.main.line > 0);
  }
});

for (const sample of evidence.samples) {
  test(`core cooldown and chi mechanics agree with directly measured SimC result: ${sample.id}`, () => {
    const result = sample.firstRSK;
    const before = result.fofCooldown.atSelectionSeconds;
    const c = new Combat({
      targets: sample.targets,
      initialChi: result.chi.atSelection,
      sunOutcomes: [
        {
          mainCrit: result.main.result === "crit",
          dawnTriggered: result.dawn.present,
          dawnCrit: result.dawn.result === "crit",
        },
      ],
    });
    // This is a mechanism fixture, not a reconstructed full SimC combat state.
    c.setBuff("zenith", 20);
    c.setBuff("avatar", 4);
    if (sample.targets > 1) c.setBuff("greatJade", 6);
    c.cooldowns.fists = before * c.haste() * c.recovery();
    const outcome = c.cast("sun");
    assert.equal(outcome.ok, true);
    const observed = c.events.find((e) => e.type === "sunResult");
    assert.equal(observed.mainCrit, result.main.result === "crit");
    assert.equal(observed.dawnTriggered, result.dawn.present);
    const measuredChi = result.dawn.present
      ? result.chi.afterDawn
      : result.chi.afterCost;
    assert.equal(c.chi, measuredChi);
    const after = result.fofCooldown.observedAfterSeconds?.seconds;
    if (after != null)
      assert.ok(
        Math.abs(c.remaining("fists") - after) < 0.003,
        `model ${c.remaining("fists")} vs directly logged ${after}`,
      );
    for (const adjustment of result.fofCooldown.adjustments) {
      assert.ok(
        Math.abs(Math.abs(adjustment.adjustmentSeconds) - 4 / c.recovery()) <
          0.002,
      );
    }
    if (result.fofCooldown.adjustments.some((a) => a.resetSentinel))
      assert.equal(c.remaining("fists"), 0);
  });
}
