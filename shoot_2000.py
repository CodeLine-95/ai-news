"""本轮巡检(2026-11-08 20:00)截图 + 样式实测：本地站点 127.0.0.1:8080
默认浅色主题，并校验 .entry::before=0、.metrics padding 四边 0、无手动同步按钮。
"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news"
os.makedirs(OUT, exist_ok=True)


async def style_check(page):
    return await page.evaluate(
        """() => {
        const res = {};
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
        res.theme = document.documentElement.getAttribute('data-theme');
        return res;
    }"""
    )


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        # 默认浅色（清掉 localStorage，让主题回到 auto/light）
        await page.goto(URL, wait_until="networkidle")
        await page.evaluate("localStorage.removeItem('themeMode'); localStorage.removeItem('viewMode');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2500)
        light = await style_check(page)
        await page.screenshot(path=f"{OUT}/巡检截图-2000-默认浅色.png", full_page=False)

        # 暗黑模式
        await page.evaluate("localStorage.setItem('themeMode','dark');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2000)
        dark = await style_check(page)
        await page.screenshot(path=f"{OUT}/巡检截图-2000-暗黑.png", full_page=False)

        # 英文原文视图
        await page.evaluate("localStorage.setItem('viewMode','en');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{OUT}/巡检截图-2000-英文原文视图.png", full_page=False)

        await browser.close()
        print(json.dumps({"light": light, "dark": dark}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
