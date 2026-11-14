import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        # default (light) view
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="light")
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{OUT}/巡检截图-0803-默认浅色.png", full_page=False)
        # dark
        await page.click('#themeToggle .seg-btn[data-theme="dark"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}/巡检截图-0803-暗黑.png", full_page=False)
        # auto (light system)
        await page.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}/巡检截图-0803-系统自动.png", full_page=False)
        # english original + back to light
        await page.click('#themeToggle .seg-btn[data-theme="light"]')
        await page.click('#viewToggle .seg-btn[data-mode="en"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}/巡检截图-0803-英文原文视图.png", full_page=False)
        await ctx.close()
        # auto with dark system scheme
        ctx2 = await browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        page2 = await ctx2.new_page()
        await page2.goto(URL, wait_until="networkidle")
        await page2.wait_for_timeout(1200)
        await page2.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page2.wait_for_timeout(800)
        await page2.screenshot(path=f"{OUT}/巡检截图-0803-系统自动-深.png", full_page=False)
        await ctx2.close()
        await browser.close()
        print("screenshots done")

asyncio.run(main())
