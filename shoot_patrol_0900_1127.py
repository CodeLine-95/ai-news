# -*- coding: utf-8 -*-
"""2026-11-27 09:00 例行巡检：五态截图 + CSS 规则断言。"""
import asyncio, json
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
STAMP = "deliverable_1127_0900"

async def check_styles(page):
    return await page.evaluate("""() => {
      const res = {};
      let beforeCount = 0;
      for (const sheet of document.styleSheets) {
        let rules; try { rules = sheet.cssRules; } catch(e) { continue; }
        for (const r of rules) if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++;
      }
      res.entry_before_rules = beforeCount;
      const e = document.querySelector('.entry');
      res.entry_before_content = e ? getComputedStyle(e, '::before').content : '(none)';
      const m = document.querySelector('.metrics');
      if (m) {
        const cs = getComputedStyle(m);
        const pads = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
        res.metrics_padding = pads;
        res.metrics_padding_all_zero = pads.every(v => parseFloat(v) === 0);
      }
      const btns = Array.from(document.querySelectorAll('button, a'));
      res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent||'')).map(b => (b.textContent||'').trim());
      res.entries = document.querySelectorAll('.entry').length;
      res.data_theme = document.documentElement.getAttribute('data-theme');
      return res;
    }""")

async def shoot(browser, name, opts):
    ctx = await browser.new_context(viewport={"width":1440,"height":1100}, device_scale_factor=2,
                                    locale="zh-CN", color_scheme=opts.get("scheme","light"))
    page = await ctx.new_page()
    await page.goto(opts["url"], wait_until="networkidle", timeout=90000)
    await page.wait_for_function("() => document.querySelectorAll('.entry').length > 3", timeout=60000)
    await page.wait_for_timeout(2000)
    if opts.get("theme"):
        try:
            await page.click(f'#themeToggle button[data-theme="{opts["theme"]}"]', timeout=5000)
        except Exception:
            pass
        await page.wait_for_timeout(800)
    if opts.get("view"):
        try:
            await page.click(f'#viewToggle button[data-view="{opts["view"]}"]', timeout=5000)
        except Exception:
            pass
        await page.wait_for_timeout(800)
    path = f"{OUT}/{STAMP}_{name}.png"
    await page.screenshot(path=path, full_page=False)
    s = await check_styles(page)
    print(name, "=>", path, "|", json.dumps(s, ensure_ascii=False), flush=True)
    await ctx.close()
    return s

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        results = {}
        results["light"] = await shoot(browser, "light", {"url":LOCAL,"theme":"light","scheme":"light"})
        results["dark"]  = await shoot(browser, "dark",  {"url":LOCAL,"theme":"dark","scheme":"dark"})
        results["auto"]  = await shoot(browser, "auto",  {"url":LOCAL,"theme":"auto","scheme":"dark"})
        results["en"]    = await shoot(browser, "en",    {"url":LOCAL,"theme":"light","view":"en","scheme":"light"})
        results["online"]= await shoot(browser, "online",{"url":ONLINE,"scheme":"light"})
        await browser.close()
        with open(f"{OUT}/{STAMP}_checks.json","w",encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\nDONE", json.dumps(results, ensure_ascii=False), flush=True)

asyncio.run(main())
