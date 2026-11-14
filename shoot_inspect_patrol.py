"""每小时巡检截图：默认(浅色)/暗黑模式/英文原文视图/移动端 + CSS 约束实测。"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

DOMAIN = "https://a7888a7e046ffc95b.app.workbuddy.host"
SHARE = "YM64NRHD37"
URL = f"{DOMAIN}/?sharecode={SHARE}"
OUT = "/workspace/ai-news"


async def check_styles(page):
    return await page.evaluate(
        """() => {
        const res = {};
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
                if (rule.selectorText &&
                    rule.selectorText.includes('.entry::before')) beforeCount++;
            }
        }
        res.entry_before_rules = beforeCount;
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding = {top: cs.paddingTop, right: cs.paddingRight,
                bottom: cs.paddingBottom, left: cs.paddingLeft};
            res.metrics_padding_all_zero = [cs.paddingTop, cs.paddingRight,
                cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0);
        }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || ''))
            .map(b => (b.textContent || '').trim());
        res.entries = document.querySelectorAll('.entry').length;
        res.theme = document.documentElement.getAttribute('data-theme');
        res.title = document.title;
        return res;
        }"""
    )


async def shoot(pw, name, theme=None, mode=None, viewport=None):
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    ctx = await browser.new_context(
        viewport=viewport or {"width": 1440, "height": 1100},
        device_scale_factor=2,
        locale="zh-CN",
    )
    page = await ctx.new_page()
    await page.goto(URL, wait_until="networkidle", timeout=90000)
    await page.wait_for_function(
        "() => document.querySelectorAll('.timeline-root > *').length > 3",
        timeout=60000,
    )
    await page.wait_for_timeout(2000)
    if theme:
        await page.click(f'#themeToggle .seg-btn[data-theme="{theme}"]')
        await page.wait_for_timeout(1200)
    if mode == "en":
        await page.click('button[data-mode="en"]')
        await page.wait_for_timeout(1200)
    path = os.path.join(OUT, name)
    await page.screenshot(path=path, full_page=False)
    print("saved:", path)
    styles = await check_styles(page)
    print("  样式实测:", json.dumps(styles, ensure_ascii=False))
    await browser.close()
    return styles


async def main():
    report = {}
    async with async_playwright() as pw:
        report["default_light"] = await shoot(pw, "网站预览-默认浅色.png")
        report["dark"] = await shoot(pw, "网站预览-暗黑模式.png", theme="dark")
        report["en_view"] = await shoot(pw, "网站预览-英文原文视图.png", mode="en")
        report["mobile"] = await shoot(
            pw, "网站截图-移动端.png", viewport={"width": 390, "height": 844})

    with open(os.path.join(OUT, "data", "frontend_check_patrol.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n=== 前端实测汇总 ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))


asyncio.run(main())
