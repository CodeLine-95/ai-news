import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080"
OUT = "/workspace/ai-news"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)

        def click_theme(t):
            return page.click(f'#themeToggle .seg-btn[data-theme="{t}"]')

        def click_view(v):
            # view buttons: try data-view then text
            return page.click(f'#viewToggle .seg-btn[data-view="{v}"]')

        async def shot(name):
            await page.wait_for_timeout(1200)
            path = f"{OUT}/{name}.png"
            await page.screenshot(path=path, full_page=False)
            print("saved", path)

        # 1) default light (zh)
        await click_theme("light")
        await shot("巡检截图-2259-默认浅色")

        # 2) dark (zh)
        await click_theme("dark")
        await shot("巡检截图-2259-暗黑")

        # 3) auto (zh)
        await click_theme("auto")
        await shot("巡检截图-2259-系统自动")

        # 4) english original view (light)
        await click_theme("light")
        try:
            await click_view("en")
        except Exception as e:
            # fallback: click by text
            await page.click("#viewToggle .seg-btn:has-text('英文')")
        await shot("巡检截图-2259-英文原文视图")

        # assertions
        entry_before = await page.evaluate(
            "getComputedStyle(document.querySelector('.entry')||document.body,'::before').content"
        )
        metrics_pad = await page.evaluate(
            "(()=>{const m=document.querySelector('.metrics');return m?getComputedStyle(m).padding:'NONE';})()"
        )
        sync_btn = await page.evaluate(
            "document.querySelectorAll('button').length + ' buttons; sync? ' + !!document.querySelector('[class*=sync]')"
        )
        print("entry::before content:", entry_before)
        print("metrics padding:", metrics_pad)
        print("buttons:", sync_btn)

        await browser.close()

asyncio.run(main())
