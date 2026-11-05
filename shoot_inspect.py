"""本轮巡检截图：线上域名三主题（浅色/暗黑/系统自动）+ 前端样式实测。

复用 shoot.py 的样式实测逻辑，额外验证暗黑/默认(浅色)/系统自动三套主题
可切换且样式正常。
"""
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
            res.metrics_padding_all_zero = [cs.paddingTop, cs.paddingRight,
                cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0);
        }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || ''))
            .map(b => (b.textContent || '').trim());
        res.entries = document.querySelectorAll('.entry').length;
        res.title = document.title;
        return res;
        }"""
    )


async def shoot(pw, name, theme):
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 1000},
        device_scale_factor=2,
        locale="zh-CN",
    )
    page = await ctx.new_page()
    await page.goto(URL, wait_until="networkidle", timeout=90000)
    await page.wait_for_function(
        "() => document.querySelectorAll('.entry').length > 3", timeout=60000)
    await page.wait_for_timeout(2500)
    if theme:
        await page.click(f'#themeToggle .seg-btn[data-theme="{theme}"]')
        await page.wait_for_timeout(1800)
    path = os.path.join(OUT, name)
    await page.screenshot(path=path, full_page=False)
    styles = await check_styles(page)
    eff = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    styles["effective_theme"] = eff
    styles["theme_requested"] = theme or "default(auto)"
    print("saved:", path, "→", json.dumps(styles, ensure_ascii=False))
    await browser.close()
    return styles


async def main():
    report = {}
    async with async_playwright() as pw:
        report["light"] = await shoot(pw, "巡检截图-浅色.png", "light")
        report["dark"] = await shoot(pw, "巡检截图-暗黑.png", "dark")
        report["auto"] = await shoot(pw, "巡检截图-系统自动.png", "auto")
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    with open(os.path.join(OUT, "data", "inspect_check.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n=== 巡检样式实测汇总 ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))


asyncio.run(main())
