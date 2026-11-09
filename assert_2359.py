from playwright.sync_api import sync_playwright
base="http://127.0.0.1:8080/?sharecode=YM64NRHD37"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":1000})
    pg.goto(base,wait_until="domcontentloaded"); pg.wait_for_timeout(2500)
    res=pg.evaluate("""()=>{
      const m=document.querySelector('.metrics');
      const cs=m?getComputedStyle(m):null;
      const hasEntryBefore=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes('entry::before'))}catch(e){return false}});
      const syncBtns=document.querySelectorAll('[class*=sync],[id*=sync]').length;
      const entries=document.querySelectorAll('.entry').length;
      const themeBtns=[...document.querySelectorAll('#themeToggle .seg-btn')].map(x=>x.getAttribute('data-mode'));
      const viewBtns=[...document.querySelectorAll('#viewToggle .seg-btn')].map(x=>x.getAttribute('data-mode'));
      return {metricsPadding:cs?cs.padding:'none',entryBefore:hasEntryBefore,syncButtons:syncBtns,entries:entries,themeModes:themeBtns,viewModes:viewBtns,title:document.title}
    }""")
    print("ASSERTIONS:",__import__('json').dumps(res,ensure_ascii=False))
    b.close()
