"""本轮巡检(2026-11-11 01:xx)截图 + 样式实测：本地站点 127.0.0.1:8080
默认浅色 / 暗黑 / 系统自动 三主题，并校验 .entry::before=0、.metrics padding 四边 0。
"""
import asyncio
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
        const metrics = document.querySelector('.metrics');
        if (metrics) {
            const cs = getComputedStyle(metrics);
            res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
        } else { res.metrics_padding = 'NO .metrics'; }
        // 统计手动同步按钮（含 data-sync / 立即同步 / sync now 文本）
        const buttons = [...document.querySelectorAll('button, a.btn, .btn')];
        res.sync_buttons = buttons
            .map(b => (b.textContent || '').trim())
            .filter(t => /同步|sync|刷新|refresh/i.test(t));
        res.item_count = document.querySelectorAll('.entry').length;
        return res;
    }"""
    )


async def shoot(page, name):
    path = os.path.join(OUT, name)
    await page.screenshot(path=path, full_page=False)
    return path


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # 默认浅色
        await page.evaluate("localStorage.setItem('theme','light')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1200)
        s1 = await style_check(page)
        await shoot(page, "巡检截图-0159-默认浅色.png")

        # 暗黑
        await page.evaluate("localStorage.setItem('theme','dark')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1200)
        s2 = await style_check(page)
        await shoot(page, "巡检截图-0159-暗黑.png")

        # 系统自动
        await page.evaluate("localStorage.setItem('theme','auto')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1200)
        s3 = await style_check(page)
        await shoot(page, "巡检截图-0159-系统自动.png")

        # 英文原文视图（验证可切换看原文）
        await page.evaluate("localStorage.setItem('viewMode','en'); localStorage.setItem('theme','light')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1200)
        await shoot(page, "巡检截图-0159-英文原文视图.png")

        await browser.close()
        print("STYLE light:", s1)
        print("STYLE dark :", s2)
        print("STYLE auto :", s3)


asyncio.run(main())
