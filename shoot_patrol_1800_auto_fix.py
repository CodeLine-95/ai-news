# -*- coding: utf-8 -*-
"""用真实点击“系统”按钮的方式验证 auto 主题跟随（不绕过 setTheme 逻辑）。"""
import asyncio
import os
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
PREFIX = "deliverable_1121_1800"


async def click_theme(page, theme):
    await page.click(f'#themeToggle .seg-btn[data-theme="{theme}"]')
    await page.wait_for_timeout(700)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        results = {}

        for scheme, label in (("dark", "auto_dark"), ("light", "auto_light")):
            ctx = await browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme=scheme)
            pg = await ctx.new_page()
            await pg.goto(LOCAL, wait_until="networkidle", timeout=40000)
            await pg.wait_for_timeout(1200)
            # 真实点击“系统”按钮
            await click_theme(pg, "auto")
            eff = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
            active = await pg.evaluate("""() => {
                const b=document.querySelector('#themeToggle .seg-btn.active');
                return b ? b.dataset.theme : null;
            }""")
            bg = await pg.evaluate("getComputedStyle(document.body).backgroundColor")
            await pg.screenshot(path=f"{OUT}/{PREFIX}_{label}.png")
            results[label] = {"system_scheme": scheme, "effective_theme": eff, "active_ctrl": active, "body_bg": bg}
            await ctx.close()

        await browser.close()
        print("AUTO_FIX_OK")
        for k, v in results.items():
            print(k, "=>", v)


asyncio.run(main())
