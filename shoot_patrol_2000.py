from playwright.sync_api import sync_playwright
import os, json
os.makedirs('/workspace/ai-news/screenshots', exist_ok=True)
base = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
out = "/workspace/ai-news/screenshots"
ts = "2000"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 1400})
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_timeout(2500)

    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-{ts}-默认浅色.png", full_page=False)

    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-{ts}-暗黑.png", full_page=False)

    pg.emulate_media(color_scheme="dark")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-{ts}-系统自动-深.png", full_page=False)
    pg.emulate_media(color_scheme="light")
    pg.evaluate("document.documentElement.setAttribute('data-theme','auto')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-{ts}-系统自动-浅.png", full_page=False)

    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.emulate_media(color_scheme="no-preference")
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(400)
    try:
        pg.click('#viewToggle .seg-btn[data-mode="en"]', timeout=5000)
    except Exception as e:
        print("en click skipped:", e)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{out}/巡检-{ts}-英文原文视图.png", full_page=False)

    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    try:
        pg.click('#viewToggle .seg-btn[data-mode="zh"]', timeout=5000)
    except Exception as e:
        print("zh click skipped:", e)
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/巡检-{ts}-全页.png", full_page=True)

    res = pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      const hasEntryBefore=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes('entry::before'))}catch(e){return false}});
      const syncBtns=document.querySelectorAll('[class*=sync],[id*=sync]').length;
      const entries=document.querySelectorAll('.entry').length;
      const themeBtns=[...document.querySelectorAll('#themeToggle .seg-btn')].map(x=>x.getAttribute('data-mode'));
      return {
        metricsPadding: cs?cs.padding:'none',
        entryBefore: hasEntryBefore,
        syncButtons: syncBtns,
        entries: entries,
        themeModes: themeBtns
      }
    }""")
    print("ASSERTIONS:", json.dumps(res, ensure_ascii=False))
    b.close()
