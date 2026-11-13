const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("C:/Users/Administrator/AppData/Roaming/npm/node_modules/@playwright/cli/node_modules/playwright-core");

(async () => {
  const output = path.resolve(__dirname, "../../../.local/windwalker-trainer-qa/sprite-loading");
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 768 } });
  const gates = {};
  const requested = new Set();
  const results = [];
  for (const [name, pattern] of [
    ["palm", "**/assets/sprites/v6/palm.webp"],
    ["sun", "**/assets/sprites/v6/sun.webp"],
    ["fistsFx", "**/assets/fx/v5/fists.webp"],
  ]) {
    let release;
    const promise = new Promise((resolve) => { release = resolve; });
    gates[name] = release;
    await page.route(pattern, async (route) => {
      requested.add(name);
      await promise;
      await route.continue();
    });
  }
  await page.route("**/assets/sprites/v6/blackout.webp", (route) => route.abort());
  const check = (name, condition) => {
    console.log(`${condition ? "PASS" : "FAIL"} ${name}`);
    assert.ok(condition, name);
    results.push(name);
  };
  const body = page.locator("#monk-sprite");
  const hasVisibleBody = async (name) => {
    const clip = await body.boundingBox();
    const actual = await page.screenshot({ clip, path: path.join(output, `${name}.png`) });
    await body.evaluate((element) => { element.style.visibility = "hidden"; });
    const blank = await page.screenshot({ clip });
    await body.evaluate((element) => { element.style.visibility = ""; });
    return !actual.equals(blank);
  };
  const decode = (src) => page.evaluate(async (src) => {
    const image = new Image();
    image.src = src;
    await image.decode();
    await new Promise(requestAnimationFrame);
  }, src);
  try {
    await page.goto("http://127.0.0.1:8766", { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => document.querySelector("#monk-sprite")?.dataset.action === "idle");
    await decode("assets/sprites/v6/idle.webp");
    await page.addStyleTag({ content: ".stage-art > :not(#monk-sprite) { visibility: hidden !important; } .stage-art { background: #062719 !important; }" });
    await page.click("#demo");
    await page.waitForFunction(() => document.querySelector("#monk-sprite")?.dataset.action === "palm");
    await page.click("#pause");
    assert.ok(requested.has("palm"));
    check("demo keeps a painted panda while the next pose is still loading", await hasVisibleBody("pending-palm"));
    gates.palm();
    await decode("assets/sprites/v6/palm.webp");
    await page.waitForFunction(() => document.querySelector("#monk-sprite").dataset.sheet?.startsWith("assets/sprites/v6/palm.webp|"));
    check("a decoded pose appears even while demonstration playback is paused", await hasVisibleBody("decoded-palm"));

    await page.evaluate(async () => {
      const { Combat } = await import("./combat.js");
      const { renderSprite } = await import("./sprite.js");
      const combat = new Combat({ initialChi: 6 });
      combat.cast("sun");
      renderSprite(document.querySelector("#arena"), combat);
    });
    await page.click("#reset");
    gates.sun();
    await decode("assets/sprites/v6/sun.webp");
    check("late pose completion cannot overwrite a reset session", await body.evaluate((element) => element.dataset.action === "idle" && element.dataset.sheet?.startsWith("assets/sprites/v6/idle.webp|")));

    await page.evaluate(async () => {
      const { Combat } = await import("./combat.js");
      const { renderSprite } = await import("./sprite.js");
      const combat = new Combat({ initialChi: 6 });
      combat.cast("blackout");
      renderSprite(document.querySelector("#arena"), combat);
    });
    check("a failed pose request preserves the last painted panda", await hasVisibleBody("failed-blackout"));

    await page.evaluate(async () => {
      const { Combat } = await import("./combat.js");
      const { renderSprite } = await import("./sprite.js");
      const combat = new Combat({ initialChi: 6, inputMode: "raw" });
      combat.cast("fists");
      renderSprite(document.querySelector("#arena"), combat);
      combat.advance(.1);
      combat.cancel();
      renderSprite(document.querySelector("#arena"), combat);
    });
    gates.fistsFx();
    await decode("assets/fx/v5/fists.webp");
    check("late FX decoding cannot restore a canceled channel effect", await page.locator('[data-sprite-layer="channel:fists"]').evaluate((element) => element.hidden));
    fs.writeFileSync(path.join(output, "results.json"), JSON.stringify({ results }, null, 2));
    console.log(JSON.stringify({ passed: results.length, artifacts: output }));
  } finally {
    for (const release of Object.values(gates)) release();
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
