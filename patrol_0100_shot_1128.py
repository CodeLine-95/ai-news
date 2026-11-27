# -*- coding: utf-8 -*-
"""01 点巡检：浏览器断言 + 暗黑/默认/系统自动/英文原文/线上截图。"""
import asyncio
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"


async def check(page, label):
    before = await page.evaluate("""() => {
      let n = 0;
      document.querySelectorAll('.entry').forEach(el => {
        const c = getComputedStyle(el, '::before');
        if (c && c.content && c.content !== 'none' && c.content !== 'normal') n++;
      });
      return n;
    }""")
    pads = await page.evaluate("""() => {
      const el = document.querySelector('.metrics');
      if (!el) return null;
      const c = getComputedStyle(el);
      return [c.paddingTop, c.paddingRight, c.paddingBottom, c.paddingLeft];
    }""")
    sync = await page.evaluate("""() => Array.from(document.querySelectorAll('button'))
      .filter(b => /同步/.test(b.textContent || '')).length""")
    theme = await page.evaluate("document.documentElement.getAttribute('data-theme')")
    active = await page.evaluate(
        "document.querySelector('#themeToggle .seg-btn.active')?.dataset.theme || 'none'"
    )
    ok = before == 0 and pads == ["0px"] * 4 and sync == 0
    print("%-10s theme=%-5s active=%-5s entry::before=%d metrics_padding=%s sync_buttons=%d %s"
          % (label, theme, active, before, pads, sync, "PASS" if ok else "FAIL"))
    assert ok, label
    return theme, active


async def shoot(browser, theme, filename, color_scheme="light"):
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 960},
        device_scale_factor=1,
        color_scheme=color_scheme,
    )
    page = await ctx.new_page()
    await page.add_init_script("localStorage.setItem('themeMode', %r);" % theme)
    await page.goto(LOCAL, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2500)
    await check(page, theme)
    await page.screenshot(path="%s/%s" % (OUT, filename), full_page=False)
    await ctx.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        await shoot(browser, "dark", "巡检截图-0100_暗黑.png", color_scheme="dark")
        await shoot(browser, "light", "巡检截图-0100_默认浅色.png", color_scheme="light")

        # 系统自动：随系统明暗动态切换
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 960}, color_scheme="light"
        )
        page = await ctx.new_page()
        await page.add_init_script("localStorage.setItem('themeMode', 'auto');")
        await page.goto(LOCAL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        t1 = await check(page, "auto-light")
        await page.emulate_media(color_scheme="dark")
        await page.wait_for_timeout(800)
        t2 = await check(page, "auto-dark")
        assert t1[0] == "light" and t2[0] == "dark", "系统自动未跟随系统切换"
        await page.screenshot(path="%s/巡检截图-0100_系统自动.png" % OUT, full_page=False)
        await ctx.close()

        # 英文原文视图
        ctx = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await ctx.new_page()
        await page.add_init_script(
            "localStorage.setItem('themeMode','light');localStorage.setItem('viewMode','en');"
        )
        await page.goto(LOCAL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)
        await check(page, "en")
        await page.screenshot(path="%s/巡检截图-0100_英文原文视图.png" % OUT, full_page=False)
        await ctx.close()

        # 线上站点
        ctx = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await ctx.new_page()
        await page.goto(ONLINE, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        await check(page, "online")
        await page.screenshot(path="%s/巡检截图-0100_线上.png" % OUT, full_page=False)
        await ctx.close()

        await browser.close()
        print("全部浏览器断言通过，截图已生成")


if __name__ == "__main__":
    asyncio.run(main())
