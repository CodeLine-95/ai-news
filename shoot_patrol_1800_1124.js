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
    const m = document.querySelector('.metrics');
    if (m) {
      const cs = getComputedStyle(m);
      res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
      res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
    }
    const btns = Array.from(document.querySelectorAll('button, a'));
    res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent || '').trim());
    res.entries = document.querySelectorAll('.entry').length;
    res.theme = document.documentElement.getAttribute('data-theme');
    res.bg = getComputedStyle(document.body).backgroundColor;
    res.has_theme_toggle = !!document.querySelector('#themeToggle');
    return res;
  });
}

async function shoot(pw, name, { theme, colorScheme, view }) {
  const browser = await pw.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 1100 }, device_scale_factor: 2,
    locale: 'zh-CN', colorScheme: colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(PUBLISHED, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(2200);
  if (view === 'en') {
    // 切换英文原文视图
    await page.evaluate(() => {
      const b = document.querySelector('#viewToggle button[data-view="en"]') || document.querySelector('#viewToggle button:last-child');
      if (b) b.click();
    }).catch(() => {});
    await page.waitForTimeout(1200);
  }
  if (theme) {
    await page.click(`#themeToggle button[data-theme="${theme}"]`).catch(() => {});
    await page.waitForTimeout(1200);
  }
  const path = `${OUT}/${name}`;
  await page.screenshot({ path, full_page: false });
  const styles = await checkStyles(page);
  console.log(name, '=>', JSON.stringify(styles));
  await browser.close();
  return { file: path, styles };
}

(async () => {
  const report = {};
  report.light     = await shoot(chromium, 'patrol_1800_1124_light.png',      { theme: 'light', colorScheme: 'light' });
  report.dark      = await shoot(chromium, 'patrol_1800_1124_dark.png',       { theme: 'dark',  colorScheme: 'dark' });
  report.autoLight = await shoot(chromium, 'patrol_1800_1124_auto_light.png', { theme: 'auto',  colorScheme: 'light' });
  report.autoDark  = await shoot(chromium, 'patrol_1800_1124_auto_dark.png',  { theme: 'auto',  colorScheme: 'dark' });
  report.en        = await shoot(chromium, 'patrol_1800_1124_en.png',         { view: 'en', colorScheme: 'light' });
  console.log('\n=== 汇总 ===');
  console.log(JSON.stringify({
    entry_before_all_zero: Object.values(report).every(r => r.styles.entry_before_rules === 0),
    metrics_padding_all_zero: Object.values(report).every(r => r.styles.metrics_padding_all_zero === true),
    no_sync_button: Object.values(report).every(r => r.styles.sync_buttons.length === 0),
    auto_light_theme: report.autoLight.styles.theme,
    auto_dark_theme: report.autoDark.styles.theme,
    light_bg: report.light.styles.bg,
    dark_bg: report.dark.styles.bg,
  }, null, 2));
})();
