import asyncio
from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(URL, wait_until="networkidle", timeout=90000)
        await page.wait_for_function(
            "() => document.querySelectorAll('.entry').length > 3", timeout=60000
        )
        await page.wait_for_timeout(2000)

        async def shot(name):
            await page.wait_for_timeout(1000)
            path = f"{OUT}/{name}.png"
            await page.screenshot(path=path, full_page=False)
            print("saved", path)

        async def click_theme(t):
            await page.click(f'#themeToggle .seg-btn[data-theme="{t}"]')

        # 默认浅色 / 暗黑 / 系统自动
        await click_theme("light")
        await shot("巡检截图-2259-线上-默认浅色")
        await click_theme("dark")
        await shot("巡检截图-2259-线上-暗黑")
        await click_theme("auto")
        await shot("巡检截图-2259-线上-系统自动")

        # 英文原文视图
        await click_theme("light")
        await page.click('#viewToggle .seg-btn[data-mode="en"]')
        await shot("巡检截图-2259-线上-英文原文")

        styles = await page.evaluate(
            """() => {
              let before = 0;
              for (const s of document.styleSheets) {
                try { for (const r of s.cssRules) {
                  if (r.selectorText && r.selectorText.includes('.entry::before')) before++;
                }} catch (e) {}
              }
              const e = document.querySelector('.entry');
              const m = document.querySelector('.metrics');
              const cs = m ? getComputedStyle(m) : null;
              return {
                entryBeforeRules: before,
                entryBeforeContent: e ? getComputedStyle(e, '::before').content : 'NONE',
                metricsPadding: cs ? [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft] : 'NONE',
                entries: document.querySelectorAll('.entry').length,
                syncButtons: Array.from(document.querySelectorAll('button,a'))
                  .filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).length,
                themeModes: Array.from(document.querySelectorAll('#themeToggle .seg-btn'))
                  .map(b => b.getAttribute('data-theme')),
              };
            }"""
        )
        print("线上样式实测:", styles)
        await browser.close()


asyncio.run(main())
