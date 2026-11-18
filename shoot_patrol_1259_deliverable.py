# -*- coding: utf-8 -*-
"""12:59 每小时例行巡检：五态截图 + 样式/主题断言实测。"""
import asyncio, os
from playwright.async_api import async_playwright

OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
LOCAL = "http://127.0.0.1:8080/"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
TAG = "deliverable_1118_1259"


async def open_page(p, url, scheme=None):
    b = await p.chromium.launch(args=["--no-sandbox"])
    pg = await b.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=2)
    if scheme:
        await pg.emulate_media(color_scheme=scheme)
    await pg.goto(url, wait_until="networkidle", timeout=60000)
    await pg.wait_for_selector(".entry", timeout=30000)
    await pg.wait_for_timeout(500)
    return b, pg


async def assertions(pg):
    before = await pg.evaluate(
        "() => { const el=document.querySelector('.entry'); if(!el) return 'no-entry';"
        "return getComputedStyle(el,'::before').content; }")
    pad = await pg.evaluate(
        "() => { const el=document.querySelector('.metrics'); if(!el) return 'no-metrics';"
        "return getComputedStyle(el).padding; }")
    sync = await pg.locator("button:has-text('同步')").count()
    entries = await pg.locator(".entry").count()
    theme = await pg.evaluate("() => document.documentElement.getAttribute('data-theme')")
    return dict(entries=entries, before=before, pad=pad, sync_btn=sync, theme=theme)


async def main():
    async with async_playwright() as p:
        results = {}
        for theme, scheme in [("light", "light"), ("dark", "dark"), ("auto", "dark")]:
            b, pg = await open_page(p, LOCAL, scheme)
            btn = pg.locator(f"#themeToggle .seg-btn[data-theme='{theme}']")
            if await btn.count():
                await btn.first.click()
            await pg.wait_for_timeout(600)
            await pg.screenshot(path=f"{OUT}/{TAG}_{theme}.png", full_page=False)
            results[theme] = await assertions(pg)
            await b.close()

        # auto 跟随系统动态切换验证（不点击，纯 media 变化）
        b, pg = await open_page(p, LOCAL, "dark")
        await pg.locator("#themeToggle .seg-btn[data-theme='auto']").first.click()
        await pg.wait_for_timeout(300)
        auto_dark = await pg.evaluate("() => document.documentElement.getAttribute('data-theme')")
        await pg.emulate_media(color_scheme="light")
        await pg.wait_for_timeout(300)
        auto_light = await pg.evaluate("() => document.documentElement.getAttribute('data-theme')")
        results["auto_follow"] = dict(system_dark=auto_dark, system_light=auto_light)
        await b.close()

        # 英文原文视图
        b, pg = await open_page(p, LOCAL, "light")
        await pg.locator("#viewToggle .seg-btn[data-mode='en']").first.click()
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=f"{OUT}/{TAG}_en.png", full_page=False)
        results["en"] = await assertions(pg)
        await b.close()

        # 线上实拍
        b, pg = await open_page(p, ONLINE, "light")
        await pg.locator("#themeToggle .seg-btn[data-theme='light']").first.click()
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=f"{OUT}/{TAG}_online.png", full_page=False)
        results["online"] = await assertions(pg)
        await b.close()

        for k, v in results.items():
            print(k, v)

asyncio.run(main())
