import asyncio, json
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"

async def shoot(page, mode, path):
    await page.goto(URL, wait_until="networkidle")
    await page.evaluate("(v) => localStorage.setItem('themeMode', v)", mode)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(1500)
    await page.screenshot(path=path, full_page=False)
    # checks
    entry_before = await page.evaluate(
        "(() => { var e=document.querySelector('.entry'); return e ? getComputedStyle(e,'::before').content : 'none'; })()"
    )
    metrics_pad = await page.evaluate(
        "document.querySelector('.metrics') ? getComputedStyle(document.querySelector('.metrics')).padding : 'n/a'"
    )
    sync_btns = await page.evaluate(
        "Array.from(document.querySelectorAll('button')).filter(b=>/同步|sync/i.test(b.textContent)).length"
    )
    entries = await page.evaluate("document.querySelectorAll('.entry').length")
    return {"mode":mode,"metrics_padding":metrics_pad,"sync_buttons":sync_btns,"entries":entries}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":1280,"height":900})
        r1 = await shoot(pg, "light", f"{OUT}/inspect_0359_light.png")
        r2 = await shoot(pg, "dark", f"{OUT}/inspect_0359_dark.png")
        r3 = await shoot(pg, "auto", f"{OUT}/inspect_0359_auto.png")
        await b.close()
        print(json.dumps([r1,r2,r3], ensure_ascii=False, indent=2))

asyncio.run(main())
