const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const URL = 'http://127.0.0.1:8080';
const OUT = '/workspace/ai-news';

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
      res.metrics_padding = { top: cs.paddingTop, right: cs.paddingRight, bottom: cs.paddingBottom, left: cs.paddingLeft };
      res.metrics_padding_all_zero = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0);
    }
    const btns = Array.from(document.querySelectorAll('button, a'));
    res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent || '').trim());
    res.entries = document.querySelectorAll('.entry').length;
    res.title = document.title;
    return res;
  });
}

async function shoot(pw, name, opts = {}) {
  const browser = await pw.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({
    viewport: opts.viewport || { width: 1440, height: 1000 },
    device_scale_factor: 2,
    locale: 'zh-CN',
    colorScheme: opts.colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2500);
  if (opts.theme) {
    // click theme segmented control if present
    await page.click(`#themeToggle button[data-theme="${opts.theme}"]`).catch(() => {});
    await page.waitForTimeout(1500);
  }
  const path = `${OUT}/${name}`;
  await page.screenshot({ path, full_page: false });
  console.log('saved:', path);
  const styles = await checkStyles(page);
  console.log('  样式实测:', JSON.stringify(styles));
  await browser.close();
  return styles;
}

(async () => {
  const report = {};
  report.light = await shoot(chromium, '巡检截图-浅色.png', { theme: 'light' });
  report.dark = await shoot(chromium, '巡检截图-暗黑.png', { theme: 'dark' });
  console.log('\n=== 汇总 ===');
  console.log(JSON.stringify(report, null, 2));
})();
