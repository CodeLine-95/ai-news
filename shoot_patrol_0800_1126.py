# -*- coding: utf-8 -*-
"""08:00 例行巡检交付截图：浅色/暗黑/系统自动/英文原文 + 线上域名 + 样式断言。"""
import asyncio
import os
import json
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
PREFIX = "patrol_0800_1126"


async def set_theme(page, theme):
    await page.evaluate(
        "t => { const b = document.querySelector('#themeToggle .seg-btn[data-theme=\"' + t + '\"]');"
        " if (b) b.click(); }", theme)
    await page.wait_for_timeout(700)


async def main():
    result = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])

        ctx_d = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="dark")
        pg = await ctx_d.new_page()
        await pg.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await pg.wait_for_timeout(1500)
        await set_theme(pg, "auto")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_auto_dark.png")
        result["auto_dark_theme"] = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
        await ctx_d.close()

        ctx_l = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        pg = await ctx_l.new_page()
        await pg.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await pg.wait_for_timeout(1500)
        await set_theme(pg, "auto")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_auto_light.png")
        result["auto_light_theme"] = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
        await set_theme(pg, "light")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_light.png")
        await set_theme(pg, "dark")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_dark.png")

        result["checks"] = await pg.evaluate("""() => {
            let entryBeforeRules = 0;
            for (const sheet of document.styleSheets) {
                let rules;
                try { rules = sheet.cssRules; } catch (e) { continue; }
                for (const r of rules) {
                    if (r.selectorText && r.selectorText.includes('.entry::before')) entryBeforeRules++;
                }
            }
            const ms = document.querySelector('.metrics');
            const cs = ms ? getComputedStyle(ms) : null;
            const btns = [...document.querySelectorAll('button')];
            return {
                entryBeforeRules,
                metricsPadding: cs ? [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft] : null,
                syncBtns: btns.filter(b => /同步|sync/i.test(b.textContent + ' ' + b.id + ' ' + b.className)).length,
                themeBtns: btns.filter(b => ['dark','light','auto'].includes(b.dataset.theme)).map(b => b.dataset.theme),
                entries: document.querySelectorAll('.entry').length
            };
        }""")

        await set_theme(pg, "light")
        await pg.evaluate("""() => {
            const b = document.querySelector('#viewToggle .seg-btn[data-mode="en"]');
            if (b) b.click();
        }""")
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=f"{OUT}/{PREFIX}_en.png")
        await ctx_l.close()

        ctx_o = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        po = await ctx_o.new_page()
        await po.goto(ONLINE, wait_until="networkidle", timeout=45000)
        await po.wait_for_timeout(2000)
        await po.evaluate("document.querySelector('#themeToggle .seg-btn[data-theme=\"light\"]').click()")
        await po.wait_for_timeout(700)
        await po.screenshot(path=f"{OUT}/{PREFIX}_online.png")
        result["online_entries"] = await po.evaluate("document.querySelectorAll('.entry').length")
        await ctx_o.close()

        await browser.close()
    with open(f"{OUT}/{PREFIX}_checks.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("SCREENSHOTS_OK", PREFIX)
    print(json.dumps(result, ensure_ascii=False))


asyncio.run(main())
