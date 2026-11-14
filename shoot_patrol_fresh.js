const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');
const URL = 'http://127.0.0.1:8080';
const TS = new Date().toISOString().replace(/[:.]/g,'-').slice(0,16);
const OUT = '/workspace/ai-news/patrol_' + TS;
const fs = require('fs');
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 2000 } });
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('.entry', { timeout: 20000 });
  await page.waitForTimeout(2000);

  const res = await page.evaluate(() => {
    let beforeCount = 0;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) {
        if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
      }
    }
    const m = document.querySelector('.metrics');
    const cs = getComputedStyle(m);
    const page2 = document.querySelector('.entry .page-zh, .entry');
    return {
      entry_before_rules: beforeCount,
      metrics_padding_all_zero: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0),
      metrics_padding: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft],
      entries: document.querySelectorAll('.entry').length,
      theme_btns: Array.from(document.querySelectorAll('#themeToggle .seg-btn')).map(b => b.dataset.theme),
      view_btns: Array.from(document.querySelectorAll('#viewToggle .seg-btn')).map(b => b.dataset.view),
      sync_btns: document.querySelectorAll('[class*="sync"]').length,
    };
  });
  console.log('ASSERTIONS', JSON.stringify(res));

  // 默认浅色
  await page.evaluate(() => { localStorage.setItem('themeMode','light'); document.documentElement.setAttribute('data-theme','light'); });
  await page.waitForTimeout(800);
  await page.screenshot({ path: OUT + '/light.png', fullPage: false });

  // 暗黑
  await page.evaluate(() => { localStorage.setItem('themeMode','dark'); document.documentElement.setAttribute('data-theme','dark'); });
  await page.waitForTimeout(800);
  await page.screenshot({ path: OUT + '/dark.png', fullPage: false });

  await browser.close();
  console.log('OUTDIR', OUT);
})();
