from playwright.sync_api import sync_playwright
import os, json
os.makedirs('/workspace/ai-news/screenshots', exist_ok=True)
base = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
out = "/workspace/ai-news/screenshots"
tag = "1120_1200"
results = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1360, "height": 1500})
    pg.goto(base, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(2500)

    # 1. 默认浅色
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.emulate_media(color_scheme="no-preference")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{out}/deliverable_{tag}_light.png", full_page=False)

    # 2. 暗黑模式
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{out}/deliverable_{tag}_dark.png", full_page=False)

    # 3. 系统自动 - 跟随系统深色
    pg.emulate_media(color_scheme="dark")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{out}/deliverable_{tag}_auto_dark.png", full_page=False)

    # 4. 系统自动 - 跟随系统浅色
    pg.emulate_media(color_scheme="light")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{out}/deliverable_{tag}_auto_light.png", full_page=False)

    # 5. 英文原文视图（浅色）
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.emulate_media(color_scheme="no-preference")
    try:
        pg.click('#viewToggle .seg-btn[data-mode="en"]', timeout=3000)
    except Exception as e:
        print("en click skipped:", e)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{out}/deliverable_{tag}_en.png", full_page=False)

    # 断言
    res = pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      const hasEntryBefore=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes('entry::before'))}catch(e){return false}});
      const syncBtns=document.querySelectorAll('[class*=sync],[id*=sync]').length;
      return {
        metricsPadding: cs?cs.padding:'none',
        entryBefore: hasEntryBefore,
        entries: document.querySelectorAll('.entry').length,
        syncBtns: syncBtns
      };
    }""")
    print("ASSERT:", json.dumps(res, ensure_ascii=False))
    b.close()
