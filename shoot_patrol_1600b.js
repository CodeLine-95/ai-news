const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright');

const URL = 'http://127.0.0.1:8080';
const OUT = '/workspace/ai-news/screenshots';

(async () => {
  const fs = require('fs');
  if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 1600 } });
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('.entry', { timeout: 15000 });
  await page.waitForTimeout(1500);

  // assertions
  const res = await page.evaluate(() => {
    let beforeCount = 0;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
    }
    const m = document.querySelector('.metrics');
    const cs = getComputedStyle(m);
    return {
      entry_before_rules: beforeCount,
      metrics_padding_all_zero: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0),
      entries: document.querySelectorAll('.entry').length,
      theme_btns: Array.from(document.querySelectorAll('#themeToggle .seg-btn')).map(b => b.dataset.theme),
    };
  });
  console.log('ASSERTIONS', JSON.stringify(res));

  // dark (default)
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/patrol_dark.png`, fullPage: false });

  // light
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/patrol_light.png`, fullPage: false });

  await browser.close();
  console.log('screenshots saved');
})();
