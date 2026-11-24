import asyncio
from playwright.async_api import async_playwright
LOCAL = "http://127.0.0.1:8080/"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"
SHOTS = [
    ("patrol_1200_local_light.png", LOCAL, "light", "zh", None),
    ("patrol_1200_local_dark.png", LOCAL, "dark", "zh", None),
    ("patrol_1200_local_auto_light.png", LOCAL, "auto", "zh", "light"),
    ("patrol_1200_local_auto_dark.png", LOCAL, "auto", "zh", "dark"),
    ("patrol_1200_local_en.png", LOCAL, "light", "en", None),
    ("patrol_1200_online.png", ONLINE, "light", "zh", None),
]
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        for fname, url, theme, view, prefers in SHOTS:
            ctx = await browser.new_context(viewport={"width": 1400, "height": 950})
            page = await ctx.new_page()
            if prefers:
                await page.emulate_media(color_scheme=prefers)
            await page.add_init_script(
                f"localStorage.setItem('themeMode','{theme}');"
                f"localStorage.setItem('viewMode','{view}');"
            )
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
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
            print(f"{fname}: total={total} view={view} theme={theme} prefers={prefers}")
            await ctx.close()
        await browser.close()
    print("DONE")
asyncio.run(main())
