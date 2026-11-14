const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const URL = 'http://127.0.0.1:8080';
const OUT = '/workspace/ai-news/screenshots';
const TAG = '1800';

(async () => {
  const fs = require('fs');
  if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 1600 } });
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('.entry', { timeout: 15000 });
  await page.waitForTimeout(1500);

  const res = await page.evaluate(() => {
    let beforeCount = 0;
    let metricsPad = null;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) {
        if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
        if (rule.selectorText === '.metrics') metricsPad = rule.style.padding;
      }
    }
    const m = document.querySelector('.metrics');
    const cs = getComputedStyle(m);
    return {
      entry_before_rules: beforeCount,
      metrics_padding_all_zero: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0),
      metrics_rule_padding: metricsPad,
      entries: document.querySelectorAll('.entry').length,
      theme_btns: Array.from(document.querySelectorAll('#themeToggle .seg-btn')).map(b => b.dataset.theme),
      view_btns: Array.from(document.querySelectorAll('#viewToggle .seg-btn')).map(b => b.dataset.view),
      sync_btns: document.querySelectorAll('[class*="sync"]').length,
    };
  });
  console.log('ASSERTIONS', JSON.stringify(res));

  await page.evaluate(() => { localStorage.setItem('themeMode','auto'); document.documentElement.setAttribute('data-theme', window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'); });
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/巡检截图-${TAG}-系统自动.png`, fullPage: false });

  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/巡检截图-${TAG}-暗黑.png`, fullPage: false });

  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/巡检截图-${TAG}-默认浅色.png`, fullPage: false });

  await page.evaluate(() => { const b = document.querySelector('#viewToggle .seg-btn[data-mode="en"]'); if (b) b.click(); });
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/巡检截图-${TAG}-英文原文视图.png`, fullPage: false });

  await browser.close();
  console.log('screenshots saved');
})();
