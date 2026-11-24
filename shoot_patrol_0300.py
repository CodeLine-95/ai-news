# -*- coding: utf-8 -*-
"""2026-11-25 03:00 巡检截图：线上站点浅色 / 暗黑 / 系统自动 + 英文原文。"""
import asyncio
import os

from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
PREFIX = "deliverable_1125_0300"


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        async def snap(name, scheme, theme=None, mode=None):
            ctx = await browser.new_context(color_scheme=scheme, viewport={"width": 1440, "height": 1000})
            pg = await ctx.new_page()
            await pg.goto(URL, wait_until="networkidle", timeout=60000)
            await pg.wait_for_timeout(1200)
            if theme:
                await pg.click(f'#themeToggle .seg-btn[data-theme="{theme}"]')
                await pg.wait_for_timeout(600)
            if mode:
                await pg.click(f'.seg-btn[data-mode="{mode}"]')
                await pg.wait_for_timeout(600)
            path = f"{OUT}/{PREFIX}_{name}.png"
            await pg.screenshot(path=path, full_page=False)
            print("saved", path)
            return pg

        pg = await snap("light", "light", "light")
        before = await pg.evaluate("""() => {
            const el = document.querySelector('.entry');
            if (!el) return 'no .entry';
            return getComputedStyle(el, '::before').content;
        }""")
        pad = await pg.evaluate("""() => {
            const el = document.querySelector('.metrics');
            if (!el) return 'no .metrics';
            const cs = getComputedStyle(el);
            return [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].join(' ');
        }""")
        sync_btn = await pg.evaluate("""() => /手动同步|sync now/i.test(document.body.innerText)""")
        count = await pg.evaluate("""() => document.querySelectorAll('.entry').length""")
        print("ENTRY_BEFORE_CONTENT:", before)
        print("METRICS_PADDING:", pad)
        print("SYNC_BUTTON:", sync_btn)
        print("VISIBLE_ENTRIES:", count)

        await snap("dark", "light", "dark")
        await snap("auto_light", "light", "auto")
        await snap("auto_dark", "dark", "auto")
        await snap("en", "light", "light", "en")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
