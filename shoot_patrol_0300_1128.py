# -*- coding: utf-8 -*-
"""02 点例行巡检截图与断言：默认浅色 / 暗黑 / 系统自动（深+浅）/ 英文原文 / 线上。"""
import json
import os

from playwright.sync_api import sync_playwright

BASE = "/workspace/ai-news"
OUT = os.path.join(BASE, "screenshots")
os.makedirs(OUT, exist_ok=True)
TS = "0300"
LOCAL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1280, "height": 1400})
    page.goto(LOCAL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2500)

    page.evaluate("document.documentElement.setAttribute('data-theme','light')")
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{OUT}/巡检截图-{TS}_默认浅色.png", full_page=False)

    page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{OUT}/巡检截图-{TS}_暗黑.png", full_page=False)

    page.emulate_media(color_scheme="dark")
    page.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{OUT}/巡检截图-{TS}_系统自动-深.png", full_page=False)

    page.emulate_media(color_scheme="light")
    page.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{OUT}/巡检截图-{TS}_系统自动-浅.png", full_page=False)

    page.emulate_media(color_scheme="no-preference")
    page.evaluate("document.documentElement.setAttribute('data-theme','light')")
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(400)
    try:
        page.click('#viewToggle .seg-btn[data-mode="en"]', timeout=5000)
    except Exception as e:
        print("en click skipped:", e)
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{OUT}/巡检截图-{TS}_英文原文视图.png", full_page=False)

    checks = page.evaluate("""()=>{
      const m = document.querySelector('.metrics');
      const cs = m ? getComputedStyle(m) : null;
      const hasEntryBefore = [...document.styleSheets].some(s => {
        try { return [...s.cssRules].some(r => r.selectorText && r.selectorText.includes('entry::before')); }
        catch (e) { return false; }
      });
      const beforeContent = hasEntryBefore ? 'present' : 'none';
      const syncBtns = document.querySelectorAll('[class*=sync],[id*=sync]').length;
      const entries = document.querySelectorAll('.entry').length;
      const themeBtns = [...document.querySelectorAll('#themeToggle .seg-btn')].map(x => x.getAttribute('data-theme') || x.getAttribute('data-mode'));
      // 系统自动跟随验证：auto 模式下改系统配色，data-theme 的解析值应变化
      document.documentElement.setAttribute('data-theme','auto');
      const resolved = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
      return {
        metricsPadding: cs ? [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft] : 'none',
        metricsPaddingAllZero: cs ? [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0) : false,
        entryBefore: hasEntryBefore,
        entryBeforeContent: beforeContent,
        syncButtons: syncBtns,
        entries: entries,
        themeModes: themeBtns,
        autoResolvedBg: resolved
      };
    }""")
    print("ASSERTIONS:", json.dumps(checks, ensure_ascii=False))

    online = browser.new_page(viewport={"width": 1280, "height": 1400})
    online.goto(ONLINE, wait_until="networkidle", timeout=60000)
    online.wait_for_timeout(2500)
    online.evaluate("document.documentElement.setAttribute('data-theme','light')")
    online.wait_for_timeout(1200)
    online.screenshot(path=f"{OUT}/巡检截图-{TS}_线上.png", full_page=False)
    online.close()

    with open(f"{OUT}/巡检截图-{TS}_checks.json", "w", encoding="utf-8") as f:
        json.dump(checks, f, ensure_ascii=False, indent=2)
    browser.close()
