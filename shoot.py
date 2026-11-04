"""抓取网站截图并做前端样式实测。

除了出图，还用 Playwright 在**线上真实渲染环境**里实测三项样式要求：
  1. .entry::before 不存在（要求：移除）
  2. .metrics 的 padding 全为 0（桌面 + 移动端）
  3. 全站无「手动同步」按钮

这三项光看源码不够——线上 CSS 可能被缓存、被覆盖，
必须以浏览器计算后的样式为准。
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
    """在真实渲染环境里实测前端样式约束。"""
    return await page.evaluate(
        """() => {
        const res = {};

        // 1) .entry::before 是否被移除
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
                if (rule.selectorText &&
                    rule.selectorText.includes('.entry::before')) {
                    beforeCount++;
                }
            }
        }
        res.entry_before_rules = beforeCount;
        const entry = document.querySelector('.entry');
        res.entry_before_content = entry
            ? getComputedStyle(entry, '::before').content : '(no .entry)';

        // 2) .metrics 的 padding（桌面）
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding = {
                top: cs.paddingTop, right: cs.paddingRight,
                bottom: cs.paddingBottom, left: cs.paddingLeft,
            };
            res.metrics_padding_all_zero = [
                cs.paddingTop, cs.paddingRight,
                cs.paddingBottom, cs.paddingLeft,
            ].every(v => parseFloat(v) === 0);
        }

        // 3) 手动同步按钮
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns
            .filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || ''))
            .map(b => (b.textContent || '').trim());

        // 4) 条目数与页面基本信息
        res.entries = document.querySelectorAll('.entry').length;
        res.title = document.title;
        return res;
        }"""
    )


async def shoot(pw, name, mode=None, viewport=None):
    browser = await pw.chromium.launch(args=["--no-sandbox"])
    ctx = await browser.new_context(
        viewport=viewport or {"width": 1440, "height": 1000},
        device_scale_factor=2,
        locale="zh-CN",
    )
    page = await ctx.new_page()
    await page.goto(URL, wait_until="networkidle", timeout=90000)
    await page.wait_for_function(
        "() => document.querySelectorAll('.timeline-root > *').length > 3",
        timeout=60000,
    )
    await page.wait_for_timeout(2500)
    if mode == "en":
        await page.click('button[data-mode="en"]')
        await page.wait_for_timeout(1500)
    elif mode == "single":
        # 单条对照：点第一条资讯的「看英文原文」，其余保持中文译文
        await page.click(".toggle-lang")
        await page.wait_for_timeout(1500)
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
        report["desktop"] = await shoot(pw, "网站预览.png")
        report["desktop_en"] = await shoot(
            pw, "网站预览-原文模式.png", mode="en")
        report["desktop_single"] = await shoot(
            pw, "网站预览-单条对照.png", mode="single")
        report["mobile"] = await shoot(
            pw, "网站截图-移动端.png",
            viewport={"width": 390, "height": 844})

    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    with open(os.path.join(OUT, "data", "frontend_check.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n=== 前端实测汇总 ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))


asyncio.run(main())
