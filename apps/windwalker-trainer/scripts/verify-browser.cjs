const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {
  chromium,
} = require("C:/Users/Administrator/AppData/Roaming/npm/node_modules/@playwright/cli/node_modules/playwright-core");

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  const output = path.resolve(
    __dirname,
    "../../../.local/windwalker-trainer-qa",
  );
  fs.mkdirSync(output, { recursive: true });
  const errors = [],
    failedAssets = [],
    results = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("response", (response) => {
    if (
      response.status() >= 400 &&
      response.url().startsWith("http://127.0.0.1:8766/")
    )
      failedAssets.push(response.url());
  });
  const check = (name, condition) => {
    assert.ok(condition, name);
    results.push(name);
  };
  const text = (id) => page.locator(`#${id}`).innerText();
  const load = async () => {
    await page.goto("http://127.0.0.1:8766", { waitUntil: "networkidle" });
    await page.locator(".skill").first().waitFor();
  };
  const settings = async (values) => {
    await page.click("#settings-open");
    for (const [id, value] of Object.entries(values))
      await page.selectOption(`#${id}`, value);
    await page.click("#settings-form button[type=submit]");
  };
  const close = async (id) => page.click(`[data-close="${id}"]`);
  const downloadReport = async () => {
    await page.click("#review-open");
    const promise = page.waitForEvent("download");
    await page.click("#export");
    const file = await (await promise).path();
    const report = JSON.parse(fs.readFileSync(file, "utf8"));
    await close("review-dialog");
    return report;
  };
  try {
    for (const viewport of [
      { width: 1366, height: 768 },
      { width: 1920, height: 1080 },
      { width: 390, height: 844 },
    ]) {
      await page.setViewportSize(viewport);
      await load();
      const bounds = await page.evaluate(() =>
        Object.fromEntries(
          [
            "skillbar",
            "cast-track",
            "routine-map",
            "energy-text",
            "crit-feedback",
          ].map((id) => {
            const r = document.getElementById(id).getBoundingClientRect();
            return [
              id,
              { top: r.top, bottom: r.bottom, left: r.left, right: r.right },
            ];
          }),
        ),
      );
      check(
        `all controls fit ${viewport.width}x${viewport.height}`,
        Object.values(bounds).every(
          (r) =>
            r.top >= 0 &&
            r.bottom <= viewport.height &&
            r.left >= 0 &&
            r.right <= viewport.width,
        ),
      );
      check(
        `no horizontal overflow ${viewport.width}`,
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      );
      await page.screenshot({
        path: path.join(output, `v4-ready-${viewport.width}.png`),
      });
    }
    await page.setViewportSize({ width: 1366, height: 768 });
    await load();
    check(
      "exactly eight physical slots",
      (await page.locator(".skill").count()) === 8,
    );
    check(
      "requested default bindings",
      (await page.locator(".skill kbd").allTextContents()).join(",") ===
        "1,2,3,4,5,E,F,G",
    );
    await page.click("#source-open");
    check(
      "three original routine references",
      (await page.locator("#reference-images img").count()) === 3,
    );
    await page.locator("#simc-evidence summary").click();
    check(
      "seven actual SimC paths available",
      (await page.locator("#simc-sample-picker option").count()) === 7,
    );
    await page.selectOption("#simc-sample-picker", "st-double-crit-seed-012");
    check(
      "real SimC sample shows observed time and concrete casts",
      /3.54/.test(await text("simc-sample-detail")) &&
        (await page.locator("#simc-sample-detail li").count()) > 10,
    );
    await close("source-dialog");
    await page.click("#spell-open");
    await page.selectOption("#spell-picker", "fists");
    check("sourced spell detail", /Wowhead/.test(await text("spell-detail")));
    await close("spell-dialog");
    const manifest = await page.evaluate(
      async () => await (await fetch("assets/sprites/v6/manifest.json")).json(),
    );
    check(
      "12 skill states use the referenced panda's held key poses",
      manifest.version === 6 && manifest.actions.length === 12 &&
        manifest.actions.every((action) => action.frames === 1),
    );
    check(
      "all sprites load locally",
      await page.evaluate(async (actions) => {
        const results = await Promise.all(
          actions.map(
            (a) =>
              new Promise((resolve) => {
                const image = new Image();
                image.onload = () =>
                  resolve(
                    image.naturalWidth === a.cols * 384 &&
                      image.naturalHeight === a.rows * 384,
                  );
                image.onerror = () => resolve(false);
                image.src = a.src;
              }),
          ),
        );
        return results.every(Boolean);
      }, manifest.actions),
    );
    check(
      "renderer uses the new referenced panda artwork",
      await page.locator("#monk-sprite").evaluate((element) =>
        getComputedStyle(element).backgroundImage.includes("assets/sprites/v6/idle.webp"),
      ),
    );
    check(
      "generated background and dummy are loaded",
      await page.locator("[data-sprite-scene]").evaluateAll((images) =>
        images.length === 2 && images.every((image) => !image.hidden && image.naturalWidth > 0),
      ),
    );
    for (const [mode, label, main, dawn] of [
      ["none", "未暴", "普通", "普通"],
      ["single", "单暴", "暴击", "普通"],
      ["dawn", "单暴", "普通", "暴击"],
      ["double", "双暴", "暴击", "暴击"],
      ["no-dawn", "未暴", "普通", "未触发"],
    ]) {
      await load();
      await page.selectOption("#scenario", "crit-branch");
      await settings({ "crit-mode": mode });
      await page.click("#start");
      const prefixIds = await page
        .locator("#routine-map .rmap-prefix [data-node-id]")
        .evaluateAll((nodes) => nodes.map((n) => n.dataset.nodeId));
      await page.keyboard.press("1");
      await page.waitForFunction(
        (expected) =>
          document.getElementById("crit-badge").textContent === expected,
        label,
      );
      const parts = await page.locator("#crit-parts span").allTextContents();
      check(
        `stable prefix after ${mode}`,
        JSON.stringify(prefixIds) ===
          JSON.stringify(
            await page
              .locator("#routine-map .rmap-prefix [data-node-id]")
              .evaluateAll((nodes) => nodes.map((n) => n.dataset.nodeId)),
          ),
      );
      check(
        `actual branch highlighted ${mode}`,
        (await page
          .locator('#routine-map .rmap-variant[data-selected="true"]')
          .count()) === 1,
      );
      check(
        `selected route badge ${mode}`,
        /本次路线/.test(await text("route-status")),
      );
      check(
        `visible ${mode} main/Dawn branch`,
        parts[0].includes(main) && parts[1].includes(dawn),
      );
      check(
        `actual cooldown feedback ${mode}`,
        /实际减少 \d+\.\d{2}秒/.test(await text("crit-cooldown")),
      );
      if (mode === "double") {
        check(
          "independent critical hit numbers",
          (await page.locator(".floating-hit.critical").count()) >= 2,
        );
        await page.screenshot({
          path: path.join(output, "v4-double-crit.png"),
        });
      }
      const report = await downloadReport();
      check(
        `export schema/crit ${mode}`,
        report.schema === 4 &&
          report.state.events.some(
            (e) =>
              e.type === "sunResult" &&
              e.mainCrit === (main === "暴击") &&
              e.dawnTriggered === (mode !== "no-dawn"),
          ),
      );
    }
    await load();
    await page.click("#start");
    await page.keyboard.press("2");
    await page.waitForTimeout(1030);
    await page.keyboard.press("4");
    check(
      "Xuen slot transforms to Conduit",
      /conduit/.test(
        await page.locator("[data-slot=tiger] img").getAttribute("src"),
      ),
    );
    await page.waitForTimeout(800);
    await page.keyboard.press("5");
    await page.keyboard.press("f");
    await page.waitForFunction(
      () => document.querySelector("#cast-label").textContent === "怒雷引导",
    );
    await page.keyboard.press("1");
    check(
      "protected FoF rejects ordinary input",
      /保护|怒雷/.test(await text("input-message")),
    );
    check(
      "FoF channel remains active",
      (await text("cast-label")) === "怒雷引导",
    );
    await page.keyboard.press("Escape");
    check(
      "explicit Escape ends FoF",
      (await text("cast-label")) === "当前没有引导",
    );
    const beforeRetry = await downloadReport();
    check("clip is a recorded fact", beforeRetry.summary.clippedFists === 1);
    await page.click("#review-open");
    const retry = page.locator("#review-rows button:enabled").last();
    check("accepted input exposes retry", (await retry.count()) === 1);
    await retry.click();
    check(
      "node restore pauses for inspection",
      (await text("pause")) === "继续",
    );
    const afterRetry = await downloadReport();
    check(
      "node restore restores channel and prior damage",
      afterRetry.state.channel?.skill === "fists" &&
        afterRetry.summary.clippedFists === 0 &&
        afterRetry.state.time <= beforeRetry.state.time,
    );
    const clock = await text("clock");
    await page.waitForTimeout(220);
    check("paused clock stays fixed", (await text("clock")) === clock);
    await load();
    await page.selectOption("#scenario", "resource");
    check(
      "resource checkpoint retains real SCK channel",
      (await text("cast-label")) === "神鹤引导",
    );
    await page.click("#start");
    await page.waitForTimeout(850);
    await page.keyboard.press("2");
    check("SCK and Palm coexist", (await text("cast-label")) === "神鹤引导");
    const resourceReport = await downloadReport();
    check(
      "coexisting Palm executed",
      resourceReport.state.casts.at(-1).skill === "palm",
    );
    await load();
    await page.click("#bindings-open");
    await page.locator("input[name=sun]").fill("Q");
    await page.click("#bindings-form button[type=submit]");
    check(
      "editable binding appears",
      (await page.locator("[data-slot=sun] kbd").innerText()) === "Q",
    );
    await page.reload();
    check(
      "binding persists",
      (await page.locator("[data-slot=sun] kbd").innerText()) === "Q",
    );
    await page.evaluate(() =>
      localStorage.removeItem("windwalker-dojo-keys-v2"),
    );
    await load();
    await settings({ "planner-mode": "search" });
    await page.waitForFunction(
      () => !document.getElementById("alternatives-open").disabled,
    );
    await page.click("#alternatives-open");
    check(
      "local search compares multiple candidates",
      (await page.locator("#alternatives-list article").count()) >= 2,
    );
    await close("alternatives-dialog");
    await page.selectOption("#scenario", "crit-branch");
    await page.waitForFunction(
      () => !document.getElementById("alternatives-open").disabled,
    );
    check(
      "current-state checkpoint has a concrete route",
      (await page.locator("#routine-map [data-node-id]").count()) > 0,
    );
    await page.click("#demo");
    await page.waitForTimeout(1200);
    await page.click("#pause");
    await page.waitForTimeout(800);
    check("demonstration is labeled", /参考演示/.test(await text("phase")));
    check(
      "paused branch map remains visible",
      (await page.locator("#routine-map .rmap-card").count()) === 3,
    );
    await page.screenshot({ path: path.join(output, "v4-active-paused.png") });
    // Expose module-local controls only in this intercepted test response so
    // multiple legal inputs can be reproduced at exactly the same engine time.
    const appSource = fs.readFileSync(
      path.resolve(__dirname, "../dist/app.js"),
      "utf8",
    );
    await page.route("**/app.js", (route) =>
      route.fulfill({
        contentType: "text/javascript",
        body:
          appSource +
          "\nglobalThis.__dojoTest={start,press,cancelInput,renderReview,render,get session(){return session},get combat(){return session.combat},get records(){return session.inputRecords}};",
      }),
    );
    await page.reload();
    await page.waitForFunction(() => globalThis.__dojoTest);
    const repeatedCancel = await page.evaluate(() => {
      const t = globalThis.__dojoTest;
      document.getElementById("bloodlust").value = "off";
      t.start();
      t.press("palm", { source: "keyboard", key: "2", slot: "palm" });
      t.combat.advance(1);
      t.press("crane", { source: "keyboard", key: "E", slot: "crane" });
      t.combat.advance(1);
      t.cancelInput("keyboard");
      t.press("fists", { source: "keyboard", key: "F", slot: "fists" });
      t.cancelInput("keyboard");
      t.renderReview();
      const controls = t.combat.controls.map((c) => ({
        time: c.time,
        channel: c.before.channel.skill,
      }));
      document.querySelector("#review-rows tr:last-child button").click();
      return {
        controls,
        restored: t.combat.channel?.skill,
        retained: t.records.map((r) => r.skill),
      };
    });
    check(
      "same-time cancel rows restore their own exact channel",
      repeatedCancel.controls.length === 2 &&
        repeatedCancel.controls.every((c) => c.time === 2) &&
        repeatedCancel.restored === "fists",
    );
    check(
      "same-time retry preserves prior controls and casts",
      repeatedCancel.retained.join(",") === "palm,crane,cancel,fists",
    );
    await page.evaluate(() => {
      const t = globalThis.__dojoTest;
      document.getElementById("scenario").value = "crit-branch";
      document.getElementById("crit-mode").value = "double";
      t.session.prepare("crit-branch", {
        inputMode: "protected",
        protectCrane: true,
        sunOutcomes: [{ mainCrit: true, dawnTriggered: true, dawnCrit: true }],
      });
      t.start();
      t.press("sun", { source: "keyboard", key: "1", slot: "sun" });
      t.render();
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.click("#route-focus");
    check(
      "mobile selected route is visible after resolution",
      await page
        .locator('#routine-map .rmap-card[data-state="observed-selected"]')
        .evaluate((node) => {
          const r = node.getBoundingClientRect(),
            parent = node.parentElement.getBoundingClientRect();
          return r.left >= parent.left - 2 && r.right <= parent.right + 2;
        }),
    );
    await page.screenshot({
      path: path.join(output, "v4-mobile-selected.png"),
    });
    check("no browser runtime errors", errors.length === 0);
    check("no failed local asset requests", failedAssets.length === 0);
    fs.writeFileSync(
      path.join(output, "v4-browser-results.json"),
      JSON.stringify(
        { checkedAt: new Date().toISOString(), results, errors, failedAssets },
        null,
        2,
      ),
    );
    console.log(
      JSON.stringify(
        { passed: results.length, errors, failedAssets, artifacts: output },
        null,
        2,
      ),
    );
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
