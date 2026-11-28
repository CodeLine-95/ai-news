// 22:00 例行巡检：六态截图 + 样式断言 + 系统自动动态切换实测
const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const LOCAL = 'http://127.0.0.1:8080/?sharecode=YM64NRHD37';
const ONLINE = 'https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37';
const OUT = '/workspace/ai-news/screenshots';
const STAMP = 'deliverable_1128_2200_patrol';

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
    res.theme_modes = Array.from(document.querySelectorAll('#themeToggle button')).map(b => b.dataset.theme);
    return res;
  });
}

async function openPage(pw, url, colorScheme) {
  const browser = await pw.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 1100 }, device_scale_factor: 2,
    locale: 'zh-CN', colorScheme: colorScheme || 'light',
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction("() => document.querySelectorAll('.entry').length > 3", { timeout: 60000 });
  await page.waitForTimeout(1800);
  return { browser, page };
}

async function shoot(pw, url, name, opts) {
  const { browser, page } = await openPage(pw, url, opts.colorScheme || 'light');
  if (opts.theme) {
    await page.click(`#themeToggle button[data-theme="${opts.theme}"]`).catch(() => {});
    await page.waitForTimeout(700);
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
  const fs = require('fs');
  if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });
  const r = {};
  r.light = await shoot(chromium, LOCAL, 'light', { theme: 'light', colorScheme: 'light' });
  r.dark = await shoot(chromium, LOCAL, 'dark', { theme: 'dark', colorScheme: 'dark' });

  // 系统自动：dark -> light -> dark 动态切换实测，并分别留图
  {
    const { browser, page } = await openPage(chromium, LOCAL, 'dark');
    await page.click('#themeToggle button[data-theme="auto"]').catch(() => {});
    await page.waitForTimeout(700);
    r.auto_dark = await checkStyles(page);
    r.auto_dark.dynamic = 'dark';
    await page.screenshot({ path: `${OUT}/${STAMP}_auto_dark.png`, full_page: false });
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForTimeout(1500);
    r.auto_light = await checkStyles(page);
    r.auto_light.dynamic = 'light';
    await page.screenshot({ path: `${OUT}/${STAMP}_auto_light.png`, full_page: false });
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.waitForTimeout(1500);
    r.auto_back_dark = await checkStyles(page);
    r.auto_back_dark.dynamic = 'dark';
    await browser.close();
    console.log('auto dynamic =>', JSON.stringify({
      dark: r.auto_dark.data_theme, light: r.auto_light.data_theme, back: r.auto_back_dark.data_theme,
    }));
  }

  r.en = await shoot(chromium, LOCAL, 'en', { theme: 'light', mode: 'en', colorScheme: 'light' });
  try { r.online = await shoot(chromium, ONLINE, 'online', { colorScheme: 'light' }); }
  catch (e) { r.online = { error: String(e).slice(0, 300) }; }

  r.assertions = {
    entry_before_rules: [r.light, r.dark, r.en, r.online].every(x => x.entry_before_rules === 0),
    metrics_padding_all_zero: [r.light, r.dark, r.en, r.online].every(x => x.metrics_padding_all_zero === true),
    no_sync_buttons: [r.light, r.dark, r.en, r.online].every(x => (x.sync_buttons || []).length === 0),
    theme_modes: ['dark', 'light', 'auto'].every(t => (r.light.theme_modes || []).includes(t)),
    auto_follows_system: r.auto_dark.data_theme === 'dark' && r.auto_light.data_theme === 'light' && r.auto_back_dark.data_theme === 'dark',
    online_entries_gt3: (r.online.entries || 0) > 3,
  };
  r.all_assertions_pass = Object.values(r.assertions).every(Boolean);
  fs.writeFileSync(`${OUT}/${STAMP}_checks.json`, JSON.stringify(r, null, 2));
  console.log('\nDONE', JSON.stringify({ assertions: r.assertions, all_pass: r.all_assertions_pass }));
  if (!r.all_assertions_pass) process.exit(2);
})().catch(e => { console.error('ERR', e); process.exit(1); });
