# -*- coding: utf-8 -*-
"""2026-11-21 06:00 巡检交付截图 + 五态实测。"""
import asyncio
import os
import json
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
PREFIX = "deliverable_1121_0600f"
os.makedirs(OUT, exist_ok=True)


async def apply_theme(page, theme):
    await page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
    await page.wait_for_timeout(600)


async def probes(page):
    return await page.evaluate("""() => {
        const e = document.querySelector('.entry');
        const before = e ? getComputedStyle(e, '::before') : null;
        const m = document.querySelector('.metrics');
        const mp = m ? getComputedStyle(m) : null;
        const pads = mp ? [mp.paddingTop, mp.paddingRight, mp.paddingBottom, mp.paddingLeft] : [];
        const syncBtns = [...document.querySelectorAll('button,a,[role=button]')]
          .filter(b => /同步|sync|刷新|refresh/i.test((b.textContent||'')+(b.getAttribute('aria-label')||''))).length;
        const themeModes = [...new Set([...document.querySelectorAll('#themeToggle .seg-btn,[data-theme].seg-btn')]
          .map(b => b.getAttribute('data-theme')))].filter(Boolean);
        return {
          entryBeforeContent: before ? before.content : 'no-entry',
          entryBeforeDisplay: before ? before.display : 'n/a',
          metricsPadding: pads,
          syncBtns: syncBtns,
          themeModes: themeModes,
          entries: document.querySelectorAll('.entry').length
        };
    }""")


async def shot(browser, url, path, theme=None, view=None, ready_wait=2500):
    page = await browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=2)
    await page.goto(url, wait_until="networkidle", timeout=45000)
    await page.wait_for_selector(".entry", timeout=30000)
    await page.wait_for_timeout(ready_wait)
    if theme:
        await apply_theme(page, theme)
    if view:
        btn = page.locator(f"#viewToggle .seg-btn[data-view='{view}']")
        if await btn.count():
            await btn.first.click()
            await page.wait_for_timeout(500)
    await page.screenshot(path=path, full_page=False)
    result = await probes(page)
    await page.close()
    return result


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        r_light = await shot(browser, LOCAL, f"{OUT}/{PREFIX}_light.png", theme="light")
        r_dark = await shot(browser, LOCAL, f"{OUT}/{PREFIX}_dark.png", theme="dark")
        r_auto = await shot(browser, LOCAL, f"{OUT}/{PREFIX}_auto.png", theme="auto")
        r_en = await shot(browser, LOCAL, f"{OUT}/{PREFIX}_en.png", theme="light", view="en")
        r_online = await shot(browser, ONLINE, f"{OUT}/{PREFIX}_online.png", theme="dark", ready_wait=3500)
        await browser.close()
        summary = {
            "light": r_light, "dark": r_dark, "auto": r_auto,
            "en": r_en, "online": r_online
        }
        with open(f"{OUT}/{PREFIX}_checks.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print("OK", json.dumps(summary, ensure_ascii=False))


asyncio.run(main())
