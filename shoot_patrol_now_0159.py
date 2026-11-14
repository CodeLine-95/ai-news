import asyncio, os, json, datetime
from playwright.async_api import async_playwright

OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8080/"
TS = datetime.datetime.now().strftime("%m%d_%H%M")

async def assert_css(pg):
    return await pg.evaluate("""() => {
        const any_before = [...document.querySelectorAll('.entry')].some(e => {
            const cs = getComputedStyle(e, '::before');
            return cs.content && cs.content !== 'none' && cs.content !== 'normal';
        });
        const m = document.querySelector('.metrics');
        const mp = m ? getComputedStyle(m).padding : 'N/A';
        const btn = [...document.querySelectorAll('button, .seg-btn')].find(b => /同步/.test(b.textContent||''));
        return { entry_before: any_before, metrics_padding: mp, sync_button: !!btn };
    }""")

async def shoot(p, theme, path, orig_view=False):
    b = await p.chromium.launch(args=["--no-sandbox"])
    ctx = await b.new_context(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)
    pg = await ctx.new_page()
    await pg.goto(URL, wait_until="networkidle", timeout=30000)
    await pg.wait_for_selector(".entry", timeout=20000)
    tbtn = pg.locator(f"#themeToggle .seg-btn[data-theme='{theme}']")
    if await tbtn.count():
        await tbtn.first.click()
    if orig_view:
        vbtn = pg.locator("#viewToggle .seg-btn[data-view='en']")
        if await vbtn.count():
            await vbtn.first.click()
    await pg.wait_for_timeout(800)
    await pg.screenshot(path=path, full_page=False)
    n = await pg.locator(".entry").count()
    css = await assert_css(pg)
    await b.close()
    return n, css

async def main():
    async with async_playwright() as p:
        results = {}
        n, css = await shoot(p, "light", f"{OUT}/patrol_{TS}_light.png")
        results["light"] = {"entries": n, **css}
        n, css = await shoot(p, "dark", f"{OUT}/patrol_{TS}_dark.png")
        results["dark"] = {"entries": n, **css}
        n, css = await shoot(p, "auto", f"{OUT}/patrol_{TS}_auto.png")
        results["auto"] = {"entries": n, **css}
        n, css = await shoot(p, "light", f"{OUT}/patrol_{TS}_en.png", orig_view=True)
        results["en"] = {"entries": n, **css}
        print(json.dumps(results, ensure_ascii=False, indent=2))

asyncio.run(main())
