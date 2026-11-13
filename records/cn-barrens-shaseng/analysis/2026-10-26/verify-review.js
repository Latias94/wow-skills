/* Verify the local report in the user's explicitly authorized Edge CDP session. */
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('C:/Users/Administrator/AppData/Roaming/npm/node_modules/@playwright/cli/node_modules/playwright-core');

(async () => {
  const endpoint = fs.readFileSync(path.join(process.env.LOCALAPPDATA, 'Microsoft/Edge/User Data/DevToolsActivePort'), 'utf8').trim().split(/\r?\n/);
  const browser = await chromium.connectOverCDP('ws://127.0.0.1:' + endpoint[0] + endpoint[1]);
  const page = await browser.contexts()[0].newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const check = (value, message) => { if (!value) throw new Error(message); };
  try {
    await page.setViewportSize({ width: 1440, height: 1080 });
    await page.goto(pathToFileURL(path.join(__dirname, 'review.html')).href, { waitUntil: 'load' });
    check(await page.locator('#window option').count() === 13, 'user white windows');
    check(await page.locator('#sequence tr').count() > 15, 'opening sequence');
    check(await page.locator('#timeline circle').count() > 4, 'FoF timeline');
    check((await page.locator('#window-note').innerText()).includes('怒雷5'), 'user opening FoF count');
    await page.locator('#actor').selectOption('elite');
    check(await page.locator('#window option').count() === 19, 'elite white windows');
    check((await page.locator('#window-note').innerText()).includes('怒雷6'), 'elite opening FoF count');
    await page.locator('#window').selectOption('7');
    check((await page.locator('#window-note').innerText()).includes('Bisset'), 'window change');
    await page.locator('#scope').selectOption('trash_buff_steady');
    check((await page.locator('#metrics').innerText()).includes('35.72'), 'steady metrics');
    const desktop = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    check(desktop.scrollWidth <= desktop.width, 'desktop horizontal overflow');
    await page.screenshot({ path: path.join(__dirname, 'review-desktop.png') });
    await page.locator('#actor').selectOption('shaseng');
    await page.locator('#scope').selectOption('boss_buff_steady');
    check((await page.locator('#metrics').innerText()).includes('40.73'), 'boss steady metrics');
    await page.setViewportSize({ width: 390, height: 844 });
    const mobile = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    check(mobile.scrollWidth <= mobile.width, 'mobile horizontal overflow');
    await page.screenshot({ path: path.join(__dirname, 'review-mobile.png') });
    const links = await page.locator('a[href]').evaluateAll(items => items.map(item => item.getAttribute('href')));
    for (const link of links.filter(link => !/^(https?:|#)/.test(link))) {
      check(fs.existsSync(path.resolve(__dirname, link)), 'Missing linked evidence: ' + link);
    }
    const gearText = await page.locator('#gear table').first().innerText();
    check(gearText.includes('341') && !gearText.includes('340'), 'displayed item levels must use WCL evidence');
    check(errors.length === 0, 'page errors: ' + errors.join('; '));
    const receipt = { checkedAt: new Date().toISOString(), desktop, mobile, userWindows: 13, eliteWindows: 19, filters: true, timeline: true, localLinks: true, pageErrors: errors };
    fs.writeFileSync(path.join(__dirname, 'browser-verification.json'), JSON.stringify(receipt, null, 2) + '\n');
    console.log(JSON.stringify(receipt));
  } finally {
    await page.close();
  }
  process.exit(0);
})().catch(error => { console.error(error.message); process.exit(1); });
