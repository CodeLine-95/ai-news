import json
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"])
        pg=await b.new_page()
        await pg.goto("http://127.0.0.1:8080/",wait_until="networkidle")
        await pg.wait_for_timeout(1500)
        res=await pg.evaluate("""()=>{
          const entry=document.querySelector('.entry');
          const before=getComputedStyle(entry,'::before');
          const m=document.querySelector('.metrics');
          const mp=getComputedStyle(m).padding;
          const eb=getComputedStyle(document.querySelector('.entry'),'::before').content;
          const sync=[...document.querySelectorAll('button')].some(x=>/同步|sync/i.test(x.textContent||''));
          return {entryBeforeContent:eb, metricsPadding:mp, syncButton:sync,
                  entryCount:document.querySelectorAll('.entry').length};
        }""")
        print(json.dumps(res))
        await b.close()
asyncio.run(main())
