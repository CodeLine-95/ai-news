from playwright.sync_api import sync_playwright
import os, json
os.makedirs('/workspace/ai-news/screenshots', exist_ok=True)
base = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
out = "/workspace/ai-news/screenshots"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 1400})
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_timeout(2500)

    # default light (默认模式)
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-1100-默认浅色.png", full_page=False)

    # dark (暗黑模式)
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-1100-暗黑.png", full_page=False)

    # auto (系统自动) — 跟随系统：深
    pg.emulate_media(color_scheme="dark")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-1100-系统自动-深.png", full_page=False)
    pg.emulate_media(color_scheme="light")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-1100-系统自动-浅.png", full_page=False)

    # english source view (英文原文视图, 默认浅色)
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.emulate_media(color_scheme="no-preference")
    try:
        pg.click('#viewToggle .seg-btn[data-mode="en"]', timeout=3000)
    except Exception as e:
        print("en click skipped:", e)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{out}/巡检-1100-英文原文视图.png", full_page=False)

    # assertions: metrics padding 0, entry::before removed, no manual sync button
    res = pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      const hasEntryBefore=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes('entry::before'))}catch(e){return false}});
      const syncBtns=document.querySelectorAll('[class*=sync],[id*=sync],button:not([data-view]):not(.seg-btn)').length;
      return {
        metricsPadding: cs?cs.padding:'none',
        entryBefore: hasEntryBefore,
        entries: document.querySelectorAll('.entry').length,
        themeAttr: document.documentElement.getAttribute('data-theme')
      };
    }""")
    print("ASSERT:", json.dumps(res, ensure_ascii=False))
    b.close()
