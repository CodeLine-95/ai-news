"""12:00 巡检截图：默认(浅色)/暗黑模式 + CSS 约束实测。"""
import asyncio
import json
from playwright.async_api import async_playwright

DOMAIN = "https://a7888a7e046ffc95b.app.workbuddy.host"
SHARE = "YM64NRHD37"
URL = f"{DOMAIN}/?sharecode={SHARE}"
OUT = "/workspace/ai-news/screenshots"


async def check_styles(page):
    return await page.evaluate("""() => {
        const res = {};
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
                if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
            }
        }
        res.entry_before_rules = beforeCount;
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding = {top: cs.paddingTop, right: cs.paddingRight, bottom: cs.paddingBottom, left: cs.paddingLeft};
            res.metrics_padding_all_zero = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0);
        }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent||'').trim());
        res.entries = document.querySelectorAll('.entry').length;
        return res;
    }""")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        # 浅色（默认）
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1600})
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.evaluate("localStorage.setItem('themeMode','light');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{OUT}/inspect_1200_light.png", full_page=False)
        light = await check_styles(page)
        light["theme"] = await page.evaluate("document.documentElement.getAttribute('data-theme')")
        # 暗黑
        await page.evaluate("localStorage.setItem('themeMode','dark');")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{OUT}/inspect_1200_dark.png", full_page=False)
        dark = await check_styles(page)
        dark["theme"] = await page.evaluate("document.documentElement.getAttribute('data-theme')")
        await ctx.close()
        print(json.dumps({"light": light, "dark": dark}, ensure_ascii=False, indent=2))
        await browser.close()


asyncio.run(main())
