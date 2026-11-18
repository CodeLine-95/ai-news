# -*- coding: utf-8 -*-
"""16:00 例行巡检交付截图：本地三态主题 + 英文原文视图 + 线上域名。"""
import asyncio
import os
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)


async def apply_theme(page, theme):
    await page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
    await page.wait_for_timeout(900)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])

        # 本地四态
        page = await browser.new_page(viewport={"width": 1440, "height": 1100})
        await page.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await page.wait_for_timeout(2000)

        await apply_theme(page, "light")
        await page.screenshot(path=f"{OUT}/deliverable_1118_1600_light.png")

        await apply_theme(page, "dark")
        await page.screenshot(path=f"{OUT}/deliverable_1118_1600_dark.png")

        await apply_theme(page, "auto")
        await page.screenshot(path=f"{OUT}/deliverable_1118_1600_auto.png")

        await apply_theme(page, "light")
        await page.evaluate("window.setView && window.setView('en')")
        await page.evaluate("""() => {
            const b = document.querySelector('#viewToggle .seg-btn[data-mode=\"en\"]');
            if (b) b.click();
        }""")
        await page.wait_for_timeout(900)
        await page.screenshot(path=f"{OUT}/deliverable_1118_1600_en.png")
        await page.close()

        # 线上域名截图（浅色）
        ctx = await browser.new_context(viewport={"width": 1440, "height": 1100}, color_scheme="light")
        p2 = await ctx.new_page()
        await p2.goto(ONLINE, wait_until="networkidle", timeout=45000)
        await p2.wait_for_timeout(2000)
        await p2.evaluate("document.documentElement.setAttribute('data-theme','light')")
        await p2.wait_for_timeout(900)
        await p2.screenshot(path=f"{OUT}/deliverable_1118_1600_online.png")
        entries = await p2.evaluate("document.querySelectorAll('.entry').length")
        await ctx.close()
        await browser.close()
        print("交付截图完成，线上 entries =", entries)


asyncio.run(main())
