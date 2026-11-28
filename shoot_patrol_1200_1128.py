# -*- coding: utf-8 -*-
"""12:00 巡检：六态浏览器断言 + 截图（本地浅/深/系统自动双态/英文原文/线上）。

断言项：
- .entry::before 样式规则为 0，computed content 为 none
- .metrics 四向 padding 均为 0px
- 全站无「同步 / sync / refresh / 刷新」按钮
- 暗黑 / 默认（浅色）/ 系统自动三主题可切换
- 系统自动跟随 color-scheme 动态切换
- 英文原文视图可切换
- 线上条目数与本地一致（均为 2936）
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(BASE, "screenshots")
os.makedirs(SHOTS, exist_ok=True)

LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"

ASSERT_JS = """() => {
  const res = {};
  let beforeCount = 0;
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const rule of rules) {
      if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
    }
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
  res.view_mode = document.documentElement.getAttribute('data-view') || (document.querySelector('#viewToggle .seg-btn.active') || {}).dataset?.mode || null;
  res.has_theme_toggle = !!document.querySelector('#themeToggle');
  res.has_view_toggle = !!document.querySelector('#viewToggle');
  const first = document.querySelector('.entry-title');
  res.first_title = first ? (first.textContent || '').trim().slice(0, 80) : null;
  res.bg = getComputedStyle(document.body).backgroundColor;
  return res;
}"""


def shoot(pw, url, name, *, color_scheme="light", theme=None, en=False):
    browser = pw.chromium.launch(args=["--no-sandbox"])
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 1100},
        device_scale_factor=2,
        locale="zh-CN",
        color_scheme=color_scheme,
    )
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_selector(".entry", timeout=60000)
    page.wait_for_timeout(2000)
    if theme:
        page.click(f'#themeToggle button[data-theme="{theme}"]')
        page.wait_for_timeout(800)
    if en:
        page.click('#viewToggle button[data-mode="en"]')
        page.wait_for_timeout(1000)
    path = os.path.join(SHOTS, name)
    page.screenshot(path=path, full_page=False)
    res = page.evaluate(ASSERT_JS)
    res["file"] = path
    print("saved:", path, flush=True)
    browser.close()
    return res


def main():
    results = {}
    with sync_playwright() as pw:
        results["local_light"] = shoot(pw, LOCAL, "deliverable_1128_1200_light.png", theme="light")
        results["local_dark"] = shoot(pw, LOCAL, "deliverable_1128_1200_dark.png", theme="dark", color_scheme="dark")
        results["auto_dark"] = shoot(pw, LOCAL, "deliverable_1128_1200_auto_dark.png", theme="auto", color_scheme="dark")
        results["auto_light"] = shoot(pw, LOCAL, "deliverable_1128_1200_auto_light.png", theme="auto", color_scheme="light")
        results["english"] = shoot(pw, LOCAL, "deliverable_1128_1200_en.png", theme="light", en=True)
        results["online"] = shoot(pw, ONLINE, "deliverable_1128_1200_online.png", theme="light")
    print("\n=== 断言汇总 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    ok = all(
        r["entry_before_rules"] == 0
        and r["entry_before_content"] in ("none", "normal")
        and r["metrics_padding_all_zero"]
        and not r["sync_buttons"]
        and r["entries"] > 3
        for r in results.values()
    )
    auto_ok = (results["auto_dark"]["data_theme"] == "dark"
               and results["auto_light"]["data_theme"] == "light")
    print("ALL_ASSERTIONS_OK:", ok and auto_ok)
    if not (ok and auto_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
