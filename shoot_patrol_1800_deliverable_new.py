# -*- coding: utf-8 -*-
"""18:00 例行巡检交付截图：浅色/暗黑/系统自动/英文原文 + 线上域名。"""
import asyncio
import os
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
PREFIX = "deliverable_1121_1800"


async def set_theme(page, theme):
    await page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
    await page.wait_for_timeout(700)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])

        # ---- 本地：系统自动(dark) ----
        ctx_d = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="dark")
        pg = await ctx_d.new_page()
        await pg.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await pg.wait_for_timeout(1500)
        await set_theme(pg, "auto")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_auto_dark.png")
        theme_attr = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
        await ctx_d.close()

        # ---- 本地：系统自动(light) ----
        ctx_l = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        pg = await ctx_l.new_page()
        await pg.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await pg.wait_for_timeout(1500)
        await set_theme(pg, "auto")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_auto_light.png")
        await set_theme(pg, "light")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_light.png")
        await set_theme(pg, "dark")
        await pg.screenshot(path=f"{OUT}/{PREFIX}_dark.png")

        # ---- 样式断言 ----
        checks = await pg.evaluate("""() => {
            const before = [...document.querySelectorAll('.entry::before')].length;
            const ms = document.querySelector('.metrics');
            const cs = ms ? getComputedStyle(ms) : null;
            return {
                entryBeforeRules: before,
                metricsPadding: cs ? [cs.paddingTop,cs.paddingRight,cs.paddingBottom,cs.paddingLeft] : null,
                syncBtns: document.querySelectorAll('[id*=sync],[class*=sync-btn],button').length
            };
        }""")

        # ---- 英文原文视图 ----
        await set_theme(pg, "light")
        await pg.evaluate("window.setView && window.setView('en')")
        await pg.evaluate("""() => {
            const b = document.querySelector('#viewToggle .seg-btn[data-mode="en"]');
            if (b) b.click();
        }""")
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=f"{OUT}/{PREFIX}_en.png")
        await ctx_l.close()

        # ---- 线上域名(浅色) ----
        ctx_o = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        po = await ctx_o.new_page()
        await po.goto(ONLINE, wait_until="networkidle", timeout=45000)
        await po.wait_for_timeout(2000)
        await po.evaluate("document.documentElement.setAttribute('data-theme','light')")
        await po.wait_for_timeout(700)
        await po.screenshot(path=f"{OUT}/{PREFIX}_online.png")
        online_entries = await po.evaluate("document.querySelectorAll('.entry').length")
        await ctx_o.close()

        await browser.close()
        print("SCREENSHOTS_OK", PREFIX)
        print("theme_attr_after_auto_dark=", theme_attr)
        print("checks=", checks)
        print("online_entries=", online_entries)


asyncio.run(main())
