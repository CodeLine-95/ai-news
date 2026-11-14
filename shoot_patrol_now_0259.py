import asyncio
from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"

async def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Light
        ctx = await browser.new_context(color_scheme="light")
        pg = await ctx.new_page()
        await pg.goto(URL, wait_until="networkidle", timeout=60000)
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f"{OUT}/patrol_light.png", full_page=False)
        # Dark
        ctx2 = await browser.new_context(color_scheme="dark")
        pg2 = await ctx2.new_page()
        await pg2.goto(URL, wait_until="networkidle", timeout=60000)
        await pg2.wait_for_timeout(1500)
        # try clicking a dark toggle if present
        try:
            await pg2.click("text=暗黑", timeout=3000)
        except Exception:
            pass
        await pg2.wait_for_timeout(1500)
        await pg2.screenshot(path=f"{OUT}/patrol_dark.png", full_page=False)
        # Auto (follow system)
        ctx3 = await browser.new_context(color_scheme="dark")
        pg3 = await ctx3.new_page()
        await pg3.goto(URL, wait_until="networkidle", timeout=60000)
        await pg3.wait_for_timeout(1500)
        try:
            await pg3.click("text=系统自动", timeout=3000)
        except Exception:
            pass
        await pg3.wait_for_timeout(1500)
        await pg3.screenshot(path=f"{OUT}/patrol_auto.png", full_page=False)
        # CSS assertions
        await pg.goto(URL, wait_until="networkidle", timeout=60000)
        await pg.wait_for_timeout(1500)
        entry_before = await pg.evaluate("""() => {
            const el = document.querySelector('.entry');
            if (!el) return 'no .entry';
            const cs = getComputedStyle(el, '::before');
            return cs.content;
        }""")
        metrics_padding = await pg.evaluate("""() => {
            const el = document.querySelector('.metrics');
            if (!el) return 'no .metrics';
            return getComputedStyle(el).padding;
        }""")
        has_sync_btn = await pg.evaluate("""() => {
            const txt = document.body.innerText;
            return /手动同步|同步按钮|sync/i.test(txt);
        }""")
        print("ENTRY_BEFORE_CONTENT:", entry_before)
        print("METRICS_PADDING:", metrics_padding)
        print("HAS_MANUAL_SYNC_BTN:", has_sync_btn)
        await browser.close()

asyncio.run(main())
