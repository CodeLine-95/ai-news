from playwright.sync_api import sync_playwright
import os
os.makedirs('/workspace/ai-news/screenshots', exist_ok=True)
base="http://127.0.0.1:8080/?sharecode=YM64NRHD37"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    # light (default)
    pg=b.new_page(viewport={"width":1280,"height":1400})
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_timeout(2500)
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.wait_for_timeout(500)
    pg.screenshot(path="/workspace/ai-news/screenshots/shot_light.png", full_page=False)
    # dark
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(500)
    pg.screenshot(path="/workspace/ai-news/screenshots/shot_dark.png", full_page=False)
    # english source view
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    try:
        pg.click('#viewToggle .seg-btn[data-view="en"]', timeout=3000)
    except Exception as e:
        print("en click skipped:", e)
    pg.wait_for_timeout(800)
    pg.screenshot(path="/workspace/ai-news/screenshots/shot_en.png", full_page=False)
    # metrics padding + entry::before assertions
    res=pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      const hasEntryBefore=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes('entry::before'))}catch(e){return false}});
      return {metricsPadding: cs?cs.padding:'none', entryBefore: hasEntryBefore, entries: document.querySelectorAll('.entry').length};
    }""")
    print("ASSERT:", res)
    b.close()
