"""巡检(2026-11-28 17:00)截图 + 浏览器样式实测。
校验：.entry::before=0、.metrics padding 四边 0、无手动同步按钮、
暗黑/默认浅色/系统自动(跟随系统)、英文原文视图、线上与本地一致。
"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news/screenshots"
STAMP = "deliverable_1128_1700_patrol"
os.makedirs(OUT, exist_ok=True)

CHECK_JS = """() => {
  const res = {};
  let beforeCount = 0;
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const r of rules) if (r.selectorText && r.selectorText.includes('.entry::before')) beforeCount++;
  }
  res.entry_before_rules = beforeCount;
  const entry = document.querySelector('.entry');
  res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no .entry)';
  const m = document.querySelector('.metrics');
  if (m) {
    const cs = getComputedStyle(m);
    res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
    res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
  }
  const btns = Array.from(document.querySelectorAll('button, a'));
  res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent || '').trim());
  res.entries = document.querySelectorAll('.entry').length;
  res.data_theme = document.documentElement.getAttribute('data-theme');
  res.body_bg = getComputedStyle(document.body).backgroundColor;
  return res;
}"""


async def shoot(browser, name, url, theme=None, mode=None, color_scheme="light"):
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 1100}, device_scale_factor=2,
        locale="zh-CN", color_scheme=color_scheme,
    )
    page = await ctx.new_page()
    await page.goto(url, wait_until="networkidle", timeout=90000)
    await page.wait_for_function("() => document.querySelectorAll('.entry').length > 3", timeout=60000)
    await page.wait_for_timeout(1500)
    if theme:
        try:
            await page.click(f'#themeToggle button[data-theme="{theme}"]', timeout=5000)
        except Exception:
            pass
        await page.wait_for_timeout(900)
    if mode:
        try:
            await page.click(f'#viewToggle button[data-mode="{mode}"]', timeout=5000)
        except Exception:
            pass
        await page.wait_for_timeout(1100)
    path = f"{OUT}/{STAMP}_{name}.png"
    await page.screenshot(path=path, full_page=False)
    chk = await page.evaluate(CHECK_JS)
    print(name, "=>", path, "|", json.dumps(chk, ensure_ascii=False))
    await ctx.close()
    return chk


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        r = {}
        r["light"] = await shoot(browser, "light", LOCAL, theme="light", color_scheme="light")
        r["dark"] = await shoot(browser, "dark", LOCAL, theme="dark", color_scheme="dark")
        r["auto_dark"] = await shoot(browser, "auto_dark", LOCAL, theme="auto", color_scheme="dark")
        r["auto_light"] = await shoot(browser, "auto_light", LOCAL, theme="auto", color_scheme="light")
        r["en"] = await shoot(browser, "en", LOCAL, theme="light", mode="en", color_scheme="light")
        r["online"] = await shoot(browser, "online", ONLINE, color_scheme="light")
        await browser.close()
        print("\nSUMMARY", json.dumps(r, ensure_ascii=False))
        with open(f"{OUT}/{STAMP}_checks.json", "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)


asyncio.run(main())
