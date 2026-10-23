async page => {
  const result = {};
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.setViewportSize({width:1440,height:1000});
  await page.reload();
  await page.locator('#current-gear').scrollIntoViewIfNeeded();
  await page.evaluate(async () => {
    for (const image of document.images) image.loading = 'eager';
    await Promise.all([...document.images].map(image => image.decode().catch(() => null)));
  });
  result.brokenImages = await page.evaluate(() => [...document.images].filter(image => !image.naturalWidth).length);
  if (result.brokenImages) throw new Error('Broken cached item images');
  result.exports = [];
  for (const mode of ['raid', 'dungeon']) {
    await page.locator(`[data-profile="${mode}"]`).click();
    const consistent = await page.evaluate(mode => {
      const data = JSON.parse(document.getElementById('report-data').textContent);
      return document.getElementById('target-raw').value === data.profiles[mode].raw;
    }, mode);
    if (!consistent) throw new Error('Mode export mismatch');
    await page.locator('#target-raw-summary').click();
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-export="target"][data-action="download"]').click();
    const download = await downloadPromise;
    const stream = await download.createReadStream();
    let downloaded = '';
    for await (const chunk of stream) downloaded += chunk.toString('utf8');
    const shown = await page.locator('#target-raw').inputValue();
    if (downloaded !== shown) throw new Error('Downloaded content mismatch');
    result.exports.push({mode, filename: download.suggestedFilename(), matches: true});
    await page.locator('#target-raw-summary').click();
  }
  await page.locator('#run-stage').selectOption('weapons');
  result.weaponTables = await page.locator('#runs .run').count();
  if (result.weaponTables !== 2) throw new Error('Weapon stage filtering failed');
  await page.locator('#run-mode').selectOption('raid');
  result.filteredTables = await page.locator('#runs .run').count();
  if (result.filteredTables !== 1) throw new Error('Mode filtering failed');
  await page.locator('#run-mode').selectOption('');
  await page.locator('#run-stage').selectOption('upgrade-current');
  await page.locator('#elite').scrollIntoViewIfNeeded();
  await page.screenshot({path:'records/cn-barrens-shaseng/analysis/2026-10-23/dashboard-elite.png',scale:'css'});
  result.overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  if (result.overflow) throw new Error('Desktop overflow');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path:'records/cn-barrens-shaseng/analysis/2026-10-23/dashboard-desktop.png',scale:'css'});
  await page.setViewportSize({width:390,height:844});
  result.mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  if (result.mobileOverflow) throw new Error('Mobile overflow');
  result.tooltipProviderLoaded = await page.evaluate(() => typeof window.$WowheadPower !== 'undefined');
  await page.locator('#current-gear .gear-row').first().locator('.item-name').hover();
  result.cachedTooltipCount = await page.locator('#current-gear details.offline-tip').count();
  await page.route('https://**/*', route => route.abort());
  await page.reload();
  result.offlineGearRows = await page.locator('#current-gear .gear-row').count();
  result.offlineEliteRows = await page.locator('#elite-samples tbody tr').count();
  if (result.offlineGearRows !== 15 || result.offlineEliteRows !== 13) throw new Error('Offline content failed');
  await page.unroute('https://**/*');
  result.pageErrors = errors;
  if (errors.length) throw new Error(errors.join('; '));
  return result;
}
