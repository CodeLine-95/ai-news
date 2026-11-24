"""13:00 巡检截图：默认(浅色)/暗黑/系统自动三主题 + 中英 + 线上，并实测 CSS 约束。"""
import asyncio
import json
from playwright.async_api import async_playwright

LOCAL = "http://127.0.0.1:8080/"
ONLINE = "https://a7888a7e046ffc95b.app.workbuddy.host/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"
SHOTS = [
    ("patrol_1300_local_light.png", LOCAL, "light", "zh", None),
    ("patrol_1300_local_dark.png", LOCAL, "dark", "zh", None),
    ("patrol_1300_local_auto_light.png", LOCAL, "auto", "zh", "light"),
    ("patrol_1300_local_auto_dark.png", LOCAL, "auto", "zh", "dark"),
    ("patrol_1300_local_en.png", LOCAL, "light", "en", None),
    ("patrol_1300_online.png", ONLINE, "light", "zh", None),
]


async def check_styles(page):
    return await page.evaluate("""() => {
        const res = {};
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
                if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
            }
        }
        res.entry_before_rules = beforeCount;
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft];
            res.metrics_padding_all_zero = res.metrics_padding.every(v => parseFloat(v) === 0);
        } else { res.metrics_padding_all_zero = 'NO .metrics'; }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|刷新|refresh/i.test(b.textContent || '')).map(b => (b.textContent||'').trim());
        res.entries = document.querySelectorAll('.entry').length;
        res.theme = document.documentElement.getAttribute('data-theme');
        return res;
    }""")


async def main():
    result = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        for fname, url, theme, view, prefers in SHOTS:
            ctx = await browser.new_context(viewport={"width": 1400, "height": 950})
            page = await ctx.new_page()
            if prefers:
                await page.emulate_media(color_scheme=prefers)
            await page.add_init_script(
                f"localStorage.setItem('themeMode','{theme}');"
                f"localStorage.setItem('viewMode','{view}');"
            )
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_function(
                    "() => { const e=document.getElementById('statTotal');"
                    " return e && e.textContent.trim()!=='0' && e.textContent.trim()!==''; }",
                    timeout=20000)
            except Exception as e:
                print("warn:", fname, repr(e))
            await page.wait_for_timeout(2200)
            try:
                total = await page.eval_on_selector("#statTotal", "el=>el.textContent.trim()")
            except Exception:
                total = "?"
            st = await check_styles(page)
            await page.screenshot(path=f"{OUT}/{fname}", full_page=False)
            result[fname] = {"total": total, "theme": st.get("theme"), "entry_before": st.get("entry_before_rules"),
                             "metrics_padding_zero": st.get("metrics_padding_all_zero"), "sync_btns": len(st.get("sync_buttons", []))}
            print(f"{fname}: total={total} theme={st.get('theme')} before={st.get('entry_before_rules')} metrics0={st.get('metrics_padding_all_zero')} sync={len(st.get('sync_buttons', []))}")
            await ctx.close()
        await browser.close()
    with open(f"{OUT}/patrol_1300_style_check.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("DONE")


asyncio.run(main())
