"""13:00 巡检截图：默认(浅色)/暗黑/系统自动三主题 + CSS 约束实测（entry::before=0, .metrics padding 0, 无手动同步按钮）。"""
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
        } else { res.metrics_padding_all_zero = 'NO .metrics'; }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent||'').trim());
        res.entries = document.querySelectorAll('.entry').length;
        return res;
    }""")


async def snap(page, theme, file):
    await page.evaluate(f"localStorage.setItem('themeMode','{theme}');")
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(1800)
    s = await check_styles(page)
    s["theme"] = await page.evaluate("document.documentElement.getAttribute('data-theme')")
    await page.screenshot(path=f"{OUT}/{file}", full_page=False)
    return s


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1600})
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1800)
        light = await snap(page, "light", "patrol_1300_light.png")
        dark = await snap(page, "dark", "patrol_1300_dark.png")
        auto = await snap(page, "auto", "patrol_1300_auto.png")
        await ctx.close()
        await browser.close()
        print(json.dumps({"light": light, "dark": dark, "auto": auto}, ensure_ascii=False, indent=2))


asyncio.run(main())
