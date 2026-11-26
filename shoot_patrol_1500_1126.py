# -*- coding: utf-8 -*-
"""15:00 巡检截图 + 样式实测：浅色/暗黑/系统自动三主题 + 英文原文视图。"""
import asyncio, json, os
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)

CHECK = """() => {
  const res = {};
  let beforeCount = 0;
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const r of rules) {
      if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++;
    }
  }
  res.entry_before_rules = beforeCount;
  const entry = document.querySelector('.entry');
  res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(none)';
  const m = document.querySelector('.metrics');
  if (m) {
    const cs = getComputedStyle(m);
    res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
    res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
  }
  res.entries = document.querySelectorAll('.entry').length;
  res.sync_buttons = Array.from(document.querySelectorAll('button'))
    .filter(b => /同步|sync|refresh|刷新/i.test(b.textContent)).length;
  return res;
}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1366, "height": 1800})
        await pg.goto(URL, wait_until="networkidle", timeout=30000)
        await pg.wait_for_timeout(2500)
        results = {}
        for theme, name in [("light", "patrol_1500_1126_light"),
                            ("dark", "patrol_1500_1126_dark"),
                            ("auto", "patrol_1500_1126_auto")]:
            await pg.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
            await pg.wait_for_timeout(700)
            await pg.screenshot(path=os.path.join(OUT, name + ".png"), full_page=False)
            results[theme] = await pg.evaluate(CHECK)
        # 英文原文视图
        try:
            await pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
            btns = await pg.query_selector_all("#viewToggle .seg-btn, .view-btn, button")
            for btn in btns:
                txt = (await btn.inner_text() or "").strip()
                if txt in ("原文", "EN", "English", "英文"):
                    await btn.click()
                    await pg.wait_for_timeout(1000)
                    break
            await pg.screenshot(path=os.path.join(OUT, "patrol_1500_1126_en.png"), full_page=False)
        except Exception as e:
            results["en_view_note"] = str(e)
        await b.close()
        print(json.dumps(results, ensure_ascii=False, indent=2))

asyncio.run(main())
