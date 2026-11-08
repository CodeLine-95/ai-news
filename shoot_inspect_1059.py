import asyncio, json, datetime
from playwright.async_api import async_playwright
URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
HOUR = datetime.datetime.now().strftime("%H%M")
async def style_check(page):
    return await page.evaluate(
        """() => {
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const r of rules) { if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++; }
        }
        const entry = document.querySelector('.entry');
        const m = document.querySelector('.metrics');
        const cs = m ? getComputedStyle(m) : null;
        return {
            entry_before_rules: beforeCount,
            entry_before_content: entry ? getComputedStyle(entry,'::before').content : 'none',
            metrics_padding_all_zero: cs ? (['Top','Right','Bottom','Left'].map(k=>parseFloat(cs['padding'+k])===0).every(Boolean)) : null,
            sync_buttons: Array.from(document.querySelectorAll('button')).filter(b=>/同步|sync|refresh|刷新/i.test(b.textContent)).length,
            entries: document.querySelectorAll('.entry').length,
            theme: document.documentElement.getAttribute('data-theme')
        };
        }"""
    )
async def shoot(page, mode, path):
    await page.goto(URL, wait_until="networkidle")
    await page.evaluate("(v) => localStorage.setItem('themeMode', v)", mode)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(1800)
    await page.screenshot(path=path, full_page=False)
    return await style_check(page)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1280, "height": 1600})
        r1 = await shoot(pg, "light", f"{OUT}/巡检截图-{HOUR}-默认浅色.png")
        r2 = await shoot(pg, "dark", f"{OUT}/巡检截图-{HOUR}-暗黑.png")
        r3 = await shoot(pg, "auto", f"{OUT}/巡检截图-{HOUR}-系统自动.png")
        # 英文原文视图（浅色）
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("() => localStorage.setItem('themeMode','light')")
        await pg.reload(wait_until="networkidle")
        await pg.evaluate("document.querySelectorAll('#viewToggle .seg-btn').forEach(b=>{if(/英文|EN/i.test(b.textContent))b.click()})")
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f"{OUT}/巡检截图-{HOUR}-英文原文视图.png", full_page=False)
        await b.close()
        print(json.dumps({"light":r1,"dark":r2,"auto":r3}, ensure_ascii=False, indent=2))
asyncio.run(main())
