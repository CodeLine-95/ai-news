import asyncio, json, datetime
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
TS = "0359"

async def shoot(page, mode, view, path):
    await page.goto(URL, wait_until="networkidle")
    await page.evaluate("(v) => localStorage.setItem('themeMode', v)", mode)
    await page.evaluate("(v) => localStorage.setItem('viewMode', v)", view)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await page.screenshot(path=path, full_page=False)
    entry_before = await page.evaluate(
        "(() => { var e=document.querySelector('.entry'); return e ? getComputedStyle(e,'::before').content : 'no-entry'; })()"
    )
    metrics_pad = await page.evaluate(
        "document.querySelector('.metrics') ? getComputedStyle(document.querySelector('.metrics')).padding : 'n/a'"
    )
    sync_btns = await page.evaluate(
        "Array.from(document.querySelectorAll('button')).filter(b=>/同步|sync/i.test(b.textContent)).length"
    )
    entries = await page.evaluate("document.querySelectorAll('.entry').length")
    return {"mode": mode, "view": view, "entry_before": entry_before,
            "metrics_padding": metrics_pad, "sync_buttons": sync_btns, "entries": entries}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1280, "height": 900})
        results = []
        results.append(await shoot(pg, "light", "zh", f"{OUT}/patrol_{TS}_light.png"))
        results.append(await shoot(pg, "dark", "zh", f"{OUT}/patrol_{TS}_dark.png"))
        results.append(await shoot(pg, "auto", "zh", f"{OUT}/patrol_{TS}_auto.png"))
        results.append(await shoot(pg, "light", "en", f"{OUT}/patrol_{TS}_en.png"))
        await b.close()
        print(json.dumps(results, ensure_ascii=False, indent=2))
        json.dump(results, open(f"{OUT}/patrol_{TS}_checks.json", "w"), ensure_ascii=False, indent=2)

asyncio.run(main())
