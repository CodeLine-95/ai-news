# -*- coding: utf-8 -*-
"""15:00 例行巡检：五态截图 + 样式实测（本地 + 线上）。"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/"
DOMAIN = "https://a7888a7e046ffc95b.app.workbuddy.host"
SHARE = "YM64NRHD37"
ONLINE = f"{DOMAIN}/?sharecode={SHARE}"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)

STYLE_JS = """() => {
  const res = {};
  let beforeCount = 0, beforeContents = [];
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const r of rules) {
      if (r.selectorText && r.selectorText.includes('.entry::before')) {
        beforeCount++; beforeContents.push(r.style && r.style.content);
      }
    }
  }
  res.entry_before_rules = beforeCount;
  const entry = document.querySelector('.entry');
  res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no .entry)';
  const m = document.querySelector('.metrics');
  if (m) {
    const cs = getComputedStyle(m);
    res.metrics_padding = {top: cs.paddingTop, right: cs.paddingRight,
      bottom: cs.paddingBottom, left: cs.paddingLeft};
    res.metrics_padding_all_zero = ['top','right','bottom','left']
      .map(k => parseFloat(res.metrics_padding[k]) === 0).every(Boolean);
  }
  const btns = Array.from(document.querySelectorAll('button, a'));
  res.sync_buttons = btns.filter(b => /同步数据|手动同步|sync now/i.test(b.textContent||''))
    .map(b => (b.textContent||'').trim());
  res.entries = document.querySelectorAll('.entry').length;
  res.theme_attr = document.documentElement.getAttribute('data-theme');
  res.active_theme_btn = (document.querySelector('#themeToggle .seg-btn.active')||{}).textContent;
  res.active_view_btn = (document.querySelector('#viewToggle .seg-btn.active')||{}).textContent;
  res.bg = getComputedStyle(document.body).backgroundColor;
  res.title = document.title;
  return res;
}"""

async def new_page(pw, url, scheme="light"):
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    ctx = await browser.new_context(viewport={"width": 1440, "height": 1000},
        device_scale_factor=2, locale="zh-CN", color_scheme=scheme)
    page = await ctx.new_page()
    await page.goto(url, wait_until="networkidle", timeout=90000)
    await page.wait_for_timeout(2500)
    return browser, page

async def main():
    result = {}
    async with async_playwright() as pw:
        browser, page = await new_page(pw, LOCAL)
        await page.click('#themeToggle .seg-btn[data-theme="light"]')
        await page.wait_for_timeout(700)
        result["light"] = await page.evaluate(STYLE_JS)
        await page.screenshot(path=f"{OUT}/deliverable_1121_1500_light.png")

        await page.click('#themeToggle .seg-btn[data-theme="dark"]')
        await page.wait_for_timeout(700)
        result["dark"] = await page.evaluate(STYLE_JS)
        await page.screenshot(path=f"{OUT}/deliverable_1121_1500_dark.png")

        await page.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page.wait_for_timeout(700)
        result["auto_light"] = await page.evaluate(STYLE_JS)
        await page.screenshot(path=f"{OUT}/deliverable_1121_1500_auto.png")
        await browser.close()

        browser2, page2 = await new_page(pw, LOCAL, scheme="dark")
        await page2.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page2.wait_for_timeout(700)
        result["auto_dark"] = await page2.evaluate(STYLE_JS)
        await browser2.close()

        browser3, page3 = await new_page(pw, LOCAL)
        await page3.click('#viewToggle .seg-btn[data-mode="en"]')
        await page3.wait_for_timeout(700)
        result["en_view"] = await page3.evaluate(STYLE_JS)
        await page3.screenshot(path=f"{OUT}/deliverable_1121_1500_en.png")
        await browser3.close()

        browser4, page4 = await new_page(pw, ONLINE)
        result["online"] = await page4.evaluate(STYLE_JS)
        await page4.screenshot(path=f"{OUT}/deliverable_1121_1500_online.png")
        await browser4.close()

    with open(f"{OUT}/deliverable_1121_1500_checks.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

asyncio.run(main())
