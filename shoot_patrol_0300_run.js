const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const LOCAL = 'http://127.0.0.1:8080';
const ONLINE = 'https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37';
const OUT = '/workspace/ai-news';
const TAG = 'deliverable_1120_0300';

async function inspect(page) {
  return await page.evaluate(() => {
    const res = {};
    let beforeCount = 0;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const r of rules) if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++;
    }
    res.entry_before_rules = beforeCount;
    const entry = document.querySelector('.entry');
    res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no entry)';
    const m = document.querySelector('.metrics');
    if (m) {
      const cs = getComputedStyle(m);
      res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
      res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
    }
    res.sync_buttons = Array.from(document.querySelectorAll('button, a'))
      .filter(b => /同步|sync|refresh|刷新/i.test((b.textContent || '')))
      .map(b => (b.textContent || '').trim());
    res.entries = document.querySelectorAll('.entry').length;
    res.theme = document.documentElement.getAttribute('data-theme');
    return res;
  });
}

async function shoot(browser, { url, name, colorScheme, theme, view }) {
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    device_scale_factor: 2,
    locale: 'zh-CN',
    colorScheme: colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2000);
  if (theme) { await page.click(`#themeToggle button[data-theme="${theme}"]`).catch(() => {}); await page.waitForTimeout(1200); }
  if (view === 'en') { await page.click('#viewToggle button[data-view="en"]').catch(() => {}); await page.waitForTimeout(1000); }
  const path = `${OUT}/${name}`;
  await page.screenshot({ path, full_page: false });
  console.log('saved:', name, JSON.stringify(await inspect(page)));
  await ctx.close();
}

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  await shoot(browser, { url: LOCAL,  name: `${TAG}_light.png`,  colorScheme: 'light', theme: 'light' });
  await shoot(browser, { url: LOCAL,  name: `${TAG}_dark.png`,   colorScheme: 'dark',  theme: 'dark' });
  await shoot(browser, { url: LOCAL,  name: `${TAG}_auto.png`,   colorScheme: 'dark',  theme: 'auto' });
  await shoot(browser, { url: LOCAL,  name: `${TAG}_en.png`,     colorScheme: 'light', theme: 'light', view: 'en' });
  await shoot(browser, { url: ONLINE, name: `${TAG}_online.png`, colorScheme: 'light' });
  await browser.close();
})();
