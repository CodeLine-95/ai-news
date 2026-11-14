import asyncio
from playwright.async_api import async_playwright

DOMAIN = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"

themes = [
    ("light", "live_light"),
    ("dark", "live_dark"),
    ("auto", "live_auto"),
]

async def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for theme, name in themes:
            ctx = await browser.new_context(viewport={"width": 1280, "height": 1600})
            page = await ctx.new_page()
            await page.add_init_script(
                f"localStorage.setItem('themeMode','{theme}');"
            )
            await page.goto(DOMAIN, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3500)
            # assert there is no manual sync button
            has_sync = await page.evaluate(
                "() => { const btns=[...document.querySelectorAll('button')]; return btns.some(b=>/同步|sync/i.test(b.textContent||'')); }"
            )
            path = f"{OUT}/{name}.png"
            await page.screenshot(path=path, full_page=False)
            # also capture CSS assertions
            metrics_padding = await page.evaluate(
                "() => { const el=document.querySelector('.metrics'); if(!el) return 'none'; return getComputedStyle(el).padding; }"
            )
            entry_before = await page.evaluate(
                "() => { let found=false; for(const ss of document.styleSheets){ try{ for(const r of ss.cssRules){ if(r.selectorText && r.selectorText.includes('.entry::before')) found=true; } }catch(e){} } return found; }"
            )
            print(f"{name}: sync_button={has_sync} metrics_padding={metrics_padding} entry_before={entry_before} -> {path}")
            await ctx.close()
        await browser.close()

asyncio.run(main())
