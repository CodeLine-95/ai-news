import asyncio
from playwright.async_api import async_playwright
URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"
SHOTS = [
    ("巡检截图-0700-默认浅色.png", "light", "zh", None),
    ("巡检截图-0700-暗黑.png", "dark", "zh", None),
    ("巡检截图-0700-系统自动.png", "auto", "zh", "light"),
    ("巡检截图-0700-英文原文视图.png", "light", "en", None),
]
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for fname, theme, view, prefers in SHOTS:
            ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
            page = await ctx.new_page()
            if prefers:
                await page.emulate_media(color_scheme=prefers)
            await page.add_init_script(
                f"localStorage.setItem('themeMode','{theme}');"
                f"localStorage.setItem('viewMode','{view}');"
            )
            try:
                await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_function(
                    "() => { const e=document.getElementById('statTotal');"
                    " return e && e.textContent.trim()!=='0' && e.textContent.trim()!==''; }",
                    timeout=20000)
            except Exception as e:
                print("warn:", fname, repr(e))
            await page.wait_for_timeout(2500)
            try:
                total = await page.eval_on_selector("#statTotal", "el=>el.textContent.trim()")
            except Exception:
                total = "?"
            await page.screenshot(path=f"{OUT}/{fname}", full_page=False)
            print(f"{fname}: total={total} view={view} theme={theme}")
            await ctx.close()
        await browser.close()
    print("DONE")
asyncio.run(main())
