const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');
const fs = require('fs');

const LOCAL = 'http://127.0.0.1:8080/?sharecode=YM64NRHD37';
const ONLINE = 'https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37';
const OUT = '/workspace/ai-news/screenshots';
const STAMP = 'deliverable_1121_0000';
fs.mkdirSync(OUT, { recursive: true });

async function checkStyles(page) {
  return await page.evaluate(() => {
    const res = {};
    let beforeCount = 0;
    for (const sheet of document.styleSheets) {
      let rules;
      try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) {
        if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
      }
    }
    res.entry_before_rules = beforeCount;
    const entry = document.querySelector('.entry');
    res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no .entry)';
    const m = document.querySelector('.metrics');
    if (m) {
      const cs = getComputedStyle(m);
      res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
      res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
    }
    const btns = Array.from(document.querySelectorAll('button, a'));
    res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent || '').trim());
    res.entries = document.querySelectorAll('.entry').length;
    res.data_theme = document.documentElement.getAttribute('data-theme');
    res.theme_buttons = Array.from(document.querySelectorAll('#themeToggle button')).map(b => b.dataset.theme);
    return res;
  });
}

async function shoot(pw, name, opts, url) {
  const browser = await pw.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    device_scale_factor: 2,
    locale: 'zh-CN',
    colorScheme: opts.colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2000);
  if (opts.theme) {
    await page.click(`#themeToggle button[data-theme="${opts.theme}"]`).catch(() => {});
    await page.waitForTimeout(800);
  }
  if (opts.mode) {
    await page.click(`#viewToggle button[data-mode="${opts.mode}"]`).catch(() => {});
    await page.waitForTimeout(1000);
  }
  const path = `${OUT}/${STAMP}_${name}.png`;
  await page.screenshot({ path, full_page: false });
  const styles = await checkStyles(page);
  console.log(name, '=>', path, '|', JSON.stringify(styles));
  await browser.close();
  return styles;
}

(async () => {
  const r = {};
  r.light = await shoot(chromium, 'light', { theme: 'light', colorScheme: 'light' }, LOCAL);
  r.dark = await shoot(chromium, 'dark', { theme: 'dark', colorScheme: 'dark' }, LOCAL);
  r.auto = await shoot(chromium, 'auto', { theme: 'auto', colorScheme: 'dark' }, LOCAL);
  r.en = await shoot(chromium, 'en', { theme: 'light', mode: 'en', colorScheme: 'light' }, LOCAL);
  try { r.online = await shoot(chromium, 'online', { theme: 'light', colorScheme: 'light' }, ONLINE); }
  catch (e) { r.online = { error: String(e).slice(0, 300) }; }
  fs.writeFileSync(`${OUT}/${STAMP}_checks.json`, JSON.stringify(r, null, 2));
  console.log('\nDONE', JSON.stringify(r));
})();
