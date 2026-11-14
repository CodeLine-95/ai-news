import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="light")
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1800)
        await page.screenshot(path=f"{OUT}/巡检截图-0917-默认浅色.png", full_page=False)
        await page.click('#themeToggle .seg-btn[data-theme="dark"]')
        await page.wait_for_timeout(900)
        await page.screenshot(path=f"{OUT}/巡检截图-0917-暗黑.png", full_page=False)
        await page.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page.wait_for_timeout(900)
        await page.screenshot(path=f"{OUT}/巡检截图-0917-系统自动.png", full_page=False)
        await page.click('#themeToggle .seg-btn[data-theme="light"]')
        await page.click('#viewToggle .seg-btn[data-mode="en"]')
        await page.wait_for_timeout(900)
        await page.screenshot(path=f"{OUT}/巡检截图-0917-英文原文视图.png", full_page=False)
        await ctx.close()
        ctx2 = await browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        page2 = await ctx2.new_page()
        await page2.goto(URL, wait_until="networkidle")
        await page2.wait_for_timeout(1500)
        await page2.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page2.wait_for_timeout(900)
        await page2.screenshot(path=f"{OUT}/巡检截图-0917-系统自动-深.png", full_page=False)
        await ctx2.close()
        await browser.close()
        print("screenshots done")

asyncio.run(main())
