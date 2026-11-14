import asyncio
from playwright.async_api import async_playwright

URL = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"

async def shot(page, theme, name):
    await page.add_init_script(f"localStorage.setItem('themeMode','{theme}')")
    await page.goto(URL, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(4000)
    await page.screenshot(path=f"{OUT}/{name}.png", full_page=False)
    has_sync = await page.query_selector("button.sync, .sync-btn, #syncBtn")
    entry_before = await page.evaluate("() => { const s=[...document.styleSheets].flatMap(x=>{try{return [...x.cssRules]}catch(e){return[]}}); return s.filter(r=>r.selectorText && r.selectorText.includes('.entry::before')).length }")
    metrics_pad = await page.evaluate("() => { const el=document.querySelector('.metrics'); if(!el) return 'no .metrics'; return getComputedStyle(el).padding }")
    theme_now = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    print(f"[{name}] theme_effective={theme_now} entry::before_rules={entry_before} metrics_padding={metrics_pad} sync_btn={'YES' if has_sync else 'none'}")

async def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1280,"height":900})
        await shot(pg, "dark", "live_dark")
        await shot(pg, "light", "live_light")
        await shot(pg, "auto", "live_auto")
        await b.close()

asyncio.run(main())
print("DONE")
