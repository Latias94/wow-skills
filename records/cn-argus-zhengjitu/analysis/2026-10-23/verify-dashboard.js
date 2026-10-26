async page => {
  const root = 'E:/github/wow-skills/records/cn-argus-zhengjitu/analysis/2026-10-23';
  const url = 'http://127.0.0.1:8767/records/cn-argus-zhengjitu/analysis/2026-10-23/dashboard.html';
  const errors = [];
  await page.context().unroute('https://**');
  page.on('pageerror', error => errors.push(error.message));
  const check = (value, message) => { if (!value) throw new Error(message); };
  await page.setViewportSize({ width: 1440, height: 1080 });
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelectorAll('#target-gear .gear-row').length === 16);
  const data = await page.locator('#report-data').evaluate(el => JSON.parse(el.textContent));
  check(await page.locator('#current-gear .gear-row').count() === 15, 'current slot count');
  check(data.meta.budget === null && (await page.locator('#budget-tag').innerText()).includes('待确认'), 'current balance must remain unknown');
  check((await page.locator('#budget-notice').innerText()).includes('H10本周已R'), 'missing current-week H10 update');
  const h3 = data.routes.find(route => route.boss.startsWith('H3／'));
  const h10 = data.routes.find(route => route.boss.startsWith('H10／'));
  check(data.runs.length === 29 && h3.targets.includes(271481) && h3.excluded.includes(270164), 'H3 useful targets or exclusion');
  check(h10.priority.includes('本周不可再安排') && h10.excluded.length === 0, 'H10 must be deferred without guessed item exclusion');
  const weeklyRoute = { h3: h3.priority, h10: h10.priority, currentBalance: data.meta.budget, conditionalProbabilityOnly: h3.note.includes('不是已核实概率') };
  check(weeklyRoute.conditionalProbabilityOnly, 'probability caveat missing');
  check(await page.locator('#run-stage').inputValue() === 'practical', 'initial stage');
  check(await page.locator('#runs .run').count() === 2, 'initial batches');
  check(await page.locator('#target-raw').inputValue() === data.profiles.dungeon.raw, 'dungeon export');
  await page.locator('img').evaluateAll(images => images.forEach(image => image.loading = 'eager'));
  await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
  const desktop = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, images: document.images.length, titledGear: document.querySelectorAll('.gear-row a[title],.gear-row img[title]').length }));
  check(desktop.scrollWidth <= desktop.width, 'desktop page overflow');
  check(desktop.titledGear === 0, 'native tooltip overlaps');
  await page.screenshot({ path: root + '/dashboard-desktop.png', fullPage: false });
  await page.locator('#run-mode').selectOption('raid');
  await page.locator('#run-stage').selectOption('validation');
  check(await page.locator('#runs .run').count() === 1, 'raid filter');
  await page.locator('#run-mode').selectOption('dungeon');
  await page.locator('#run-stage').selectOption('robustness');
  check(await page.locator('#runs .run').count() === 3, 'sensitivity filter');
  const downloads = [];
  for (const mode of ['raid', 'dungeon']) {
    await page.locator('[data-profile="' + mode + '"]').click();
    check(await page.locator('#target-raw').inputValue() === data.profiles[mode].raw, mode + ' export mismatch');
    await page.locator('#target-raw').evaluate(el => el.closest('details').open = true);
    const pending = page.waitForEvent('download');
    await page.locator('[data-export="target"][data-action="download"]').click();
    const download = await pending;
    const name = download.suggestedFilename();
    check(name === 'zhengjitu-' + mode + '-2026-10-23.simc', 'wrong download filename');
    await download.saveAs(root + '/browser-downloads/' + name);
    downloads.push(name);
  }
  await page.locator('#current-raw').evaluate(el => el.closest('details').open = true);
  const currentPending = page.waitForEvent('download');
  await page.locator('[data-export="current"][data-action="download"]').click();
  const currentDownload = await currentPending;
  await currentDownload.saveAs(root + '/browser-downloads/' + currentDownload.suggestedFilename());
  downloads.push(currentDownload.suggestedFilename());
  await page.locator('#target-raw').evaluate(el => el.closest('details').open = false);
  const first = page.locator('#target-gear .gear-row').first();
  const item = first.locator('.item-name');
  await item.hover();
  let onlineTooltip = false;
  try {
    await page.locator('.wowhead-tooltip').first().waitFor({ state: 'visible', timeout: 7000 });
    onlineTooltip = true;
  } catch {}
  const gem = first.locator('a.gem').first();
  const gemName = await gem.locator('span').last().innerText();
  await gem.hover();
  let gemTooltip = false;
  try {
    await page.waitForFunction(name => [...document.querySelectorAll('.wowhead-tooltip')].some(el => el.innerText.includes(name) && el.getBoundingClientRect().width > 0), gemName, { timeout: 7000 });
    gemTooltip = true;
  } catch {}
  await first.locator('details').evaluate(el => el.open = true);
  check((await first.locator('.offline-tip').innerText()).includes('非完整配置'), 'offline reference disclaimer');
  await first.locator('details').evaluate(el => el.open = false);
  const rowHitAreas = await first.evaluate(el => {
    const box = el.getBoundingClientRect();
    return [[box.x + 20, box.y + 20], [box.right - 7, box.bottom - 7]].map(([x, y]) => Boolean(document.elementFromPoint(x, y)?.closest('a.item-name')));
  });
  check(rowHitAreas.every(Boolean), 'row icon/whitespace link coverage');
  await page.mouse.move(0, 0);
  await page.locator('.wowhead-tooltip').first().waitFor({ state: 'hidden', timeout: 3000 });
  await page.locator('#equipment').evaluate(el => el.scrollIntoView({ block: 'start' }));
  await page.screenshot({ path: root + '/dashboard-target-desktop.png', fullPage: false });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.mouse.move(0, 0);
  await page.locator('#equipment').evaluate(el => el.scrollIntoView({ block: 'start' }));
  const mobile = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, localTableScrolls: [...document.querySelectorAll('.table-scroll')].filter(el => el.scrollWidth > el.clientWidth).length }));
  check(mobile.scrollWidth <= mobile.width, 'mobile page overflow');
  await page.screenshot({ path: root + '/dashboard-mobile.png', fullPage: false });
  await page.context().route('https://**', route => route.abort());
  await page.goto('file:///' + root + '/dashboard.html', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelectorAll('#target-gear .gear-row').length === 16);
  await page.locator('img').evaluateAll(images => images.forEach(image => image.loading = 'eager'));
  await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
  const offline = { slots: await page.locator('#target-gear .gear-row').count(), budget: await page.locator('#budget-tag').innerText(), title: await page.title() };
  check(errors.length === 0, 'JavaScript page errors: ' + errors.join('; '));
  return { desktop, mobile, offline, downloads, onlineTooltip, gemTooltip, rowHitAreas, weeklyRoute, pageErrors: errors, checkedAt: new Date().toISOString() };
}
