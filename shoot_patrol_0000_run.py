# -*- coding: utf-8 -*-
"""00点巡检：五态实测（浅色/暗黑/系统自动/英文原文/线上）+ 截图。"""
import json
from playwright.sync_api import sync_playwright

SHARE = "?sharecode=YM64NRHD37"
LOCAL = "http://127.0.0.1:8080/" + SHARE
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/" + SHARE
STAMP = "/workspace/ai-news/deliverable_1120_0000"

INSPECT_JS = """() => {
  const m = document.querySelector('.metrics');
  const cs = m ? getComputedStyle(m) : null;
  let entryBefore = false;
  for (const s of document.styleSheets) {
    try { if ([...s.cssRules].some(r => r.selectorText && r.selectorText.includes('entry::before'))) { entryBefore = true; break; } }
    catch (e) {}
  }
  const syncBtns = [...document.querySelectorAll('button,a')]
    .filter(b => /同步|sync|刷新数据|手动同步/i.test(b.textContent || '')).length;
  const theme = document.documentElement.getAttribute('data-theme') ||
    document.body.getAttribute('data-theme') ||
    (document.documentElement.classList.contains('dark') ? 'dark' : '') || 'default';
  return {
    entryBefore,
    metricsPadding: cs ? `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}` : 'none',
    syncBtns, theme,
    entries: document.querySelectorAll('.entry').length,
    bg: getComputedStyle(document.body).backgroundColor,
    title: document.title
  };
}"""


def set_mode(page, mode):
    page.evaluate("""(m) => {
      const b = [...document.querySelectorAll('#themeToggle .seg-btn')].find(x => x.getAttribute('data-theme') === m);
      if (b) b.click();
    }""", mode)
    page.wait_for_timeout(500)


def main():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])

        ctx = browser.new_context(viewport={"width": 1360, "height": 1100}, color_scheme="light")
        page = ctx.new_page()
        page.goto(LOCAL, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        set_mode(page, "light")
        results["light"] = page.evaluate(INSPECT_JS)
        page.screenshot(path=STAMP + "_light.png", full_page=False)

        set_mode(page, "dark")
        results["dark"] = page.evaluate(INSPECT_JS)
        page.screenshot(path=STAMP + "_dark.png", full_page=False)

        page.emulate_media(color_scheme="dark")
        set_mode(page, "auto")
        page.wait_for_timeout(600)
        results["auto_dark"] = page.evaluate(INSPECT_JS)
        page.screenshot(path=STAMP + "_auto.png", full_page=False)

        page.evaluate("""() => {
          const b = [...document.querySelectorAll('#viewToggle .seg-btn')]
            .find(x => /en|原文|english/i.test((x.getAttribute('data-mode') || '') + (x.textContent || '')));
          if (b) b.click();
        }""")
        page.wait_for_timeout(600)
        results["en"] = page.evaluate(INSPECT_JS)
        page.screenshot(path=STAMP + "_en.png", full_page=False)
        ctx.close()

        ctx = browser.new_context(viewport={"width": 1360, "height": 1100}, color_scheme="light")
        page = ctx.new_page()
        page.goto(ONLINE, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        results["online"] = page.evaluate(INSPECT_JS)
        page.screenshot(path=STAMP + "_online.png", full_page=False)
        ctx.close()

        browser.close()
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
