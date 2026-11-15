"""2026-11-15 02:59 例行巡检截图 + 样式实测：本地站点 127.0.0.1:8080
默认(浅色)/暗黑/系统自动 三主题，并校验 .entry::before=0、.metrics padding 四边 0、无手动同步按钮。
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/static"
os.makedirs(OUT, exist_ok=True)
TS = "0259_1115"


async def shoot(page, theme, name):
    await page.add_init_script(
        f"localStorage.setItem('themeMode', {json.dumps(theme)});"
    )
    await page.goto(URL, wait_until="networkidle")
    await page.wait_for_timeout(2500)
    path = f"{OUT}/patrol_{TS}_{name}.png"
    await page.screenshot(path=path, full_page=False)
    res = await page.evaluate(
        """() => {
            const out = {};
            let before = 0;
            for (const sheet of document.styleSheets) {
                try {
                    for (const r of sheet.cssRules) {
                        if (r.selectorText && r.selectorText.includes('.entry::before')) before++;
                    }
                } catch (e) {}
            }
            out.entry_before_rules = before;
            const m = document.querySelector('.metrics');
            if (m) {
                const cs = getComputedStyle(m);
                out.metrics_padding = cs.padding;
                out.metrics_padding_all_zero = ['paddingTop','paddingRight','paddingBottom','paddingLeft']
                    .map(k => parseFloat(cs[k])).every(v => v === 0);
            } else { out.metrics_padding = 'NO .metrics'; out.metrics_padding_all_zero = false; }
            out.sync_buttons = Array.from(document.querySelectorAll('button, a'))
                .filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || ''))
                .map(b => (b.textContent||'').trim());
            out.entries = document.querySelectorAll('.entry').length;
            out.theme = document.documentElement.getAttribute('data-theme');
            return out;
        }"""
    )
    print(f"[{name}] entries={res['entries']} entry_before={res['entry_before_rules']} metrics_padding={res['metrics_padding']} all_zero={res['metrics_padding_all_zero']} sync_btns={res['sync_buttons']} theme={res['theme']} -> {path}")
    return res


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        # auto: 用 color_scheme=dark 证明「系统自动」跟随系统深色
        r1 = await shoot(await (await browser.new_context()).new_page(), "light", "light")
        r2 = await shoot(await (await browser.new_context()).new_page(), "dark", "dark")
        ctx_auto = await browser.new_context(color_scheme="dark")
        r3 = await shoot(await ctx_auto.new_page(), "auto", "auto")
        await browser.close()
        print("SUMMARY", json.dumps({"light": r1, "dark": r2, "auto": r3}, ensure_ascii=False))


asyncio.run(main())
