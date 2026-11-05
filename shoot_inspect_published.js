const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const PUBLISHED = 'https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37';
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
    res.data_theme = document.documentElement.getAttribute('data-theme');
    res.has_view_toggle = !!document.querySelector('#viewToggle');
    res.has_theme_toggle = !!document.querySelector('#themeToggle');
    return res;
  });
}

async function shoot(pw, name, theme, colorScheme) {
  const browser = await pw.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    device_scale_factor: 2,
    locale: 'zh-CN',
    colorScheme: colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(PUBLISHED, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2500);
  if (theme) {
    await page.click(`#themeToggle button[data-theme="${theme}"]`).catch(() => {});
    await page.waitForTimeout(1500);
  }
  const path = `${OUT}/${name}`;
  await page.screenshot({ path, full_page: false });
  console.log('saved:', path);
  const styles = await checkStyles(page);
  console.log('  样式实测:', JSON.stringify(styles));
  await browser.close();
  return { file: path, styles };
}

(async () => {
  const report = {};
  const pw = chromium;
  report.light = await shoot(pw, '巡检截图-浅色.png', 'light', 'light');
  report.dark = await shoot(pw, '巡检截图-暗黑.png', 'dark', 'dark');
  report.auto = await shoot(pw, '巡检截图-系统自动.png', 'auto', 'dark');
  console.log('\n=== 汇总 ===');
  console.log(JSON.stringify(report, null, 2));
})();
