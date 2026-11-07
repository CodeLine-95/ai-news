"""本轮巡检(2026-11-07 16:00)截图 + 样式实测：本地站点 127.0.0.1:8080
浅色 / 暗黑 / 系统自动 三套主题，校验 .entry::before=0、.metrics padding 四边 0、无手动同步按钮。
"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)


async def style_check(page, theme_requested):
    res = await page.evaluate(
        """(themeRequested) => {
        const res = { theme_requested: themeRequested };
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const r of rules) {
                if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++;
            }
        }
        res.entry_before_rules = beforeCount;
        const entry = document.querySelector('.entry');
        res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no .entry)';
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding = { top: cs.paddingTop, right: cs.paddingRight,
                bottom: cs.paddingBottom, left: cs.paddingLeft };
            res.metrics_padding_all_zero = ['top','right','bottom','left']
                .map(k=>parseFloat(res.metrics_padding[k])===0).every(Boolean);
        }
        res.entries = document.querySelectorAll('.entry').length;
        res.sync_buttons = Array.from(document.querySelectorAll('button'))
            .filter(b => /同步|sync|refresh|刷新/i.test(b.textContent)).length;
        res.title = document.title;
        res.effective_theme = document.documentElement.getAttribute('data-theme');
        return res;
    }""",
        theme_requested,
    )
    return res


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1280, "height": 1700})
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2500)

        out = {}
        for mode in ["light", "dark", "auto"]:
            await page.evaluate("(m) => { localStorage.setItem('themeMode', m); document.documentElement.setAttribute('data-theme', m); }", mode)
            await page.wait_for_timeout(900)
            await page.screenshot(path=os.path.join(OUT, f"shot_{mode}_1600.png"), full_page=False)
            out[mode] = await style_check(page, mode)

        await browser.close()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        with open("/workspace/ai-news/data/inspect_check.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)


asyncio.run(main())
