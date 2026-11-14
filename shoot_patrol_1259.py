import asyncio, os
from playwright.async_api import async_playwright

OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8080/"

async def shoot(p, theme, path):
    b = await p.chromium.launch(args=["--no-sandbox"])
    pg = await b.new_page(viewport={"width": 1280, "height": 1000},
                          device_scale_factor=2)
    await pg.goto(URL, wait_until="networkidle", timeout=30000)
    await pg.wait_for_selector(".entry", timeout=20000)
    btn = pg.locator(f"#themeToggle .seg-btn[data-theme='{theme}']")
    if await btn.count():
        await btn.first.click()
    await pg.wait_for_timeout(700)
    await pg.screenshot(path=path, full_page=False)
    n_entries = await pg.locator(".entry").count()
    before = await pg.evaluate("() => { const el=document.querySelector('.entry'); if(!el) return 'no-entry'; const cs=getComputedStyle(el,'::before'); return cs.content; }")
    metrics_pad = await pg.evaluate("() => { const el=document.querySelector('.metrics'); if(!el) return 'no-metrics'; return getComputedStyle(el).padding; }")
    has_sync_btn = await pg.locator("button:has-text('同步')").count()
    await b.close()
    return n_entries, before, metrics_pad, has_sync_btn

async def main():
    async with async_playwright() as p:
        ne, before, mp, sb = await shoot(p, "light", f"{OUT}/巡检截图-1259-默认浅色.png")
        nd, before_d, mp_d, sb_d = await shoot(p, "dark", f"{OUT}/巡检截图-1259-暗黑.png")
        print(f"OK entries_light={ne} entries_dark={nd}")
        print(f"entry_before_light={before!r} entry_before_dark={before_d!r}")
        print(f"metrics_pad_light={mp!r} metrics_pad_dark={mp_d!r}")
        print(f"sync_button_light={sb} sync_button_dark={sb_d}")

asyncio.run(main())
