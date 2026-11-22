const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const LOCAL = 'http://127.0.0.1:8080/?sharecode=YM64NRHD37';
const ONLINE = 'https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37';
const OUT = '/workspace/ai-news';
const STAMP = "deliverable_1122_1600";

async function checkStyles(page) {
  return await page.evaluate(() => {
    const res = {};
    let beforeCount = 0, beforeContentSample = [];
    for (const sheet of document.styleSheets) {
      let rules;
      try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) {
        if (rule.selectorText && rule.selectorText.includes('.entry::before')) {
          beforeCount++;
          try { beforeContentSample.push(rule.style.content || '(none)'); } catch (e) {}
        }
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
    res.sync_buttons = btns.filter(b => /同步|sync|刷新|refresh/i.test(b.textContent || '')).map(b => (b.textContent || '').trim());
    res.entries = document.querySelectorAll('.entry').length;
    res.data_theme = document.documentElement.getAttribute('data-theme');
    res.body_bg = getComputedStyle(document.body).backgroundColor;
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
  await page.goto(url || LOCAL, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2000);
  if (opts.theme) {
    await page.click(`#themeToggle button[data-theme="${opts.theme}"]`).catch(() => {});
    await page.waitForTimeout(1000);
  }
  if (opts.mode) {
    await page.click(`#viewToggle button[data-mode="${opts.mode}"]`).catch(() => {});
    await page.waitForTimeout(1200);
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
  r.light = await shoot(chromium, 'light', { theme: 'light', colorScheme: 'light' });
  r.dark = await shoot(chromium, 'dark', { theme: 'dark', colorScheme: 'dark' });
  r.auto = await shoot(chromium, 'auto', { theme: 'auto', colorScheme: 'dark' });
  r.auto_light = await shoot(chromium, 'auto_light', { theme: 'auto', colorScheme: 'light' });
  r.en = await shoot(chromium, 'en', { theme: 'light', mode: 'en', colorScheme: 'light' });
  r.online = await shoot(chromium, 'online', {}, ONLINE);
  console.log('\nDONE', JSON.stringify(r));
})();
