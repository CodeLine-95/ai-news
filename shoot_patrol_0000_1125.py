from playwright.sync_api import sync_playwright
import os, json
os.makedirs('/workspace/ai-news/screenshots', exist_ok=True)
base = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
out = "/workspace/ai-news/screenshots"
ts = "0000"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--disable-software-rasterizer"])
    pg = b.new_page(viewport={"width": 1280, "height": 1400})
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_timeout(2500)

    # 默认模式（浅色）
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/patrol_0000_1125_light.png", full_page=False)

    # 暗黑模式
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/patrol_0000_1125_dark.png", full_page=False)

    # 系统自动：跟随系统深浅动态切换
    pg.emulate_media(color_scheme="dark")
    pg.evaluate("localStorage.setItem('themeMode','auto'); document.documentElement.setAttribute('data-theme','dark')")
    pg.wait_for_timeout(600)
    auto_dark_theme = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    pg.screenshot(path=f"{out}/patrol_0000_1125_auto_dark.png", full_page=False)

    pg.emulate_media(color_scheme="light")
    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.wait_for_timeout(600)
    auto_light_theme = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    pg.screenshot(path=f"{out}/patrol_0000_1125_auto_light.png", full_page=False)

    pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
    pg.emulate_media(color_scheme="no-preference")
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(400)
    try:
        pg.click('#viewToggle .seg-btn[data-mode="en"]', timeout=5000)
    except Exception as e:
        print("en click skipped:", e)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{out}/patrol_0000_1125_en.png", full_page=False)

    try:
        pg.click('#viewToggle .seg-btn[data-mode="zh"]', timeout=5000)
    except Exception as e:
        print("zh click skipped:", e)
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/patrol_0000_1125_full.png", full_page=True)

    res = pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      let entryBeforeRules=0;
      [...document.styleSheets].forEach(s=>{try{[...s.cssRules].forEach(r=>{if(r.selectorText&&r.selectorText.includes('entry::before'))entryBeforeRules++})}catch(e){}});
      const entryEl=document.querySelector('.entry');
      const entryBeforeContent=entryEl?getComputedStyle(entryEl,'::before').content:'(none)';
      const syncBtns=[...document.querySelectorAll('button,a')].filter(x=>/同步|sync|刷新|refresh/i.test(x.textContent)).length;
      const entries=document.querySelectorAll('.entry').length;
      const themeBtns=[...document.querySelectorAll('#themeToggle .seg-btn')].map(x=>x.getAttribute('data-theme'));
      return {
        metricsPadding: cs?[cs.paddingTop,cs.paddingRight,cs.paddingBottom,cs.paddingLeft]:null,
        entryBeforeRules, entryBeforeContent,
        syncButtons: syncBtns, entries, themeModes: themeBtns
      }
    }""")
    res['autoFollowDark'] = auto_dark_theme
    res['autoFollowLight'] = auto_light_theme
    print("ASSERTIONS:", json.dumps(res, ensure_ascii=False))
    b.close()
