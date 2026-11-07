import asyncio, json
from playwright.async_api import async_playwright
URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
async def shoot(page, mode, path):
    await page.goto(URL, wait_until="networkidle")
    await page.evaluate("(v) => localStorage.setItem('themeMode', v)", mode)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(1800)
    await page.screenshot(path=path, full_page=False)
    entry_before = await page.evaluate("(() => { var e=document.querySelector('.entry'); return e ? getComputedStyle(e,'::before').content : 'none'; })()")
    metrics_pad = await page.evaluate("document.querySelector('.metrics') ? getComputedStyle(document.querySelector('.metrics')).padding : 'n/a'")
    sync_btns = await page.evaluate("Array.from(document.querySelectorAll('button')).filter(b=>/同步|sync/i.test(b.textContent)).length")
    entries = await page.evaluate("document.querySelectorAll('.entry').length")
    return {"mode": mode, "entry_before_content": entry_before, "metrics_padding": metrics_pad, "sync_buttons": sync_btns, "entries": entries}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1280, "height": 900})
        r1 = await shoot(pg, "light", f"{OUT}/巡检截图-0900-浅色.png")
        r2 = await shoot(pg, "dark", f"{OUT}/巡检截图-0900-暗黑.png")
        r3 = await shoot(pg, "auto", f"{OUT}/巡检截图-0900-系统自动.png")
        await b.close()
        print(json.dumps([r1,r2,r3], ensure_ascii=False, indent=2))
asyncio.run(main())
