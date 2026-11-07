import asyncio
from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/巡检截图-2200"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2500)
        await page.wait_for_selector("#newsRoot .entry", timeout=30000)
        await page.wait_for_timeout(1500)

        # 默认浅色
        await page.click('#themeToggle .seg-btn[data-theme="light"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}-默认浅色.png", full_page=False)
        await page.screenshot(path=f"{OUT}-默认浅色-全页.png", full_page=True)

        # 暗黑
        await page.click('#themeToggle .seg-btn[data-theme="dark"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}-暗黑.png", full_page=False)

        # 英文原文视图
        await page.click('#viewToggle .seg-btn[data-mode="en"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}-英文原文视图.png", full_page=False)

        # 系统自动（回到中文）
        await page.click('#viewToggle .seg-btn[data-mode="zh"]')
        await page.click('#themeToggle .seg-btn[data-theme="auto"]')
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{OUT}-系统自动.png", full_page=False)

        # 计数
        count = await page.eval_on_selector_all("#newsRoot .entry", "els => els.length")
        title = await page.title()
        print("entries:", count, "title:", title)
        await browser.close()

asyncio.run(main())
