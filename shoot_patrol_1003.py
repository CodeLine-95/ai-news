import asyncio, os, json
from playwright.async_api import async_playwright

OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8080/"
TS = "1003"

async def assert_css(pg):
    res = await pg.evaluate("""() => {
        const any_before = [...document.querySelectorAll('.entry')].some(e => {
            const cs = getComputedStyle(e, '::before');
            return cs.content && cs.content !== 'none' && cs.content !== 'normal';
        });
        const m = document.querySelector('.metrics');
        const mp = m ? getComputedStyle(m).padding : 'N/A';
        const btn = [...document.querySelectorAll('button, .seg-btn')].find(b => /同步/.test(b.textContent||''));
        return { entry_before: any_before, metrics_padding: mp, sync_button: !!btn };
    }""")
    return res

async def shoot(p, theme, path, orig_view=False):
    b = await p.chromium.launch(args=["--no-sandbox"])
    pg = await b.new_page(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)
    await pg.goto(URL, wait_until="networkidle", timeout=30000)
    await pg.wait_for_selector(".entry", timeout=20000)
    await pg.evaluate(f"localStorage.setItem('themeMode','{theme}');")
    tbtn = pg.locator(f"#themeToggle .seg-btn[data-theme='{theme}']")
    if await tbtn.count():
        await tbtn.first.click()
    if orig_view:
        vbtn = pg.locator("#viewToggle .seg-btn[data-view='en']")
        if await vbtn.count():
            await vbtn.first.click()
    await pg.wait_for_timeout(700)
    await pg.screenshot(path=path, full_page=False)
    n = await pg.locator(".entry").count()
    css = await assert_css(pg)
    await b.close()
    return n, css

async def main():
    async with async_playwright() as p:
        ne, cs1 = await shoot(p, "light", f"{OUT}/patrol_{TS}_light.png")
        nd, cs2 = await shoot(p, "dark", f"{OUT}/patrol_{TS}_dark.png")
        na, cs3 = await shoot(p, "auto", f"{OUT}/patrol_{TS}_auto.png")
        ne2, cs4 = await shoot(p, "light", f"{OUT}/patrol_{TS}_en.png", orig_view=True)
        summary = {"entries_light": ne, "entries_dark": nd, "entries_auto": na,
                   "css_light": cs1, "css_dark": cs2, "css_auto": cs3, "css_en": cs4}
        print("OK", json.dumps(summary, ensure_ascii=False))

asyncio.run(main())
