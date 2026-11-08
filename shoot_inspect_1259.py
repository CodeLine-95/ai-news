"""本轮巡检(2026-11-08 12:59)截图 + 样式实测：本地站点 127.0.0.1:8080
浅色 / 暗黑 / 系统自动 三主题，并校验 .entry::before=0、.metrics padding 四边 0、
无手动同步按钮。
"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/"
OUT = "/workspace/ai-news/screenshots"
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
        page = await browser.new_page(viewport={"width": 1280, "height": 1600})
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2500)

        # 默认（浅色）
        await page.evaluate("document.documentElement.setAttribute('data-theme','light')")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(OUT, "巡检截图-1259-默认浅色.png"), full_page=False)
        light = await style_check(page)

        # 暗黑
        await page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(OUT, "巡检截图-1259-暗黑.png"), full_page=False)
        dark = await style_check(page)

        # 系统自动
        await page.evaluate("document.documentElement.setAttribute('data-theme','auto')")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(OUT, "巡检截图-1259-系统自动.png"), full_page=False)

        # 英文原文视图（切换 viewToggle 到英文）
        await page.evaluate("document.documentElement.setAttribute('data-theme','light')")
        try:
            await page.click("#viewToggle .seg-btn:last-child", timeout=3000)
        except Exception as e:
            print("viewToggle click skip:", e)
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUT, "巡检截图-1259-英文原文视图.png"), full_page=False)

        await browser.close()
        print(json.dumps({"light": light, "dark": dark}, ensure_ascii=False, indent=2))


asyncio.run(main())
