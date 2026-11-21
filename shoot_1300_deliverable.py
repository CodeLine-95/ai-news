# -*- coding: utf-8 -*-
"""11:00 例行巡检交付截图 + 五态实测。"""
import asyncio
import os
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"
PREFIX = "deliverable_1119_1300"
os.makedirs(OUT, exist_ok=True)


async def apply_theme(page, theme):
    await page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
    await page.wait_for_timeout(700)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1440, "height": 1100})
        await page.goto(LOCAL, wait_until="networkidle", timeout=40000)
        await page.wait_for_timeout(2000)

        probes = await page.evaluate("""() => {
            const entry = document.querySelector('.entry');
            const before = entry ? getComputedStyle(entry, '::before').content : 'no-entry';
            const beforeDisplay = entry ? getComputedStyle(entry, '::before').display : 'n/a';
            const m = document.querySelector('.metrics');
            const cs = m ? getComputedStyle(m) : null;
            const pads = cs ? [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft] : [];
            const syncBtns = [...document.querySelectorAll('button,a,[role=button]')]
              .filter(b => /同步|sync|refresh|刷新/i.test((b.textContent||'')+(b.getAttribute('aria-label')||''))).length;
            const themeBtns = [...document.querySelectorAll('#themeToggle .seg-btn, [data-theme].seg-btn')]
              .map(b => b.getAttribute('data-theme'));
            return {
              entryBeforeContent: before, entryBeforeDisplay: beforeDisplay,
              metricsPadding: pads, syncBtns: syncBtns,
              themeModes: [...new Set(themeBtns)],
              entryCount: document.querySelectorAll('.entry').length
            };
        }""")
        print("[实测]", probes)

        theme_check = {}
        for t in ("light", "dark", "auto"):
            await apply_theme(page, t)
            theme_check[t] = await page.evaluate(
                "() => document.documentElement.getAttribute('data-theme')")
        print("[实测] 主题切换:", theme_check)

        await apply_theme(page, "light")
        await page.screenshot(path=f"{OUT}/{PREFIX}_light.png")
        await apply_theme(page, "dark")
        await page.screenshot(path=f"{OUT}/{PREFIX}_dark.png")
        await apply_theme(page, "auto")
        await page.screenshot(path=f"{OUT}/{PREFIX}_auto.png")
        await apply_theme(page, "light")
        await page.evaluate("""() => {
            const b = document.querySelector('#viewToggle .seg-btn[data-mode="en"]');
            if (b) b.click();
        }""")
        await page.wait_for_timeout(900)
        await page.screenshot(path=f"{OUT}/{PREFIX}_en.png")
        await page.close()

        ctx = await browser.new_context(viewport={"width": 1440, "height": 1100}, color_scheme="light")
        p2 = await ctx.new_page()
        await p2.goto(ONLINE, wait_until="networkidle", timeout=45000)
        await p2.wait_for_timeout(2000)
        await p2.evaluate("document.documentElement.setAttribute('data-theme','light')")
        await p2.wait_for_timeout(900)
        await p2.screenshot(path=f"{OUT}/{PREFIX}_online.png")
        online_entries = await p2.evaluate("document.querySelectorAll('.entry').length")
        online_stat = await p2.evaluate("""() => {
            const el = document.querySelector('.metric-num');
            return el ? el.textContent.trim() : 'n/a';
        }""")
        await ctx.close()
        await browser.close()
        print("交付截图完成，线上 entries =", online_entries, "线上指标 =", online_stat)
        print("[结论] entry::before content=%s / display=%s" % (
            probes["entryBeforeContent"], probes["entryBeforeDisplay"]))
        print("[结论] metrics padding=%s" % probes["metricsPadding"])
        print("[结论] 手动同步按钮数=%s" % probes["syncBtns"])
        print("[结论] 主题模式=%s 切换结果=%s" % (probes["themeModes"], theme_check))
        print("[结论] 本地entries=%s 线上entries=%s" % (
            probes["entryCount"], online_entries))


asyncio.run(main())
