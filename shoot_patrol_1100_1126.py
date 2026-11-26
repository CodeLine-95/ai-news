import asyncio
from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"

async def shot(ctx, name, theme=None, mode=None):
    page = await ctx.new_page()
    await page.goto(URL, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(1500)
    if theme:
        await page.click(f'#themeToggle .seg-btn[data-theme="{theme}"]')
        await page.wait_for_timeout(700)
    if mode:
        await page.click(f'#viewToggle .seg-btn[data-mode="{mode}"]')
        await page.wait_for_timeout(500)
    await page.screenshot(path=f"{OUT}/{name}.png", full_page=False)
    await page.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        ctx_light = await b.new_context(viewport={"width": 1440, "height": 900}, color_scheme="light")
        await shot(ctx_light, "巡检截图-1100-1126-浅色", theme="light")
        await shot(ctx_light, "巡检截图-1100-1126-暗黑", theme="dark")
        await shot(ctx_light, "巡检截图-1100-1126-英文原文", theme="light", mode="en")
        await ctx_light.close()
        ctx_dark = await b.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        page = await ctx_dark.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(1200)
        await page.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page.wait_for_timeout(700)
        await page.screenshot(path=f"{OUT}/巡检截图-1100-1126-系统自动深色.png", full_page=False)
        await ctx_dark.close()
        await b.close()
        print("screenshots done")

asyncio.run(main())
